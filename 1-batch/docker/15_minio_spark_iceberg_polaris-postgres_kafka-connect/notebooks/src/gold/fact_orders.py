from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_fact_orders(spark, dim_customers: DataFrame, dim_dates: DataFrame) -> DataFrame:
    o = spark.table("polaris.silver.orders")

    df = (
        o.alias("o")
        .join(dim_customers.select("customer_id", "customer_sk").alias("dc"), "customer_id", "left")
        .join(
            dim_dates.select(F.col("ds").alias("purchase_ds"), F.col("date_sk").alias("order_purchase_date_sk")).alias(
                "dd"
            ),
            F.to_date(F.col("o.order_purchase_timestamp")) == F.col("dd.purchase_ds"),
            "left",
        )
        .select(
            "o.order_id",
            "dc.customer_sk",
            "o.customer_id",
            "o.order_status",
            "order_purchase_date_sk",
            "o.order_purchase_timestamp",
            "o.order_approved_at",
            "o.order_delivered_carrier_date",
            "o.order_delivered_customer_date",
            "o.order_estimated_delivery_date",
            "o.ds",
        )
    )
    return df
