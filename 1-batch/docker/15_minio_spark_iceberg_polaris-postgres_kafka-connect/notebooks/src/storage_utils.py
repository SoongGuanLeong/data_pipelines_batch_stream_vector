from .config import *
from .file_utils import safe_file_type
from pathlib import Path
from datetime import datetime


def get_spark_path(file_path: Path, load_date: str):
    """Return s3a path for Spark ingestion"""
    file_type = safe_file_type(file_path)
    return f"s3a://{BUCKET}/{RAW_FOLDER}/{file_type}/load_date={load_date}/{file_path.name}"
