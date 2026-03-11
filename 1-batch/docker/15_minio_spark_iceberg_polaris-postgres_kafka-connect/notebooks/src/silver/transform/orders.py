from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)


def transform_orders(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = [
        "order_id",
        "customer_id",
        "order_status",
    ]
    for c in trim_cols:
        df = remove_control_characters(df, F.col(c))
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=trim_cols)

    df = df.withColumn("order_status", F.lower(F.col("order_status")))
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
    df = df.filter(F.col("order_status").isin(VALID_STATUSES))

    # timestamp - convert, invalid date
    must_have_cols = [
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
        "created_at",
        "updated_at",
    ]
    lifecycle_cols = [
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ]

    next_three_months = F.current_timestamp() + F.expr("INTERVAL 3 MONTHS")

    for c in must_have_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", next_three_months))

    for c in lifecycle_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.withColumn(
            c,
            F.when(
                F.col(c).between("2000-01-01", next_three_months), F.col(c)
            ).otherwise(F.lit(None)),  # filter extreme dates and keep null values
        )

    # id - not null (done in string part), dedup (we doing append model), length/regex
    id_cols = ["order_id", "customer_id"]
    # check if ids are md5
    for c in id_cols:
        df = df.filter(F.col(c).rlike("^[a-fA-F0-9]{32}$"))

    # string special handling - accents (not needed here)
    return df
