from pyspark.sql import DataFrame, functions as F
from src.monitoring.dq_metrics import write_dq_metrics


def collect_orders_dq_metrics(df: DataFrame, table_name: str) -> DataFrame:

    metrics = []

    # order_id, customer_id - not null, md5
    id_cols = ["order_id", "customer_id"]
    for c in id_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum((~F.col(c).rlike("^[a-fA-F0-9]{32}$")).cast("int")).alias(f"invalid_{c}"))
    # order_status - enum
    VALID_STATUSES = [
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable",
    ]
    metrics.append(F.sum((~F.col("order_status").isin(VALID_STATUSES)).cast("int")).alias("invalid_order_status"))

    next_three_months = F.current_timestamp() + F.expr("INTERVAL 3 MONTHS")
    # order_purchase_timestamp, order_estimated_delivery_date - not null, limits
    must_have_cols = ["order_purchase_timestamp", "order_estimated_delivery_date"]
    for c in must_have_cols:
        metrics.append(F.sum(F.col(c).isNull().cast("int")).alias(f"null_{c}"))
        metrics.append(F.sum((~F.col(c).between("2000-01-01", next_three_months)).cast("int")).alias(f"invalid_{c}"))
    # order_approved_at, order_delivered_carrier_date, order_delivered_customer_date - can null, limits
    lifecycle_cols = [
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ]
    for c in lifecycle_cols:
        metrics.append(
            F.sum((F.col(c).isNotNull() & ~F.col(c).between("2000-01-01", next_three_months)).cast("int")).alias(
                f"invalid_{c}"
            )
        )

    # dupes count - PK + time
    metrics.append((F.count("*") - F.count_distinct("order_id", "cdc_ts")).alias("duplicate_count"))

    write_dq_metrics(df, metrics, table_name)

    return df
