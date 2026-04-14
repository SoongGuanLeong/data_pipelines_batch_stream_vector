from pyspark.sql import DataFrame, functions as F
from src.pipeline.batch.monitoring.dq_metrics import write_dq_metrics


def collect_order_reviews_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    # review_id, order_id - not null, md5
    id_cols = ["review_id", "order_id"]
    for c in id_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum((~F.col(c).rlike("^[a-fA-F0-9]{32}$")).cast("int")).alias(f"invalid_{c}"))
    # review_score - not null, isin(1,5)
    metrics.append(F.sum(F.col("review_score").isNull().cast("int")).alias("null_review_score"))
    metrics.append(F.sum((~F.col("review_score").between(1, 5)).cast("int")).alias("invalid_review_score"))

    # review_comment_title, review_comment_message - not null (null -> N/A)
    na_cols = ["review_comment_title", "review_comment_message"]
    for c in na_cols:
        metrics.append(F.sum((F.col(c) == "N/A").cast("int")).alias(f"missing_{c}"))

    # review_creation_date, review_answer_timestamp - not null, limits
    ts_cols = ["review_creation_date", "review_answer_timestamp"]
    tomorrow = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    for c in ts_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum((F.col(c) < F.lit("2000-01-01 00:00:00").cast("timestamp")).cast("int")).alias(f"old_{c}"))
        metrics.append(F.sum((F.col(c) > tomorrow).cast("int")).alias(f"future_{c}"))

    # dupes count - PK + time
    metrics.append((F.count("*") - F.count_distinct("review_id", "cdc_ts")).alias("duplicate_count"))

    write_dq_metrics(df, metrics, table_name)

    return df
