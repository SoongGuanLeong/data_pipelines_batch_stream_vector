from .avro_utils import fetch_avro_schema
from .config_loader import load_config
from .file_utils import safe_file_type, checksum
from .metadata_utils import ddl_metadata_table, already_ingested, log_ingestion_metadata
from .spark_sql_magic import sql
from .storage_utils import get_spark_path
from .transform_utils import flatten_structs, normalize_column_names, remove_control_characters, convert_accents
from .watermark import get_last_commit_ts, get_effective_watermark, get_changed_keys, log_watermark_info
from .writers import overwrite_table, replace_by_key, merge_into, overwrite_partitions


__all__ = [
    "fetch_avro_schema",
    "load_config",
    "safe_file_type",
    "checksum",
    "ddl_metadata_table",
    "already_ingested",
    "log_ingestion_metadata",
    "sql",
    "get_spark_path",
    "flatten_structs",
    "normalize_column_names",
    "remove_control_characters",
    "convert_accents",
    "get_last_commit_ts",
    "get_effective_watermark",
    "get_changed_keys",
    "log_watermark_info",
    "overwrite_table",
    "replace_by_key",
    "merge_into",
    "overwrite_partitions",
]
