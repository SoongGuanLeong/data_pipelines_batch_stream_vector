from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.pipeline.batch.common.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)


def transform_order_items(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = [
        "order_id",
        "product_id",
        "seller_id",
    ]
    for c in trim_cols:
        df = remove_control_characters(df, c)
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=trim_cols)

    # Numeric - defensive casting, range check, not null (dropna/fillna), precision
    df = (
        df.withColumn("order_item_id", F.col("order_item_id").cast("integer"))
        .filter(F.col("order_item_id") > 0)
        .dropna(subset=["order_item_id"])
    )

    df = df.filter(F.col("price") > 0).filter(F.col("freight_value") >= 0)

    # timestamp - convert, invalid date
    event_cols = ["created_at", "updated_at"]
    event_upper_limit = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    deadline_cols = ["shipping_limit_date"]
    deadline_upper_limit = F.current_timestamp() + F.expr("INTERVAL 3 MONTHS")

    for c in event_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", event_upper_limit))

    for c in deadline_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", deadline_upper_limit))

    # id - not null (done in string part), dedup (we doing append model), length/regex
    id_cols = ["order_id", "product_id", "seller_id"]
    # check if ids are md5
    for c in id_cols:
        df = df.filter(F.col(c).rlike("^[a-fA-F0-9]{32}$"))

    # string special handling - accents (not needed here)
    return df
