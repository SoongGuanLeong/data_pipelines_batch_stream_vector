# ================================================================================
# catalog / storage
# ================================================================================
PROJECT = "olist"
CATALOG = "polaris"
BRONZE_NAMESPACE = "bronze"
SILVER_NAMESPACE = "silver"
GOLD_NAMESPACE = "gold"

BUCKET = "olist-ecommerce"

# ================================================================================
# spark job
# ================================================================================
JOB_NAMES = {
    "raw_ingestion": f"{PROJECT}-raw-ingestion",
    "init_lakehouse": f"{PROJECT}-init-lakehouse",
    "bronze_cdc_ddl": f"{PROJECT}-bronze-cdc-ddl",
    "bronze_cdc_ingestion_backfill": f"{PROJECT}-bronze-cdc-ingestion-backfill",
    "bronze_cdc_ingestion_update": f"{PROJECT}-bronze-cdc-ingestion-update",
    "bronze_lookup_ddl_ingestion": f"{PROJECT}-bronze-lookup-ddl-ingestion",
}

# ================================================================================
# Kafka
# ================================================================================
KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC_PREFIX = "olist.oltp"
CHECKPOINT_BASE = f"s3a://{BUCKET}/checkpoints"

# url
APICURIO_URL = "http://apicurio:8081/apis/registry/v2/groups/default/artifacts"

# Ingestion topics
TOPIC_SUFFIX = [
    "customers",
    "order_items",
    "order_payments",
    "order_reviews",
    "orders",
    "products",
    "sellers",
]

# ================================================================================
# Minio / Raw ingestion
# ================================================================================
MC_ALIAS = "myminio"
RAW_FOLDER = "raw"

ALLOWED_TYPES = {"csv", "json", "parquet", "jpg", "png", "pdf", "txt"}

RAW_METADATA_TABLE = "raw_ingestion_metadata"
LOOKUP_METADATA_TABLE = "lookup_ingestion_metadata"

LOOKUP_TABLES = {
    "geolocation": {
        "schema": """
            geolocation_zip_code_prefix STRING,
            geolocation_lat DOUBLE,
            geolocation_lng DOUBLE,
            geolocation_city STRING,
            geolocation_state STRING
        """,
        "file_path": "/opt/spark/datasets/olist_geolocation_dataset.csv",
    },
    "product_category_name": {
        "schema": """
            product_category_name STRING,
            product_category_name_english STRING
        """,
        "file_path": "/opt/spark/datasets/product_category_name_translation.csv",
    },
}
