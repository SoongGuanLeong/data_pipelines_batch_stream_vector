from pyspark.sql import DataFrame, functions as F


def collect_common_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:
    metrics_df = df.agg(
        F.count("*").alias("total_rows"),
        # cdc_op - enum
        F.sum((~F.col("cdc_op").isin(["c", "u", "d"])).cast("int")).alias("bad_cdc_op"),
        # cdc_ts - not null, limits
        F.sum(F.col("cdc_ts").isNull().cast("int")).alias("null_cdc_ts"),
        F.sum(
            (F.col("cdc_ts") < F.lit("2000-01-01 00:00:00").cast("timestamp")).cast(
                "int"
            )
        ).alias("old_cdc_ts"),
        F.sum((F.col("cdc_ts") > F.current_timestamp()).cast("int")).alias(
            "future_cdc_ts"
        ),
        # ds - not null
        F.sum(F.col("ds").isNull().cast("int")).alias("null_ds"),
        # spark_ingest_ts - not null
        F.sum(F.col("spark_ingest_ts").isNull().cast("int")).alias(
            "null_spark_ingest_ts"
        ),
        # batch_id - not null
        F.sum(F.col("batch_id").isNull().cast("int")).alias("null_batch_id"),
        # created_at - not null
        F.sum(F.col("created_at").isNull().cast("int")).alias("null_created_at"),
        # updated_at - not null
        F.sum(F.col("updated_at").isNull().cast("int")).alias("null_updated_at"),
    )

    metrics_df = (
        metrics_df.withColumn("pipeline_stage", F.lit("silver"))
        .withColumn("source_table", F.lit(table_name))
        .withColumn("timestamp", F.current_timestamp())
    )

    metrics_df.writeTo("monitoring.dq_metrics").append()

    return df
