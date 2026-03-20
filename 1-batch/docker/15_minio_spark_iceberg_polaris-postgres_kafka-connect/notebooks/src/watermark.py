from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F


# =========================================================
# 1. Get last commit timestamp (Iceberg metadata)
# =========================================================
def get_last_commit_ts(
    spark: SparkSession,
    target_table: str,
) -> str | None:
    """
    Get latest snapshot commit timestamp from Iceberg table.

    Returns None if table is empty or does not exist.
    """

    try:
        df = spark.sql(f"""
            SELECT max(committed_at) AS ts
            FROM {target_table}.snapshots
        """)

        result = df.collect()[0]["ts"]
        return result

    except Exception:
        # table might not exist yet (first run)
        return None


# =========================================================
# 2. Apply late data buffer
# =========================================================
def get_effective_watermark(
    last_commit_ts,
    buffer_hours: int,
):
    """
    Apply buffer to handle late-arriving data.

    Returns a column expression usable in filters.
    """

    if last_commit_ts is None:
        return None

    return F.lit(last_commit_ts) - F.expr(f"INTERVAL {buffer_hours} HOURS")


# =========================================================
# 3. Detect changed keys (generic)
# =========================================================
def get_changed_keys(
    spark: SparkSession,
    source_table: str,
    key_column: str,
    effective_ts,
) -> DataFrame:
    """
    Generic changed key detection.

    Parameters
    ----------
    source_table : str
        Silver/source table
    key_column : str
        Primary key column (e.g., customer_id)
    effective_ts :
        watermark threshold (Column expression)

    Returns
    -------
    DataFrame with distinct changed keys
    """

    df = spark.table(source_table)

    if effective_ts is None:
        # first run → return all keys
        return df.select(key_column).distinct()

    return df.filter(F.col("spark_ingest_ts") > effective_ts).select(key_column).distinct()


# =========================================================
# 4. Optional: debug helper (very useful)
# =========================================================
def log_watermark_info(
    last_commit_ts,
    buffer_hours: int,
):
    """
    Simple debug logging for pipeline visibility.
    """

    if last_commit_ts is None:
        print("[Watermark] First run (no previous snapshot)")
        return

    print(f"[Watermark] Last commit ts: {last_commit_ts}")
    print(f"[Watermark] Buffer hours: {buffer_hours}")
