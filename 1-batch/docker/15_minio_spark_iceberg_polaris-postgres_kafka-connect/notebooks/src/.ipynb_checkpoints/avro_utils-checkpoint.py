import requests
from .config import *


def fetch_avro_schema(topic: str) -> str:
    """
    Fetch the latest Avro schema JSON from Apicurio Registry for a topic.
    Returns a JSON string ready for Spark from_avro().
    """

    url = f"{APICURIO_URL}/{TOPIC_PREFIX}.{topic}-value/versions/latest"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
