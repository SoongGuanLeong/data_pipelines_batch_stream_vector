# notebooks/spark_sql_magic.py
from IPython.core.magic import register_cell_magic
from pyspark.sql import SparkSession

# Get or create Spark session
spark = SparkSession.builder.getOrCreate()


@register_cell_magic
def sql(line, cell):
    """
    Run Spark SQL in a notebook cell using %%sql.
    Supports multiple statements separated by ';'.
    Only prints output for statements that return a table.
    """
    statements = [stmt.strip() for stmt in cell.split(";") if stmt.strip()]

    for stmt in statements:
        try:
            df = spark.sql(stmt)
            # Only show if the DataFrame has columns (i.e., SELECT statements)
            if df.columns:
                df.show(truncate=False)
        except Exception as e:
            print(f"⚠️ Error executing statement:\n{stmt}\n{e}")

    return None  # prevent DataFrame[] at the end
