from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F  # , Window as W
from src.gold.common import build_temporal_scd2_join_condition
from src.gold.dq import build_gold_fact_metrics, build_range_violation_metric


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_fact_order_reviews_core(
    order_reviews: DataFrame, orders: DataFrame, dim_customers: DataFrame, dim_date: DataFrame
) -> DataFrame:
    """
    Core logic to build fact_order_reviews DataFrame
    """
    r = order_reviews.alias("r")
    o = orders.alias("o")
    c = dim_customers.alias("c")
    dc = dim_date.alias("dc")  # review creation date
    da = dim_date.alias("da")  # review answer date

    fact = r.join(o, "order_id", "left")
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
    fact = fact.join(dc, F.to_date(F.col("r.review_creation_date")) == F.col("dc.ds"), "left")
    fact = fact.join(da, F.to_date(F.col("r.review_answer_timestamp")) == F.col("da.ds"), "left")

    fact = fact.select(
        F.col("r.review_id"),
        F.col("r.order_id"),
        F.col("r.review_score"),
        F.col("r.review_comment_title"),
        F.col("r.review_comment_message"),
        F.col("dc.date_sk").alias("review_creation_date_sk"),
        F.col("r.review_creation_date"),
        F.col("da.date_sk").alias("review_answer_date_sk"),
        F.col("r.review_answer_timestamp"),
        F.col("c.customer_sk"),
        F.col("o.customer_id"),
    )

    return fact


# =========================================================
# Full build
# =========================================================
def build_fact_order_reviews(
    spark: SparkSession,
    order_reviews_table: str,
    orders_table: str,
    customers_table: str,
    date_table: str,
) -> DataFrame:
    order_reviews = spark.table(order_reviews_table)
    orders = spark.table(orders_table)
    dim_customers = spark.table(customers_table)
    dim_date = spark.table(date_table)

    fact = _build_fact_order_reviews_core(order_reviews, orders, dim_customers, dim_date)
    return fact


# =========================================================
# Incremental build
# =========================================================
def build_fact_order_reviews_incremental(
    spark: SparkSession,
    order_reviews_table: str,
    orders_table: str,
    customers_table: str,
    date_table: str,
    changed_order_ids: DataFrame,
    changed_customer_ids: DataFrame,
) -> DataFrame:
    """
    dependencies:
        customer → orders → order_reviews
    """
    all_order_reviews = spark.table(order_reviews_table)
    all_orders = spark.table(orders_table)
    changed_order_ids = changed_order_ids.select("order_id").distinct()
    changed_customer_ids = changed_customer_ids.select("customer_id").distinct()

    impacted_orders_direct = changed_order_ids
    impacted_orders_from_customers = all_orders.join(changed_customer_ids, "customer_id", "inner").select("order_id")
    impacted_order_ids = impacted_orders_direct.unionByName(impacted_orders_from_customers).distinct()

    impacted_reviews_from_orders = all_order_reviews.join(impacted_order_ids, "order_id", "inner")
    order_reviews = impacted_reviews_from_orders

    orders = all_orders.join(order_reviews.select("order_id").distinct(), "order_id", "inner")

    impacted_customer_ids = orders.select("customer_id").unionByName(changed_customer_ids).distinct()
    dim_customers = spark.table(customers_table).join(impacted_customer_ids, "customer_id", "inner")

    dim_date = spark.table(date_table)

    fact = _build_fact_order_reviews_core(order_reviews, orders, dim_customers, dim_date)

    return fact


# =========================================================
# Validation
# =========================================================
def validate_fact_order_reviews(df: DataFrame) -> list:
    """
    Basic validation for fact_order_reviews
    """
    metrics = build_gold_fact_metrics(
        df,
        key_columns=["review_id"],
        required_columns=["customer_sk", "order_id", "review_creation_date_sk", "review_answer_date_sk"],
    )
    metrics.append(build_range_violation_metric("review_score", 1, 5))
    return metrics
