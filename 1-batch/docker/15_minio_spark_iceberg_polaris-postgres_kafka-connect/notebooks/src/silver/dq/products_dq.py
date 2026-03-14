from pyspark.sql import DataFrame, functions as F
from .utils import write_dq_metrics


def collect_products_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    # product_id - not null, md5
    id_cols = ["product_id"]
    for c in id_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum(~F.col(c).rlike("^[a-fA-F0-9]{32}$").cast("int")).alias(f"invalid_{c}"))

    # product_category_name - N/A
    metrics.append(F.sum((F.col("product_category_name") == "N/A").cast("int")).alias("missing_product_category_name"))

    # product_name_length, product_description_length, product_photos_qty - >= 0
    can_zero_cols = [
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
    ]
    for c in can_zero_cols:
        metrics.append(F.sum((F.col(c) < 0).cast("int")).alias(f"negative_{c}"))

    # product_weight_g, product_length_cm, product_height_cm, product_width_cm, product_volume_cm3 - > 0
    cannot_zero_cols = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "product_volume_cm3",
    ]
    for c in cannot_zero_cols:
        metrics.append(F.sum((F.col(c) <= 0).cast("int")).alias(f"invalid_{c}"))

    # dupes count - PK + time
    metrics.append((F.count("*") - F.count_distinct("product_id", "cdc_ts")).alias("duplicate_count"))

    write_dq_metrics(df, metrics, table_name)

    return df
