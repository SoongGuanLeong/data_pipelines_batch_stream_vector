from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType

import re


def flatten_structs(df: DataFrame) -> DataFrame:
    """
    Example:
        Input: [id, name, address{street, city}]
        Output: [id, name, address_street, address_city]
    """

    cols = []

    for field in df.schema.fields:
        if isinstance(field.dataType, StructType):
            for nested in field.dataType.fields:
                cols.append(
                    F.col(f"{field.name}.{nested.name}").alias(
                        f"{field.name}_{nested.name}"
                    )
                )

        else:
            cols.append(F.col(field.name))

    return df.select(cols)


def normalize_column_names(df):
    """
    returns a new DataFrame with the renamed columns while keeping the actual data intact
    Example:
        Cust_Name → cust_name
        custID → custid
        CUST_ADDRESS → cust_address
    """

    new_cols = []

    for col in df.columns:
        new = col.lower()
        new = re.sub(r"[^a-z0-9]+", "_", new)

        new_cols.append(new)

    return df.toDF(*new_cols)


def remove_control_characters(df: DataFrame, c: str) -> DataFrame:
    """
    Removes control characters from specified columns.
    """
    # This regex covers non-printable ASCII control characters
    bad_chars_regex = r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"

    return df.withColumn(c, F.regexp_replace(F.col(c), bad_chars_regex, ""))


def convert_accents(df: DataFrame, c: str) -> DataFrame:
    # Source characters and their corresponding targets
    # This is extremely fast because it happens in the JVM
    return df.withColumn(
        c,
        F.translate(
            F.col(c),
            "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
            "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN",
        ),
    )
