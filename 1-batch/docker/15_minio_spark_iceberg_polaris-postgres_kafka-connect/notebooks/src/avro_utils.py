import requests


def fetch_avro_schema(topic: str, apicurio_url: str, topic_prefix: str) -> str:
    """
    Fetch the latest Avro schema JSON from Apicurio Registry for a topic.
    Returns a JSON string ready for Spark from_avro().
    """

    url = f"{apicurio_url}/{topic_prefix}.{topic}-value/versions/latest"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
