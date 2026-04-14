from pyspark.sql import DataFrame, functions as F
from src.pipeline.batch.monitoring.dq_metrics import write_dq_metrics


def collect_geolocation_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    metrics.append(F.count("*").alias("total_rows"))

    metrics.append(
        F.sum(F.col("geolocation_zip_code_prefix").isNull().cast("int")).alias("null_geolocation_zip_code_prefix")
    )
    metrics.append(F.sum(F.col("geolocation_lat").isNull().cast("int")).alias("null_geolocation_lat"))
    metrics.append(F.sum(F.col("geolocation_lng").isNull().cast("int")).alias("null_geolocation_lng"))

    metrics.append(F.sum((~F.col("geolocation_lat").between(-90.0, 90.0)).cast("int")).alias("invalid_geolocation_lat"))
    metrics.append(
        F.sum((~F.col("geolocation_lng").between(-180.0, 180.0)).cast("int")).alias("invalid_geolocation_lng")
    )

    metrics.append(
        (
            F.count("*")
            - F.count_distinct(
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_city",
                "geolocation_state",
            )
        ).alias("duplicate_count")
    )

    write_dq_metrics(df, metrics, table_name)

    return df
