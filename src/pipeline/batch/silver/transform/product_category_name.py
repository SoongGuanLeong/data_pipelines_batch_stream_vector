from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.pipeline.batch.common.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)


def transform_product_category_name(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case forma
    trim_cols = ["product_category_name", "product_category_name_english"]
    for c in trim_cols:
        df = remove_control_characters(df, c)
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=["product_category_name"])
    df = df.dropDuplicates(["product_category_name"])

    df = df.withColumn("product_category_name", F.lower(F.col("product_category_name")))
    df = df.withColumn("product_category_name_english", F.initcap(F.col("product_category_name_english")))

    df = df.withColumn("ds", F.current_date())

    return df
