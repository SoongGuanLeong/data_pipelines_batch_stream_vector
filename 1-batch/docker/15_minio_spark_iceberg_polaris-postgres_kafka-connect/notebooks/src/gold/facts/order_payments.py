from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F  # , Window as W
from src.gold.common import build_temporal_scd2_join_condition
from src.gold.dq import build_gold_fact_metrics


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
        build_temporal_scd2_join_condition(
            fact_key=F.col("o.customer_id"),
            dim_key=F.col("c.customer_id"),
            fact_event_ts=F.col("o.order_purchase_timestamp"),
            dim_effective_from=F.col("c.effective_from"),
            dim_effective_to=F.col("c.effective_to"),
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
def validate_fact_order_payments(df: DataFrame) -> list:
    return build_gold_fact_metrics(
        df,
        key_columns=["order_id", "payment_sequential"],
        required_columns=["customer_sk", "order_id", "order_purchase_date_sk"],
        non_negative_columns=["payment_value"],
    )
