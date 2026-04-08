from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F, Window as W


def apply_scd2(
    df: DataFrame,
    business_key: str,
    surrogate_key: str,
    effective_from_col: str = "cdc_ts",
    tie_breaker_col: str = "spark_ingest_ts",
) -> DataFrame:
    """
    Apply SCD2 interval columns and deterministic surrogate key generation.
    """

    w = W.partitionBy(business_key).orderBy(F.col(effective_from_col), F.col(tie_breaker_col))

    return (
        df.withColumn("effective_from", F.col(effective_from_col))
        .withColumn("effective_to", F.lead(effective_from_col).over(w))
        .withColumn("is_current", F.col("effective_to").isNull())
        .withColumn(surrogate_key, F.sha2(F.concat_ws("||", F.col(business_key), F.col("effective_from")), 256))
    )


def build_temporal_scd2_join_condition(
    fact_key: Column,
    dim_key: Column,
    fact_event_ts: Column,
    dim_effective_from: Column,
    dim_effective_to: Column,
) -> Column:
    """
    Build standard SCD2 temporal join condition:
      fact.key = dim.key
      and fact_ts >= dim.effective_from
      and (fact_ts < dim.effective_to or dim.effective_to is null)
    """

    return (
        (fact_key == dim_key)
        & (fact_event_ts >= dim_effective_from)
        & ((fact_event_ts < dim_effective_to) | dim_effective_to.isNull())
    )
