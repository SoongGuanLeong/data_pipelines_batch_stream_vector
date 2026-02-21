from pathlib import Path
from datetime import datetime, timezone
from .raw_utils import safe_file_type


def log_ingestion_metadata(
    spark,
    table_name: str,
    file_path: Path,
    spark_path: str,
    checksum: str,
):

    file_size = file_path.stat().st_size
    upload_ts = datetime.now(timezone.utc)
    file_type = safe_file_type(file_path)

    metadata_df = spark.createDataFrame(
        [
            {
                "file_name": file_path.name,
                "file_type": file_type,
                "path": spark_path,
                "size_bytes": file_size,
                "upload_ts": upload_ts,
                "checksum": checksum,
            }
        ]
    )

    metadata_df.write.format("iceberg").mode("append").saveAsTable(table_name)
