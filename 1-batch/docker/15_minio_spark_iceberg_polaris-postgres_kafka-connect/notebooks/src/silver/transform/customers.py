from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.transform_utils import flatten_structs, normalize_column_names


def transform_customers(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    microsecond_cols = ["created_at", "updated_at"]
    for c in microsecond_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))

    df = df.withColumn("customer_city", F.initcap(F.col("customer_city"))).withColumn(
        "customer_state", F.upper(F.col("customer_state"))
    )

    return df
