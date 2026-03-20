from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_dim_dates(spark, start_date: str, end_date: str) -> DataFrame:
    df = spark.sql(f"""
        SELECT explode(sequence(
            to_date('{start_date}'),
            to_date('{end_date}'),
            interval 1 day
        )) AS ds
    """)

    df = (
        df.withColumn("date_sk", F.date_format("ds", "yyyyMMdd").cast("int"))
        .withColumn("year", F.year("ds"))
        .withColumn("quarter", F.quarter("ds"))
        .withColumn("month", F.month("ds"))
        .withColumn("day", F.dayofmonth("ds"))
        .withColumn("weekday", F.dayofweek("ds"))
        .withColumn("is_weekend", F.when(F.dayofweek("ds").isin([1, 7]), 1).otherwise(0))
        .withColumn("is_holiday", F.lit(0))  # placeholder
    )

    return df
