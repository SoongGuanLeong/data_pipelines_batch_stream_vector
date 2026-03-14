from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def collect_sellers_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    # order_id, product_id, seller_id - not null, md5
    id_cols = ["order_id", "product_id", "seller_id"]
    for c in id_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum(~F.col(c).rlike("^[a-fA-F0-9]{32}$").cast("int")).alias(f"invalid_{c}"))

    # order_item_id - not null, > 0
    metrics.append(F.sum(F.col("order_item_id").isNull().cast("int")).alias("null_order_item_id"))
    metrics.append(F.sum((F.col("order_item_id") <= 0).cast("int")).alias("negative_order_item_id"))

    # shipping_limit_date - not null, limits (between 2000-01-01 and current_timestamp + 3 months)
    sld = "shipping_limit_date"
    metrics.append(F.sum(F.col(sld).isNull().cast("int")).alias(f"null_{sld}"))
    metrics.append(F.sum((F.col(sld) < F.lit("2000-01-01").cast("timestamp")).cast("int")).alias(f"old_{sld}"))
    metrics.append(F.sum((F.col(sld) > F.current_timestamp()).cast("int")).alias(f"future_{sld}"))

    # price > 0, freight_value >= 0
    metrics.append(F.sum((F.col("price") <= 0).cast("int")).alias("invalid_price"))
    metrics.append(F.sum((F.col("freight_value") < 0).cast("int")).alias("negative_freight_value"))

    # dupes count - PK + time
    metrics.append((F.count("*") - F.count_distinct("order_id", "order_item_id", "cdc_ts")).alias("duplicate_count"))

    metrics_df = df.agg(*metrics)

    metrics_df = (
        metrics_df.withColumn("pipeline_stage", F.lit("silver"))
        .withColumn("source_table", F.lit(table_name))
        .withColumn("timestamp", F.current_timestamp())
    )

    metrics_df.writeTo("monitoring.dq_metrics").append()
    return df
