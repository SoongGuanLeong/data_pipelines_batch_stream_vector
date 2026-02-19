import hashlib
from .config import *
from datetime import datetime
from pathlib import Path


def safe_file_type(file_path: Path):
    """Infer file type; unknown types go to 'other'"""
    ext = file_path.suffix.lower().lstrip(".")
    return ext if ext in ALLOWED_TYPES else "other"


def checksum(file_path: Path, algo="md5"):
    """Compute file checksum"""
    h = hashlib.new(algo)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def get_target_path(file_path: Path):
    """Return MinIO path using type + load_date partition"""
    today = datetime.today().strftime("%Y-%m-%d")
    file_type = safe_file_type(file_path)
    return f"{MC_ALIAS}/{BUCKET}/{RAW_FOLDER}/{file_type}/load_date={today}/{file_path.name}"


def get_spark_path(file_path: Path):
    """Return s3a path for Spark ingestion"""
    today = datetime.today().strftime("%Y-%m-%d")
    file_type = safe_file_type(file_path)
    return f"s3a://{BUCKET}/{RAW_FOLDER}/{file_type}/load_date={today}/{file_path.name}"
