from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)

from pyspark.sql.types import DecimalType


def transform_order_payments(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = [
        "order_id",
        "payment_type",
    ]
    for c in trim_cols:
        df = remove_control_characters(df, F.col(c))
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=["order_id"])
    df = df.fillna("not_defined", subset=["order_id"])

    df = df.withColumn("payment_type", F.lower(F.col("payment_type")))
    VALID_PAYMENT_TYPES = [
        "boleto",
        "debit_card",
        "voucher",
        "credit_card",
    ]
    df = df.withColumn(
        "payment_type",
        F.when(
            F.col("payment_type").isin(VALID_PAYMENT_TYPES), F.col("payment_type")
        ).otherwise("N/A"),
    )

    # Numeric - not null (dropna/fillna), defensive casting, range check, precision
    df = df.fillna(0, subset=["payment_value"])
    df = df.withColumn(
        "payment_value",
        F.when(F.col("payment_value") < 0, 0).otherwise(F.col("payment_value")),
    )
    df = df.withColumn("payment_value", F.col("payment_value").cast(DecimalType(18, 6)))

    cannot_zero_cols = ["payment_sequential", "payment_installments"]
    for c in cannot_zero_cols:
        df = df.withColumn(c, F.when(F.col(c) == 0, 1).otherwise(F.col(c)))
        df = df.filter((F.col(c) >= 1))
        df = df.withColumn(c, F.col(c).cast("integer"))

    # timestamp - convert, invalid date
    microsecond_cols = ["created_at", "updated_at"]
    tomorrow = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    for c in microsecond_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", tomorrow))

    # string special handling - accents (not needed here)
    return df
