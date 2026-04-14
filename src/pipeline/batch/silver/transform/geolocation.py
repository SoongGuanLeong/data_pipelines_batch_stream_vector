from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.pipeline.batch.common.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)


def transform_geolocation(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = [
        "geolocation_zip_code_prefix",
        "geolocation_city",
        "geolocation_state",
    ]
    for c in trim_cols:
        df = remove_control_characters(df, c)
        df = df.withColumn(c, F.trim(F.col(c)))

    # type safety
    df = df.withColumn("geolocation_lat", F.col("geolocation_lat").cast("double"))
    df = df.withColumn("geolocation_lng", F.col("geolocation_lng").cast("double"))
    df = df.withColumn("geolocation_zip_code_prefix", F.col("geolocation_zip_code_prefix").cast("string"))

    # basic validity
    df = df.filter(F.col("geolocation_lat").between(-90.0, 90.0))
    df = df.filter(F.col("geolocation_lng").between(-180.0, 180.0))
    df = df.dropna(subset=["geolocation_zip_code_prefix"])

    df = df.groupBy("geolocation_zip_code_prefix").agg(
        F.avg("geolocation_lat").alias("geolocation_lat"),
        F.avg("geolocation_lng").alias("geolocation_lng"),
        F.first("geolocation_city", ignorenulls=True).alias("geolocation_city"),
        F.first("geolocation_state", ignorenulls=True).alias("geolocation_state"),
    )

    df = df.withColumn("ds", F.current_date())
    return df
