from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F, Window as W


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
    return _apply_scd2_logic(df)


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
# Shared SCD2 logic
# =========================================================
def _apply_scd2_logic(df: DataFrame) -> DataFrame:
    """
    Apply SCD2 window logic.

    Assumptions:
    - cdc_ts is business event time
    - spark_ingest_ts is tie-breaker
    """

    w = W.partitionBy("customer_id").orderBy(F.col("cdc_ts"), F.col("spark_ingest_ts"))

    df = (
        df.withColumn("effective_from", F.col("cdc_ts"))
        .withColumn("effective_to", F.lead("cdc_ts").over(w))
        .withColumn("is_current", F.col("effective_to").isNull())
    )

    df = df.withColumn(
        "customer_sk",
        F.sha2(F.concat_ws("||", F.col("customer_id"), F.col("effective_from")), 256),
    )

    return df


# =========================================================
# Optional: validation helpers (good practice)
# =========================================================
def validate_scd2_customers(df: DataFrame) -> None:
    """
    Basic SCD2 sanity checks.
    Raises exception if invalid.
    """

    # 1. no duplicate (customer_id, effective_from)
    dup = df.groupBy("customer_id", "effective_from").count().filter("count > 1")

    if not dup.isEmpty():
        raise ValueError("Duplicate SCD2 keys detected")

    # 2. only one current row per customer
    current = df.filter("is_current = true")

    dup_current = current.groupBy("customer_id").count().filter("count > 1")

    if not dup_current.isEmpty():
        raise ValueError("Multiple current rows detected")

    # 3. effective_from < effective_to (if not null)
    invalid = df.filter((F.col("effective_to").isNotNull()) & (F.col("effective_from") >= F.col("effective_to")))

    if not invalid.isEmpty():
        raise ValueError("Invalid SCD2 intervals detected")
