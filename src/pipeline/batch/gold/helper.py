from pyspark.sql import DataFrame, SparkSession
from src.pipeline.batch.common.watermark import get_changed_keys


def get_changed_order_ids(spark: SparkSession, effective_ts) -> DataFrame:
    return get_changed_keys(
        spark,
        source_table="polaris.silver.orders",
        key_column="order_id",
        effective_ts=effective_ts,
    )


def get_changed_customer_ids(spark: SparkSession, effective_ts) -> DataFrame:
    return get_changed_keys(
        spark,
        source_table="polaris.silver.customers",
        key_column="customer_id",
        effective_ts=effective_ts,
    )


def get_changed_product_ids(spark: SparkSession, effective_ts) -> DataFrame:
    return get_changed_keys(
        spark,
        source_table="polaris.silver.products",
        key_column="product_id",
        effective_ts=effective_ts,
    )


def get_changed_seller_ids(spark: SparkSession, effective_ts) -> DataFrame:
    return get_changed_keys(
        spark,
        source_table="polaris.silver.sellers",
        key_column="seller_id",
        effective_ts=effective_ts,
    )
