from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.transform_utils import (
    flatten_structs,
    normalize_column_names,
    remove_control_characters,
)


def transform_order_reviews(df: DataFrame) -> DataFrame:
    df = flatten_structs(df)
    df = normalize_column_names(df)

    # String - remove ctrl chars, trim, not null (dropna/fillna), case format
    trim_cols = [
        "review_id",
        "order_id",
        "review_comment_title",
        "review_comment_message",
    ]
    for c in trim_cols:
        df = remove_control_characters(df, F.col(c))
        df = df.withColumn(c, F.trim(F.col(c)))

    df = df.dropna(subset=["review_id", "order_id"])
    df = df.fillna("N/A", subset=["review_comment_title", "review_comment_message"])

    # Numeric - defensive casting, range check, not null (dropna/fillna), precision
    df = (
        df.withColumn("review_score", F.col("review_score").cast("integer"))
        .filter(F.col("review_score").between(1, 5))
        .dropna(subset=["review_score"])
    )

    # timestamp - convert, invalid date
    microsecond_cols = [
        "created_at",
        "updated_at",
        "review_creation_date",
        "review_answer_timestamp",
    ]
    tomorrow = F.current_timestamp() + F.expr("INTERVAL 1 DAY")
    for c in microsecond_cols:
        df = df.withColumn(c, (F.col(c) / 1000000).cast("timestamp"))
        df = df.filter(F.col(c).between("2000-01-01", tomorrow))

    # id - not null (done in string part), dedup (we doing append model), length/regex
    id_cols = ["review_id", "order_id"]
    # check if ids are md5
    for c in id_cols:
        df = df.filter(F.col(c).rlike("^[a-fA-F0-9]{32}$"))

    # string special handling - accents (not needed here)
    return df
