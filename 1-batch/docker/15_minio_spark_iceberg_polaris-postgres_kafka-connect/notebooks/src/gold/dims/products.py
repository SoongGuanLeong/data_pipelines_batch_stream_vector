from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F, Window as W


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_dim_products_core(products: DataFrame) -> DataFrame:
    df = products.select(
        "product_id",
        "product_category_name",
        "product_category_name_english",
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "product_volume_cm3",
        "cdc_ts",
        "spark_ingest_ts",
    )
    return _apply_scd2_logic(df)


# =========================================================
# FULL build
# =========================================================
def build_dim_products_scd2(spark: SparkSession, products_table: str) -> DataFrame:

    products = spark.table(products_table)
    return _build_dim_products_core(products)


# =========================================================
# Incremental build (by changed keys)
# =========================================================
def build_incremental_dim_products(
    spark: SparkSession,
    products_table: str,
    changed_product_ids: DataFrame,
) -> DataFrame:

    products = spark.table(products_table).join(changed_product_ids, "product_id", "inner")

    return _build_dim_products_core(products)


# =========================================================
# Shared SCD2 logic
# =========================================================
def _apply_scd2_logic(df: DataFrame) -> DataFrame:

    w = W.partitionBy("product_id").orderBy(F.col("cdc_ts").asc(), F.col("spark_ingest_ts").asc())

    df = (
        df.withColumn("effective_from", F.col("cdc_ts"))
        .withColumn("effective_to", F.lead("cdc_ts").over(w))
        .withColumn("is_current", F.col("effective_to").isNull())
    )

    df = df.withColumn("product_sk", F.sha2(F.concat_ws("||", F.col("product_id"), F.col("effective_from")), 256))

    return df


# =========================================================
# Optional: validation helpers (good practice)
# ========================================================
def validate_scd2_products(df: DataFrame) -> None:

    dup = df.groupBy("product_id", "effective_from").count().filter("count > 1")
    if not dup.isEmpty():
        raise ValueError("Duplicate SCD2 keys detected")

    current = df.filter("is_current = true")
    dup_current = current.groupBy("product_id").count().filter("count > 1")
    if not dup_current.isEmpty():
        raise ValueError("Multiple current rows detected")

    invalid = df.filter((F.col("effective_to").isNotNull()) & (F.col("effective_from") >= F.col("effective_to")))
    if not invalid.isEmpty():
        raise ValueError("Invalid SCD2 intervals detected")
