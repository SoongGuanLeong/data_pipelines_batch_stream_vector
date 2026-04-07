from pyspark.sql import DataFrame, functions as F


def write_dq_metrics(
    df: DataFrame,
    metrics: list,
    table_name: str,
    pipeline_stage: str = "silver",
    table: str = "monitoring.dq_metrics",
) -> DataFrame:

    metrics_df = df.agg(*metrics)

    metric_cols = metrics_df.columns

    metric_names = F.array(*[F.lit(c) for c in metric_cols])
    metric_values = F.array(*[F.col(c) for c in metric_cols])

    metrics_long = (
        metrics_df.select(
            F.explode(F.map_from_arrays(metric_names, metric_values)).alias("metric_name", "metric_value")
        )
        .withColumn("pipeline_stage", F.lit(pipeline_stage))
        .withColumn("source_table", F.lit(table_name))
        .withColumn("timestamp", F.current_timestamp())
    )

    metrics_long.writeTo(table).append()

    return df
