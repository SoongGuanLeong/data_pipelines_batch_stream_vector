from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.pipeline.batch.common.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
    convert_accents,
)


def transform_sellers(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]
    for c in trim_cols:
        df = remove_control_characters(df, c)
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=["seller_id"])
    df = df.fillna("N/A", subset=["seller_zip_code_prefix", "seller_city", "seller_state"])

    df = df.withColumn("seller_city", F.initcap(F.col("seller_city"))).withColumn(
        "seller_state", F.upper(F.col("seller_state"))
    )

    # timestamp - convert, invalid date
    microsecond_cols = ["created_at", "updated_at"]
    tomorrow = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    for c in microsecond_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", tomorrow))

    # id - not null (done in string part), dedup (we doing append model), length/regex
    id_cols = ["seller_id"]
    # check if ids are md5
    for c in id_cols:
        df = df.filter(F.col(c).rlike("^[a-fA-F0-9]{32}$"))

    # string special handling - accents (not carry semantic meaning)
    accent_cols = ["seller_city", "seller_state"]
    for c in accent_cols:
        df = convert_accents(df, c)

    return df
