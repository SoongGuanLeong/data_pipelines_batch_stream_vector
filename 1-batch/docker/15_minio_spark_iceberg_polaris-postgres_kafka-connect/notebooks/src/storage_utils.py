from .file_utils import safe_file_type
from pathlib import Path
from datetime import datetime


def get_spark_path(
    file_path: Path,
    load_date: str,
    bucket: str,
    raw_folder: str,
    allowed_types: set[str],
):
    """Return s3a path for Spark ingestion"""
    file_type = safe_file_type(file_path, allowed_types)
    return f"s3a://{bucket}/{raw_folder}/{file_type}/load_date={load_date}/{file_path.name}"
