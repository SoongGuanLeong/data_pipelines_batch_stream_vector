from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F  # Window as W
from src.pipeline.batch.gold.scd2 import apply_scd2


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_dim_customers_core(customers: DataFrame, geolocation: DataFrame) -> DataFrame:
    """
    Core logic to build dim_customers DataFrame
    """
    df = (
        customers.alias("c")
        .join(
            geolocation.alias("g"),
            F.col("c.customer_zip_code_prefix") == F.col("g.geolocation_zip_code_prefix"),
            "left",
        )
        .select(
            F.col("c.customer_id"),
            F.col("c.customer_unique_id"),
            F.col("c.customer_zip_code_prefix"),
            F.col("c.customer_city"),
            F.col("c.customer_state"),
            F.col("g.geolocation_lat"),
            F.col("g.geolocation_lng"),
            F.col("c.cdc_ts"),
            F.col("c.spark_ingest_ts"),
        )
    )
    return apply_scd2(df, business_key="customer_id", surrogate_key="customer_sk")


# =========================================================
# FULL build
# =========================================================
def build_dim_customers_scd2(
    spark: SparkSession,
    customers_table: str,
    geolocation_table: str,
) -> DataFrame:

    customers = spark.table(customers_table)
    geo = spark.table(geolocation_table)
    return _build_dim_customers_core(customers, geo)


# =========================================================
# Incremental build (by changed keys)
# =========================================================
def build_incremental_dim_customers(
    spark: SparkSession,
    customers_table: str,
    geolocation_table: str,
    changed_customer_ids: DataFrame,
) -> DataFrame:

    customers = spark.table(customers_table).join(changed_customer_ids, "customer_id", "inner")
    geo = spark.table(geolocation_table)
    return _build_dim_customers_core(customers, geo)


# =========================================================
# Optional: validation helpers (good practice)
# =========================================================
def validate_scd2_customers(df: DataFrame) -> list:
    metrics = []

    metrics.append((F.count("*") - F.count_distinct("customer_id", "effective_from")).alias("duplicate_keys"))
    metrics.append(
        (
            F.sum(F.when(F.col("is_current"), 1).otherwise(0))
            - F.count_distinct(F.when(F.col("is_current"), F.col("customer_id")))
        ).alias("multiple_current_rows")
    )
    metrics.append(
        F.sum(
            ((F.col("effective_to").isNotNull()) & (F.col("effective_from") >= F.col("effective_to"))).cast("int")
        ).alias("invalid_intervals")
    )

    return metrics
