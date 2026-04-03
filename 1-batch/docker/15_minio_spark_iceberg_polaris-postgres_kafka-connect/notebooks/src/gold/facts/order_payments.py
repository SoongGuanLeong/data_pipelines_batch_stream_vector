from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F  # , Window as W


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_fact_order_payments_core(
    order_payments: DataFrame, orders: DataFrame, dim_customers: DataFrame, dim_date: DataFrame
) -> DataFrame:
    """
    Core logic to build fact_order_payments DataFrame
    """
    op = order_payments.alias("op")
    o = orders.alias("o")
    c = dim_customers.alias("c")
    dp = dim_date.alias("dp")

    fact = op.join(o, "order_id", "left")
    fact = fact.join(
        c,
        (
            (F.col("o.customer_id") == F.col("c.customer_id"))
            & (F.col("o.order_purchase_timestamp") >= F.col("c.effective_from"))
            & ((F.col("o.order_purchase_timestamp") < F.col("c.effective_to")) | F.col("c.effective_to").isNull())
        ),
        "left",
    )
    fact = fact.join(dp, F.to_date(F.col("o.order_purchase_timestamp")) == F.col("dp.ds"), "left")

    fact = fact.select(
        F.col("op.order_id"),
        F.col("op.payment_sequential"),
        F.col("op.payment_type"),
        F.col("op.payment_installments"),
        F.col("op.payment_value"),
        F.col("c.customer_sk"),
        F.col("o.customer_id"),
        F.col("dp.date_sk").alias("order_purchase_date_sk"),
        F.col("o.order_purchase_timestamp"),
    )
    return fact


# =========================================================
# Full build
# =========================================================
def build_fact_order_payments(
    spark: SparkSession,
    order_payments_table: str,
    orders_table: str,
    customers_table: str,
    date_table: str,
) -> DataFrame:

    order_payments = spark.table(order_payments_table)
    orders = spark.table(orders_table)
    dim_customers = spark.table(customers_table)
    dim_date = spark.table(date_table)

    fact = _build_fact_order_payments_core(order_payments, orders, dim_customers, dim_date)
    return fact


# =========================================================
# Incremental build
# =========================================================
def build_fact_order_payments_incremental(
    spark: SparkSession,
    order_payments_table: str,
    orders_table: str,
    customers_table: str,
    date_table: str,
    changed_order_ids: DataFrame,
    changed_customer_ids: DataFrame,
) -> DataFrame:
    """
    dependencies:
        customer → orders → order_payments
    """
    all_order_payments = spark.table(order_payments_table)
    all_orders = spark.table(orders_table)
    changed_order_ids = changed_order_ids.select("order_id").distinct()
    changed_customer_ids = changed_customer_ids.select("customer_id").distinct()

    impacted_orders_direct = changed_order_ids
    impacted_orders_from_customers = all_orders.join(changed_customer_ids, "customer_id", "inner").select("order_id")
    impacted_order_ids = impacted_orders_direct.unionByName(impacted_orders_from_customers).distinct()

    impacted_payments_from_orders = all_order_payments.join(impacted_order_ids, "order_id", "inner")
    order_payments = impacted_payments_from_orders

    orders = all_orders.join(order_payments.select("order_id").distinct(), "order_id", "inner")

    impacted_customer_ids = orders.select("customer_id").unionByName(changed_customer_ids).distinct()
    dim_customers = spark.table(customers_table).join(impacted_customer_ids, "customer_id", "inner")

    dim_date = spark.table(date_table)

    fact = _build_fact_order_payments_core(order_payments, orders, dim_customers, dim_date)
    return fact


# =========================================================
# Validation
# =========================================================
def validate_fact_order_payments(df: DataFrame):
    """
    Basic validation for fact_order_payments
    """
    # Unique order_id + payment_sequential
    dup = df.groupBy("order_id", "payment_sequential").count().filter(F.col("count") > 1)
    if not dup.isEmpty():
        raise ValueError("Duplicate (order_id, payment_sequential) found in fact_order_payments")

    # Non-null foreign keys
    cols = ["customer_sk"]
    for c in cols:
        nulls = df.filter(F.col(c).isNull())
        if not nulls.isEmpty():
            raise ValueError(f"Null {c} found in fact_order_payments")

    # Non-null date SKs
    for c in ["order_purchase_date_sk"]:
        if not df.filter(F.col(c).isNull()).isEmpty():
            raise ValueError(f"Null {c} found in fact_order_payments")
