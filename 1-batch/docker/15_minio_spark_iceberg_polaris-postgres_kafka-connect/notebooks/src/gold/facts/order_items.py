from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F  # , Window as W


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_fact_order_items_core(
    order_items: DataFrame,
    orders: DataFrame,
    dim_customers: DataFrame,
    dim_sellers: DataFrame,
    dim_products: DataFrame,
    dim_date: DataFrame,
) -> DataFrame:
    """
    Core logic to build fact_order_items DataFrame
    """
    oi = order_items.alias("oi")
    o = orders.alias("o")
    c = dim_customers.alias("c")
    s = dim_sellers.alias("s")
    p = dim_products.alias("p")

    # -----------------------------------
    # Join to o, c, s, p, dim_date dp dd
    # -----------------------------------
    fact = oi.join(o, "order_id", "left")
    fact = fact.join(
        c,
        (
            (F.col("o.customer_id") == F.col("c.customer_id"))
            & (F.col("o.order_purchase_timestamp") >= F.col("c.effective_from"))
            & ((F.col("o.order_purchase_timestamp") < F.col("c.effective_to")) | F.col("c.effective_to").isNull())
        ),
        "left",
    )
    fact = fact.join(
        s,
        (
            (F.col("oi.seller_id") == F.col("s.seller_id"))
            & (F.col("o.order_purchase_timestamp") >= F.col("s.effective_from"))
            & ((F.col("o.order_purchase_timestamp") < F.col("s.effective_to")) | F.col("s.effective_to").isNull())
        ),
        "left",
    )
    fact = fact.join(
        p,
        (
            (F.col("oi.product_id") == F.col("p.product_id"))
            & (F.col("o.order_purchase_timestamp") >= F.col("p.effective_from"))
            & ((F.col("o.order_purchase_timestamp") < F.col("p.effective_to")) | F.col("p.effective_to").isNull())
        ),
        "left",
    )
    fact = fact.join(dim_date.alias("dp"), F.to_date(F.col("o.order_purchase_timestamp")) == F.col("dp.ds"), "left")

    fact = fact.join(
        dim_date.alias("dd"), F.to_date(F.col("o.order_delivered_customer_date")) == F.col("dd.ds"), "left"
    )

    fact = fact.select(
        F.col("oi.order_id"),
        F.col("oi.order_item_id"),
        F.col("c.customer_sk"),
        F.col("s.seller_sk"),
        F.col("p.product_sk"),
        F.col("o.customer_id"),
        F.col("oi.seller_id"),
        F.col("oi.product_id"),
        # -------------------------------
        # ITEM-LEVEL EVENT
        # -------------------------------
        F.col("oi.shipping_limit_date"),
        F.col("oi.price"),
        F.col("oi.freight_value"),
        # -------------------------------
        # ORDER SNAPSHOT
        # -------------------------------
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
def build_fact_order_items(
    spark: SparkSession,
    order_items_table: str,
    orders_table: str,
    customers_table: str,
    sellers_table: str,
    products_table: str,
    date_table: str,
) -> DataFrame:

    order_items = spark.table(order_items_table)
    orders = spark.table(orders_table)
    dim_customers = spark.table(customers_table)
    dim_sellers = spark.table(sellers_table)
    dim_products = spark.table(products_table)
    dim_date = spark.table(date_table)

    fact = _build_fact_order_items_core(order_items, orders, dim_customers, dim_sellers, dim_products, dim_date)
    return fact


# =========================================================
# Incremental build
# =========================================================
def build_fact_order_items_incremental(
    spark: SparkSession,
    order_items_table: str,
    orders_table: str,
    customers_table: str,
    sellers_table: str,
    products_table: str,
    date_table: str,
    changed_order_ids: DataFrame,
    changed_customer_ids: DataFrame,
    changed_seller_ids: DataFrame,
    changed_product_ids: DataFrame,
) -> DataFrame:
    """
    dependency graph:
    - fact_order_items:
        customer → orders → order_items
        product  → order_items
        seller   → order_items

    1. impacted_orders
    2. impacted_order_items
    3. filter orders
    4. filter dimensions
    5. rebuild
    """

    all_order_items = spark.table(order_items_table)
    all_orders = spark.table(orders_table)

    impacted_orders_direct = changed_order_ids.select("order_id")
    impacted_orders_from_customers = all_orders.join(changed_customer_ids, "customer_id", "inner").select("order_id")
    impacted_order_ids = impacted_orders_direct.unionByName(impacted_orders_from_customers).distinct()

    impacted_items_from_orders = all_order_items.join(impacted_order_ids, "order_id", "inner")
    impacted_items_from_products = all_order_items.join(changed_product_ids, "product_id", "inner")
    impacted_items_from_sellers = all_order_items.join(changed_seller_ids, "seller_id", "inner")

    order_items = (
        impacted_items_from_orders.unionByName(impacted_items_from_products)
        .unionByName(impacted_items_from_sellers)
        .dropDuplicates(["order_id", "order_item_id"])
    )
    orders = all_orders.join(order_items.select("order_id").distinct(), "order_id", "inner")

    impacted_customer_ids = (
        orders.select("customer_id").unionByName(changed_customer_ids.select("customer_id")).distinct()
    )
    dim_customers = spark.table(customers_table).join(impacted_customer_ids, "customer_id", "inner")

    impacted_product_ids = (
        order_items.select("product_id").unionByName(changed_product_ids.select("product_id")).distinct()
    )
    dim_products = spark.table(products_table).join(impacted_product_ids, "product_id", "inner")

    impacted_seller_ids = order_items.select("seller_id").unionByName(changed_seller_ids.select("seller_id")).distinct()
    dim_sellers = spark.table(sellers_table).join(impacted_seller_ids, "seller_id", "inner")

    dim_date = spark.table(date_table)

    fact = _build_fact_order_items_core(order_items, orders, dim_customers, dim_sellers, dim_products, dim_date)

    return fact


# =========================================================
# Validation
# =========================================================
def validate_fact_order_items(df: DataFrame) -> list:
    """
    Basic validation for fact_order_items
    """
    metrics = []

    metrics.append((F.count("*") - F.count_distinct("order_id", "order_item_id")).alias("duplicate_keys"))

    non_null_columns = ["customer_sk", "product_sk", "seller_sk", "order_purchase_date_sk"]
    for c in non_null_columns:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))

    return metrics
