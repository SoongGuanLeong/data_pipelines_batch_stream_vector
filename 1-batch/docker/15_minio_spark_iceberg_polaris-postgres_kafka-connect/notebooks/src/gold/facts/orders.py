from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

# from pyspark.sql import Window as W
from src.watermark import get_changed_keys


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_fact_orders_core(orders: DataFrame, dim_customers: DataFrame, dim_date: DataFrame) -> DataFrame:
    """
    Core logic to build fact_orders DataFrame
    """

    # -----------------------------
    # SCD2 temporal join with customers
    # -----------------------------
    fact = orders.alias("o").join(
        dim_customers.alias("c"),
        (
            (F.col("o.customer_id") == F.col("c.customer_id"))
            & (F.col("o.order_purchase_timestamp") >= F.col("c.effective_from"))
            & ((F.col("o.order_purchase_timestamp") < F.col("c.effective_to")) | F.col("c.effective_to").isNull())
        ),
        "left",
    )

    # -----------------------------
    # Join to dim_date (purchase)
    # -----------------------------
    fact = fact.join(dim_date.alias("dp"), F.to_date("o.order_purchase_timestamp") == F.col("dp.ds"), "left")

    # -----------------------------
    # Join to dim_date (delivered)
    # -----------------------------
    fact = fact.join(dim_date.alias("dd"), F.to_date("o.order_delivered_customer_date") == F.col("dd.ds"), "left")

    fact = fact.select(
        F.col("o.order_id"),
        F.col("c.customer_sk"),
        F.col("o.customer_id"),
        F.col("o.order_status"),
        F.col("dp.date_sk").alias("order_purchase_date_sk"),
        F.col("o.order_purchase_timestamp"),
        F.col("o.order_approved_at"),
        F.col("o.order_delivered_carrier_date"),
        F.col("dd.date_sk").alias("order_delivered_customer_date_sk"),
        F.col("o.order_delivered_customer_date"),
        F.col("o.order_estimated_delivery_date"),
    )

    return fact


# =========================================================
# Full build
# =========================================================
def build_fact_orders(spark: SparkSession, orders_table: str, customers_table: str, date_table: str) -> DataFrame:
    orders = spark.table(orders_table)
    dim_customers = spark.table(customers_table)
    dim_date = spark.table(date_table)

    fact = _build_fact_orders_core(orders, dim_customers, dim_date)
    return fact


# =========================================================
# Incremental build
# =========================================================
def build_fact_orders_incremental(
    spark: SparkSession,
    orders_table: str,
    customers_table: str,
    date_table: str,
    changed_customer_ids: DataFrame,
    changed_order_ids: DataFrame,
) -> DataFrame:

    orders = spark.table(orders_table).join(changed_order_ids, "order_id", "inner")
    # Include customers impacted by changed orders (not only changed customer records).
    # Without this, an updated order for an unchanged customer can produce null customer_sk.
    # impacted FKs = changed FKs + FKs of changed records (orders)
    impacted_customer_ids = (
        orders.select("customer_id").unionByName(changed_customer_ids.select("customer_id")).distinct()
    )
    dim_customers = spark.table(customers_table).join(impacted_customer_ids, "customer_id", "inner")

    dim_date = spark.table(date_table)

    fact = _build_fact_orders_core(orders, dim_customers, dim_date)
    return fact


# =========================================================
# Helper functions
# =========================================================
def get_changed_customer_ids(spark: SparkSession, effective_ts) -> DataFrame:
    return get_changed_keys(
        spark,
        source_table="polaris.silver.customers",
        key_column="customer_id",
        effective_ts=effective_ts,
    )


def get_changed_order_ids(spark: SparkSession, effective_ts) -> DataFrame:
    return get_changed_keys(
        spark,
        source_table="polaris.silver.orders",
        key_column="order_id",
        effective_ts=effective_ts,
    )


# =========================================================
# Validation
# =========================================================
def validate_fact_orders(df: DataFrame):
    """
    Basic validation for fact_orders
    """

    # Unique order_id
    dup = df.groupBy("order_id").count().filter(F.col("count") > 1)
    if dup.limit(1).count() > 0:
        raise ValueError("Duplicate order_id found in fact_orders")

    # Non-null foreign keys
    nulls = df.filter(F.col("customer_sk").isNull())
    if nulls.limit(1).count() > 0:
        raise ValueError("Null customer_sk found in fact_orders")

    # Valid date SKs
    for c in ["order_purchase_date_sk", "order_delivered_customer_date_sk"]:
        if df.filter(F.col(c).isNull()).limit(1).count() > 0:
            raise ValueError(f"Null {c} found in fact_orders")
