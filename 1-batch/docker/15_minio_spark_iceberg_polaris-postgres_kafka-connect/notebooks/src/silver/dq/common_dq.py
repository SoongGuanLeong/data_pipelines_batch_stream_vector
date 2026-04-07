from pyspark.sql import DataFrame, functions as F
from src.monitoring.dq_metrics import write_dq_metrics


def collect_common_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    metrics.append(F.count("*").alias("total_rows"))
    # cdc_op - enum
    metrics.append(F.sum((~F.col("cdc_op").isin(["c", "u", "d"])).cast("int")).alias("bad_cdc_op"))
    # cdc_ts, created_at, updated_at - not null, limits
    ts_cols = ["cdc_ts", "created_at", "updated_at"]
    for c in ts_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum((F.col(c) < F.lit("2000-01-01 00:00:00").cast("timestamp")).cast("int")).alias(f"old_{c}"))

    metrics.append(F.sum((F.col("cdc_ts") > F.current_timestamp()).cast("int")).alias("future_cdc_ts"))
    tomorrow = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    metrics.append(F.sum((F.col("created_at") > tomorrow).cast("int")).alias("future_created_at"))
    metrics.append(F.sum((F.col("updated_at") > tomorrow).cast("int")).alias("future_updated_at"))

    # ds, spark_ingest_ts, batch_id - not null
    not_null_cols = ["ds", "spark_ingest_ts", "batch_id"]
    for c in not_null_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))

    write_dq_metrics(df, metrics, table_name)

    return df
