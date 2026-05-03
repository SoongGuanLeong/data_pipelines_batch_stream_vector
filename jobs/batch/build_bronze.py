"""Bronze stage runner.

This script turns notebooks 20/21/22 into a runnable CLI entrypoint.

Modes:
- ddl: create CDC bronze + DLQ + audit tables from Apicurio schemas
- ingest: read Kafka CDC topics and append into bronze/DLQ/audit tables
- lookup: create and ingest static lookup tables (geolocation, product category)
- all: run ddl -> ingest -> lookup
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.avro.functions import from_avro

from src.pipeline.batch.common.avro_utils import fetch_avro_schema
from src.pipeline.batch.common.config_loader import load_config
from src.pipeline.batch.common.file_utils import checksum
from src.pipeline.batch.common.metadata_utils import (
    already_ingested,
    ddl_metadata_table,
    log_ingestion_metadata,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Bronze stage jobs")
    parser.add_argument(
        "--mode",
        choices=["all", "ddl", "ingest", "lookup"],
        default="all",
        help="Bronze operation mode",
    )
    parser.add_argument(
        "--config-dir",
        default="configs/batch",
        help="Folder containing *.yaml config files",
    )
    parser.add_argument(
        "--starting-offsets",
        default="earliest",
        choices=["earliest", "latest"],
        help="Kafka startingOffsets for ingest mode",
    )
    parser.add_argument(
        "--checkpoint-suffix",
        default="all_topics",
        help="Suffix appended under checkpoint base path",
    )
    return parser.parse_args()


def build_spark(app_name: str) -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def create_bronze_table(
    spark: SparkSession,
    topic: str,
    catalog: str,
    bronze_namespace: str,
    apicurio_url: str,
    topic_prefix: str,
) -> None:
    table_name = f"{catalog}.{bronze_namespace}.{topic}"
    if spark.catalog.tableExists(table_name):
        print(f"Table {table_name} exists. Skipping.")
        return

    schema_dict = fetch_avro_schema(topic, apicurio_url, topic_prefix)
    schema_json = json.dumps(schema_dict)

    df_schema = (
        spark.createDataFrame([], "value BINARY")
        .withColumn("avro_bytes", F.lit(None).cast("binary"))
        .select(from_avro("avro_bytes", schema_json).alias("data"))
        .select("data.*")
    )

    df_final = (
        df_schema.withColumn("kafka_offset", F.lit(None).cast("long"))
        .withColumn("kafka_partition", F.lit(None).cast("int"))
        .withColumn("kafka_ingest_ts", F.lit(None).cast("timestamp"))
        .withColumn("batch_id", F.lit(None).cast("string"))
        .withColumn("spark_ingest_ts", F.lit(None).cast("timestamp"))
    )

    (
        df_final.writeTo(table_name)
        .tableProperty("format-version", "3")
        .tableProperty("write.format.default", "parquet")
        .tableProperty("write.parquet.compression-codec", "zstd")
        .tableProperty("write.target-file-size-bytes", "134217728")
        .partitionedBy(F.partitioning.days("spark_ingest_ts"))
        .create()
    )
    print(f"Created {table_name}")


def create_dlq_table(spark: SparkSession, topic: str, catalog: str, bronze_namespace: str) -> None:
    table_name = f"{catalog}.{bronze_namespace}.{topic}_dlq"
    if spark.catalog.tableExists(table_name):
        print(f"Table {table_name} exists. Skipping.")
        return

    df = (
        spark.createDataFrame([], "raw_value BINARY")
        .withColumn("kafka_offset", F.lit(None).cast("long"))
        .withColumn("kafka_partition", F.lit(None).cast("int"))
        .withColumn("kafka_ingest_ts", F.lit(None).cast("timestamp"))
        .withColumn("spark_ingest_ts", F.lit(None).cast("timestamp"))
        .withColumn("batch_id", F.lit(None).cast("string"))
    )

    (
        df.writeTo(table_name)
        .tableProperty("format-version", "3")
        .tableProperty("write.format.default", "parquet")
        .tableProperty("write.parquet.compression-codec", "zstd")
        .partitionedBy(F.partitioning.days("spark_ingest_ts"))
        .create()
    )
    print(f"Created {table_name}")


def create_audit_table(spark: SparkSession, topic: str, catalog: str, bronze_namespace: str) -> None:
    table_name = f"{catalog}.{bronze_namespace}.{topic}_audit"
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            kafka_partition INT,
            topic STRING,
            batch_id STRING,
            batch_ts TIMESTAMP,
            min_offset BIGINT,
            max_offset BIGINT,
            row_count BIGINT
        ) USING ICEBERG
        PARTITIONED BY (F.partitioning.days(batch_ts))
        """
    )


def run_cdc_ddl(spark: SparkSession, cfg: dict) -> None:
    catalog = cfg["general"]["catalog"]
    bronze_namespace = cfg["general"]["namespaces"]["bronze"]
    apicurio_url = cfg["api"]["apicurio_url"]
    topic_prefix = cfg["kafka"]["topic_prefix"]
    topics = cfg["kafka"]["topic_suffix"]

    for topic in topics:
        create_bronze_table(spark, topic, catalog, bronze_namespace, apicurio_url, topic_prefix)
        create_dlq_table(spark, topic, catalog, bronze_namespace)
        create_audit_table(spark, topic, catalog, bronze_namespace)
