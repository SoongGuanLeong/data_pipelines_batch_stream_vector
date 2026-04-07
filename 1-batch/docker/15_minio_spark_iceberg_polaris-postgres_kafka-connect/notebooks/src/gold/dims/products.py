from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F, Window as W


# =========================================================
# Core build logic (hidden helper)
# =========================================================
def _build_dim_products_core(products: DataFrame, translation: DataFrame) -> DataFrame:
    df = products.alias("p").join(
        translation.alias("t"), F.col("p.product_category_name") == F.col("t.product_category_name"), "left"
    )

    df = df.select(
        "p.product_id",
        "p.product_category_name",
        "t.product_category_name_english",
        "p.product_name_length",
        "p.product_description_length",
        "p.product_photos_qty",
        "p.product_weight_g",
        "p.product_length_cm",
        "p.product_height_cm",
        "p.product_width_cm",
        "p.product_volume_cm3",
        "p.cdc_ts",
        "p.spark_ingest_ts",
    )
    return _apply_scd2_logic(df)


# =========================================================
# FULL build
# =========================================================
def build_dim_products_scd2(spark: SparkSession, products_table: str, translation_table: str) -> DataFrame:

    products = spark.table(products_table)
    translation = spark.table(translation_table)
    return _build_dim_products_core(products, translation)


# =========================================================
# Incremental build (by changed keys)
# =========================================================
def build_incremental_dim_products(
    spark: SparkSession,
    products_table: str,
    translation_table: str,
    changed_product_ids: DataFrame,
) -> DataFrame:

    products = spark.table(products_table).join(changed_product_ids, "product_id", "inner")
    translation = spark.table(translation_table)

    return _build_dim_products_core(products, translation)


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
def validate_scd2_products(df: DataFrame) -> list:

    metrics = []

    metrics.append((F.count("*") - F.count_distinct("product_id", "effective_from")).alias("duplicate_keys"))

    metrics.append(
        (
            F.sum(F.when(F.col("is_current"), 1).otherwise(0))
            - F.count_distinct(F.when(F.col("is_current"), F.col("product_id")))
        ).alias("multiple_current_rows")
    )

    metrics.append(
        F.sum(
            ((F.col("effective_to").isNotNull()) & (F.col("effective_from") >= F.col("effective_to"))).cast("int")
        ).alias("invalid_intervals")
    )

    return metrics
