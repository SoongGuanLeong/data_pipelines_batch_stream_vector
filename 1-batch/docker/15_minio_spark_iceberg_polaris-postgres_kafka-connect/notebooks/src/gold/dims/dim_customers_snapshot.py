from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window as W


def build_dim_customers_snapshot(spark, snapshot_date: str) -> DataFrame:
    """
    Snapshot table is optional and used for point-in-time queries.
    Primary source of truth is dim_customers_scd2.
    """

    c = spark.table("polaris.silver.customers")
    geo = spark.table("polaris.silver.geolocations")

    # get data upto a certain event date
    c_filtered = c.filter(F.col("cdc_ts") <= F.to_timestamp(F.lit(snapshot_date)))

    # dedup
    w = W.partitionBy("customer_id").orderBy(F.col("cdc_ts").desc(), F.col("spark_ingest_ts").desc())
    c_snapshot = c_filtered.withColumn("rn", F.row_number().over(w)).filter(F.col("rn") == 1).drop("rn")

    df = (
        c_snapshot.alias("c")
        .join(geo.alias("g"), F.col("c.customer_zip_code_prefix") == F.col("g.geolocation_zip_code_prefix"), "left")
        .select(
            F.col("c.customer_id"),
            F.col("c.customer_unique_id"),
            F.col("c.customer_zip_code_prefix"),
            F.col("c.customer_city"),
            F.col("c.customer_state"),
            F.col("g.geolocation_lat"),
            F.col("g.geolocation_lng"),
            F.col("c.cdc_ts").alias("record_updated_at"),
            F.col("c.ds"),
        )
        .withColumn("customer_sk", F.row_number().over(w.orderBy("customer_id")))
    )

    return df
