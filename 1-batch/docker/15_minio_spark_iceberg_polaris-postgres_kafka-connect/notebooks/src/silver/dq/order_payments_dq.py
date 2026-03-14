from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def collect_order_payments_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    # order_id - not null, md5
    metrics.append(F.sum(F.col("order_id").isNull().cast("int")).alias("null_order_id"))
    metrics.append(F.sum(~F.col("order_id").rlike("^[a-fA-F0-9]{32}$").cast("int")).alias("invalid_order_id"))
    # payment_type - not N/A
    metrics.append(F.sum((F.col("payment_type") == "N/A").cast("int")).alias("invalid_payment_type"))
    # payment_value - >=0, not null
    metrics.append(F.sum((F.col("payment_value") < 0).cast("int")).alias("negative_payment_value"))
    metrics.append(F.sum(F.col("payment_value").isNull().cast("int")).alias("null_payment_value"))
    # payment_sequential, payment_installments - >= 1
    more_than_one_cols = ["payment_sequential", "payment_installments"]
    for c in more_than_one_cols:
        metrics.append(F.sum((F.col(c) < 1).cast("int")).alias(f"invalid_{c}"))
    # dupes count - PK + time
    metrics.append(
        (F.count("*") - F.count_distinct("order_id", "payment_sequential", "cdc_ts")).alias("duplicate_count")
    )

    metrics_df = df.agg(*metrics)

    metrics_df = (
        metrics_df.withColumn("pipeline_stage", F.lit("silver"))
        .withColumn("source_table", F.lit(table_name))
        .withColumn("timestamp", F.current_timestamp())
    )

    metrics_df.writeTo("monitoring.dq_metrics").append()
    return df
