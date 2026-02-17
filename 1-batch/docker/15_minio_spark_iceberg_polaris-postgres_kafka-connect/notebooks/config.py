# catalog / storage
CATALOG = "polaris"
BRONZE_NAMESPACE = "bronze"
SILVER_NAMESPACE = "silver"
GOLD_NAMESPACE = "gold"

BUCKET = "s3://olist-ecommerce"

# spark job
PROJECT = "olist"

JOB_NAMES = {
    "init_lakehouse": f"{PROJECT}-init-lakehouse",
    "bronze_ddl": f"{PROJECT}-bronze-ddl",
    "bronze_ingestion": f"{PROJECT}-bronze-ingestion",
}

# Kafka
KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC_PREFIX = "olist.oltp"

# url
APICURIO_URL = "http://apicurio:8081/apis/registry/v2/groups/default/artifacts"

# Ingestion topics
INGESTION_CONFIG = [
    "customers",
    "order_items",
    "order_payments",
    "order_reviews",
    "orders",
    "products",
    "sellers",
]
