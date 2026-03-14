from pyspark.sql import DataFrame, functions as F
from .utils import write_dq_metrics


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

    write_dq_metrics(df, metrics, table_name)

    return df
