from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def collect_customers_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    # customer_id, customer_unique_id - not null, md5
    id_cols = ["customer_id", "customer_unique_id"]
    for c in id_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum(~F.col(c).rlike("^[a-fA-F0-9]{32}$").cast("int")).alias(f"invalid_{c}"))
    # customer_zip_code_prefix - regex
    metrics.append(
        F.sum(~F.col("customer_zip_code_prefix").rlike("^[0-9]{5}$").cast("int")).alias("invalid_customer_zip_code")
    )
    # dupes count - PK + time
    metrics.append((F.count("*") - F.count_distinct("customer_id", "cdc_ts")).alias("duplicate_count"))

    metrics_df = df.agg(*metrics)

    metrics_df = (
        metrics_df.withColumn("pipeline_stage", F.lit("silver"))
        .withColumn("source_table", F.lit(table_name))
        .withColumn("timestamp", F.current_timestamp())
    )

    metrics_df.writeTo("monitoring.dq_metrics").append()

    return df
