from .config import *
import hashlib
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
