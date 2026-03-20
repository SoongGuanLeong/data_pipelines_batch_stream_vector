from pyspark.sql import DataFrame, SparkSession


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
    key_column: str,
) -> None:
    """
    Replace data for specific keys (DELETE + INSERT).

    Pattern:
    1. Delete existing rows for affected keys
    2. Insert recomputed rows

    Guarantees:
    - idempotent (same input → same output)
    - correct for SCD2
    """

    staging_table = f"{target_table}__staging"

    # write new data
    df.write.format("iceberg").mode("overwrite").saveAsTable(staging_table)

    # get affected keys once
    spark.sql(f"""
        CREATE OR REPLACE TEMP VIEW affected_keys AS
        SELECT DISTINCT {key_column} FROM {staging_table}
    """)

    # delete only affected keys
    spark.sql(f"""
        DELETE FROM {target_table}
        WHERE {key_column} IN (SELECT {key_column} FROM affected_keys)
    """)

    # --- INSERT new data ---
    spark.sql(f"""
        INSERT INTO {target_table}
        SELECT * FROM {staging_table}
    """)


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
