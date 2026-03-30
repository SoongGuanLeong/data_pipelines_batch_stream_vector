from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
# from pyspark.sql import Window as W


def build_dim_date(spark: SparkSession, start_date: str, end_date: str) -> DataFrame:

    df = spark.sql(f"""
            SELECT explode(
                sequence(
                    to_date('{start_date}'),
                    to_date('{end_date}'),
                    interval 1 day
                )
            ) AS ds
        """)

    df = (
        df.withColumn("date_sk", F.date_format("ds", "yyyyMMdd").cast("int"))
        .withColumn("year", F.year("ds"))
        .withColumn("quarter", F.quarter("ds"))
        .withColumn("month", F.month("ds"))
        .withColumn("day", F.dayofmonth("ds"))
        .withColumn("day_of_week", F.dayofweek("ds"))
        .withColumn("day_name", F.date_format("ds", "EEEE"))
        .withColumn("week_of_year", F.weekofyear("ds"))
        .withColumn(
            "is_weekend",
            F.col("day_of_week").isin([1, 7]),  # Sun=1, Sat=7
        )
    )

    return df
