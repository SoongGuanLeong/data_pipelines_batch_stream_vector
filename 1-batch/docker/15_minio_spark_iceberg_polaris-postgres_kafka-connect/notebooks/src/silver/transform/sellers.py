from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.transform_utils import flatten_structs, normalize_column_names


def transform_sellers(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    microsecond_cols = ["created_at", "updated_at"]
    for c in microsecond_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))

    df = df.withColumn("seller_city", F.initcap(F.col("seller_city"))).withColumn(
        "seller_state", F.upper(F.col("seller_state"))
    )

    return df
