from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)


def transform_products(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = ["product_id", "product_category_name"]
    for c in trim_cols:
        df = remove_control_characters(df, c)
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=["product_id"])
    df = df.fillna("N/A", subset=["product_category_name"])

    df = df.withColumn("product_category_name", F.lower(F.col("product_category_name")))

    # Numeric - not null (dropna/fillna), defensive casting, range check, precision
    can_zero_cols = [
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
    ]
    df = df.fillna(0, subset=can_zero_cols)
    for c in can_zero_cols:
        df = df.withColumn(c, F.col(c).cast("integer"))
        df = df.withColumn(c, F.when(F.col(c) < 0, 0).otherwise(F.col(c)))

    cannot_zero_cols = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for c in cannot_zero_cols:
        df = df.withColumn(c, F.when(F.col(c) > 0, F.col(c)).otherwise(F.lit(None)))

    df = df.withColumn(
        "product_volume_cm3",
        F.col("product_length_cm")
        * F.col("product_height_cm")
        * F.col("product_width_cm"),
    )

    # timestamp - convert, invalid date
    microsecond_cols = ["created_at", "updated_at"]
    tomorrow = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    for c in microsecond_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", tomorrow))

    # string special handling - accents (not needed here)
    return df
