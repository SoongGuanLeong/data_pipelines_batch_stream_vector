from pyspark.sql import DataFrame, functions as F
from src.monitoring.dq_metrics import write_dq_metrics


def collect_product_category_name_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:
    metrics = []

    metrics.append(F.count("*").alias("total_rows"))

    metrics.append(F.sum(F.col("product_category_name").isNull().cast("int")).alias("null_product_category_name"))
    metrics.append(
        F.sum(F.col("product_category_name_english").isNull().cast("int")).alias("null_product_category_name_english")
    )

    metrics.append(
        F.sum((F.length(F.trim(F.col("product_category_name"))) == 0).cast("int")).alias("blank_product_category_name")
    )
    metrics.append(
        F.sum((F.length(F.trim(F.col("product_category_name_english"))) == 0).cast("int")).alias(
            "blank_product_category_name_english"
        )
    )

    metrics.append((F.count("*") - F.count_distinct("product_category_name")).alias("duplicate_category_key_count"))

    write_dq_metrics(df, metrics, table_name)
    return df
