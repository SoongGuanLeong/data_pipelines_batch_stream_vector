from collections.abc import Iterable
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_gold_fact_metrics(
    df: DataFrame,
    key_columns: list[str],
    required_columns: Iterable[str],
    non_negative_columns: Iterable[str] | None = None,
) -> list:
    """
    Build common Gold fact DQ metrics:
    - duplicate key count
    - null counts on required columns
    - negative value counts on configured measure columns
    """

    metrics = []

    metrics.append((F.count("*") - F.count_distinct(*key_columns)).alias("duplicate_keys"))

    for col_name in required_columns:
        metrics.append(F.sum(F.col(col_name).isNull().cast("int")).alias(f"null_{col_name}"))

    if non_negative_columns:
        for col_name in non_negative_columns:
            metrics.append(F.sum((F.col(col_name) < 0).cast("int")).alias(f"negative_{col_name}"))

    return metrics


def build_range_violation_metric(column_name: str, lower_bound: int, upper_bound: int) -> F.Column:
    """
    Count rows where a numeric column is outside [lower_bound, upper_bound].
    """
    return F.sum(((F.col(column_name) < lower_bound) | (F.col(column_name) > upper_bound)).cast("int")).alias(
        f"out_of_range_{column_name}"
    )
