from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F, Window as W


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_dim_sellers_core(sellers: DataFrame, geolocation: DataFrame) -> DataFrame:
    """
    Core logic to build dim_sellers DataFrame
    """
    df = (
        sellers.alias("s")
        .join(
            geolocation.alias("g"),
            F.col("s.seller_zip_code_prefix") == F.col("g.geolocation_zip_code_prefix"),
            "left",
        )
        .select(
            F.col("s.seller_id"),
            F.col("s.seller_zip_code_prefix"),
            F.col("s.seller_city"),
            F.col("s.seller_state"),
            F.col("g.geolocation_lat"),
            F.col("g.geolocation_lng"),
            F.col("s.cdc_ts"),
            F.col("s.spark_ingest_ts"),
        )
    )
    return _apply_scd2_logic(df)


# =========================================================
# FULL build
# =========================================================
def build_dim_sellers_scd2(
    spark: SparkSession,
    sellers_table: str,
    geolocation_table: str,
) -> DataFrame:

    sellers = spark.table(sellers_table)
    geo = spark.table(geolocation_table)
    return _build_dim_sellers_core(sellers, geo)


# =========================================================
# Incremental build (by changed keys)
# =========================================================
def build_incremental_dim_sellers(
    spark: SparkSession,
    sellers_table: str,
    geolocation_table: str,
    changed_seller_ids: DataFrame,
) -> DataFrame:

    sellers = spark.table(sellers_table).join(changed_seller_ids, "seller_id", "inner")
    geo = spark.table(geolocation_table)
    return _build_dim_sellers_core(sellers, geo)


# =========================================================
# Shared SCD2 logic
# =========================================================
def _apply_scd2_logic(df: DataFrame) -> DataFrame:
    """
    Apply SCD2 window logic.

    Assumptions:
    - cdc_ts is business event time
    - spark_ingest_ts is tie-breaker
    """

    w = W.partitionBy("seller_id").orderBy(F.col("cdc_ts"), F.col("spark_ingest_ts"))

    df = (
        df.withColumn("effective_from", F.col("cdc_ts"))
        .withColumn("effective_to", F.lead("cdc_ts").over(w))
        .withColumn("is_current", F.col("effective_to").isNull())
    )

    df = df.withColumn(
        "seller_sk",
        F.sha2(F.concat_ws("||", F.col("seller_id"), F.col("effective_from")), 256),
    )

    return df


# =========================================================
# Optional: validation helpers (good practice)
# =========================================================
def validate_scd2_sellers(df: DataFrame) -> list:
    """
    Basic SCD2 sanity checks.
    Raises exception if invalid.
    Return metrics dict for monitoring.dq_metrics
    """
    metrics = []

    metrics.append((F.count("*") - F.count_distinct("seller_id", "effective_from")).alias("duplicate_keys"))

    metrics.append(
        (
            F.sum(F.when(F.col("is_current"), 1).otherwise(0))
            - F.count_distinct(F.when(F.col("is_current"), F.col("seller_id")))
        ).alias("multiple_current_rows")
    )

    metrics.append(
        F.sum(
            ((F.col("effective_to").isNotNull()) & (F.col("effective_from") >= F.col("effective_to"))).cast("int")
        ).alias("invalid_intervals")
    )

    return metrics
