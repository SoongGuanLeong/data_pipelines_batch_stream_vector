from pyspark.sql import DataFrame, SparkSession
from typing import List
import uuid


# =========================================================
# 1. Full overwrite (stateless pipelines)
# =========================================================
def overwrite_table(
    df: DataFrame,
    target_table: str,
) -> None:
    """
    Full table overwrite.

    Use for:
    - stateless pipelines
    - small/medium tables
    """

    (df.write.format("iceberg").mode("overwrite").saveAsTable(target_table))


# =========================================================
# 2. Key-level replace (incremental SCD2 pattern)
# =========================================================
def replace_by_key(
    spark: SparkSession,
    df: DataFrame,
    target_table: str,
    key_columns: List[str],
) -> None:
    """
    Replace data for specific keys (DELETE + INSERT).

    Production-safe version:
    - supports composite keys
    - safe for concurrent runs
    - no staging table conflicts
    """

    staging_table = f"{target_table}_staging_{uuid.uuid4().hex}"

    try:
        # write new data
        df.write.format("iceberg").mode("overwrite").saveAsTable(staging_table)

        # dynamically build condition string
        conditions = []
        for col in key_columns:
            conditions.append(f"t.{col} = s.{col}")
        join_condition = " AND ".join(conditions)

        # delete only affected keys
        spark.sql(f"""
            DELETE FROM {target_table} t
            WHERE EXISTS (
                SELECT 1
                FROM {staging_table} s
                WHERE {join_condition}
            )
        """)

        # --- INSERT new data ---
        col_list = ", ".join(df.columns)
        spark.sql(f"""
            INSERT INTO {target_table} ({col_list})
            SELECT {col_list} FROM {staging_table}
        """)
    finally:
        spark.sql(f"DROP TABLE IF EXISTS {staging_table}")


# =========================================================
# 3. Optional: MERGE (stateful alternative)
# =========================================================
def merge_into(
    spark: SparkSession,
    df: DataFrame,
    target_table: str,
    merge_condition: str,
) -> None:
    """
    Generic MERGE INTO.

    Use only when:
    - true incremental row-level updates needed
    - not doing full-key replacement

    WARNING:
    - more complex
    - state-dependent
    """

    staging_table = f"{target_table}__staging"

    df.write.format("iceberg").mode("overwrite").saveAsTable(staging_table)

    spark.sql(f"""
        MERGE INTO {target_table} t
        USING {staging_table} s
        ON {merge_condition}

        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)


# =========================================================
# 4. Optional: safe overwrite with partition pruning
# =========================================================
def overwrite_partitions(
    df: DataFrame,
    target_table: str,
) -> None:
    """
    Overwrite only affected partitions.

    Requires:
    - table is partitioned
    - df contains partition columns

    Note:
    Iceberg handles this efficiently.
    """

    (df.write.format("iceberg").mode("overwrite").option("overwrite-mode", "dynamic").saveAsTable(target_table))
