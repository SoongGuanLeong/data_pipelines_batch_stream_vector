from pathlib import Path
from datetime import datetime, timezone
from .file_utils import safe_file_type
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def ddl_metadata_table(spark: SparkSession, table_name: str):
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            file_name STRING,
            file_type STRING,
            path STRING,
            size_bytes BIGINT,
            upload_ts TIMESTAMP,
            checksum STRING
        )
        USING ICEBERG
        PARTITIONED BY (days(upload_ts))
    """)
    print(f"{table_name} created.")


def already_ingested(spark: SparkSession, table_name: str, checksum: str) -> bool:
    return spark.table(table_name).filter(F.col("checksum") == checksum).limit(1).count() > 0


def log_ingestion_metadata(
    spark: SparkSession,
    table_name: str,
    file_path: Path,
    spark_path: str,
    checksum: str,
    allowed_types: set[str],
):

    # ---- Idempotency Guard ----
    if already_ingested(spark, table_name, checksum):
        print(f"⚠️ Metadata already exists for checksum {checksum}. Skipping.")
        return

    file_size = file_path.stat().st_size
    upload_ts = datetime.now(timezone.utc)
    file_type = safe_file_type(file_path, allowed_types)

    metadata_df = spark.createDataFrame(
        [
            {
                "file_name": file_path.name,
                "file_type": file_type,
                "path": spark_path,
                "size_bytes": file_size,
                "upload_ts": upload_ts,
                "checksum": checksum,
            }
        ]
    )

    metadata_df.write.format("iceberg").mode("append").saveAsTable(table_name)

    print(f"{table_name} ingested")
