from pyspark.sql import DataFrame, functions as F
from src.pipeline.batch.monitoring.dq_metrics import write_dq_metrics


def collect_sellers_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = [
        # seller_id - not null, md5
        F.sum(F.col("seller_id").isNull().cast("int")).alias("null_seller_id"),
        F.sum((~F.col("seller_id").rlike("^[a-fA-F0-9]{32}$")).cast("int")).alias("invalid_seller_id"),
        # seller_zip_code_prefix - regex
        F.sum((~F.col("seller_zip_code_prefix").rlike("^[0-9]{5}$")).cast("int")).alias("invalid_seller_zip_code"),
        # dupes count - PK + time
        (F.count("*") - F.count_distinct("seller_id", "cdc_ts")).alias("duplicate_count"),
    ]

    write_dq_metrics(df, metrics, table_name)

    return df
