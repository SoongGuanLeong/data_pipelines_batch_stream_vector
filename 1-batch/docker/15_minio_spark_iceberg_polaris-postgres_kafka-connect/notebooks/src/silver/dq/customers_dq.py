from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def collect_customers_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics_df = df.agg(
        # customer_id - not null, md5
        F.sum(F.col("customer_id").isNull().cast("int")).alias("null_customer_id"),
        F.sum(~F.col("customer_id").rlike("^[a-fA-F0-9]{32}$").cast("int")).alias(
            "invalid_customer_id"
        ),
        # customer_unique_id - not null, md5
        F.sum(F.col("customer_unique_id").isNull().cast("int")).alias(
            "null_customer_unique_id"
        ),
        F.sum(
            ~F.col("customer_unique_id").rlike("^[a-fA-F0-9]{32}$").cast("int")
        ).alias("invalid_customer_unique_id"),
        # customer_zip_code_prefix - regex
        F.sum(~F.col("customer_zip_code_prefix").rlike("^[0-9]{5}$").cast("int")).alias(
            "invalid_customer_zip_code"
        ),
        # created_at - not null, limits
        F.sum(F.col("created_at").isNull().cast("int")).alias("null_created_at"),
        F.sum(
            (F.col("created_at") < F.lit("2000-01-01").cast("timestamp")).cast("int")
        ).alias("old_created_at"),
        F.sum((F.col("created_at") > F.current_timestamp()).cast("int")).alias(
            "future_created_at"
        ),
        # updated_at - not null, limits
        F.sum(F.col("updated_at").isNull().cast("int")).alias("null_updated_at"),
        F.sum(
            (F.col("updated_at") < F.lit("2000-01-01").cast("timestamp")).cast("int")
        ).alias("old_updated_at"),
        F.sum((F.col("updated_at") > F.current_timestamp()).cast("int")).alias(
            "future_updated_at"
        ),
        # dupes count - PK + time
        (F.count("*") - F.count_distinct("customer_id", "cdc_ts")).alias(
            "duplicate_count"
        ),
    )

    metrics_df = (
        metrics_df.withColumn("pipeline_stage", F.lit("silver"))
        .withColumn("source_table", F.lit(table_name))
        .withColumn("timestamp", F.current_timestamp())
    )

    metrics_df.writeTo("monitoring.dq_metrics").append()

    return df
