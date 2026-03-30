import requests
import time


def fetch_avro_schema(topic: str, apicurio_url: str, topic_prefix: str) -> str:
    """
    Fetch the latest Avro schema JSON from Apicurio Registry for a topic.
    Returns a JSON string ready for Spark from_avro().
    """
    subject = f"{topic_prefix}.{topic}-value"
    url = f"{apicurio_url}/{subject}/versions/latest"

    max_retries = 5
    base_delay = 1  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)

            # ---- Success ----
            if response.status_code == 200:
                return response.json()

            # ---- Non-retryable errors ----
            if response.status_code in (400, 401, 403, 404):
                raise RuntimeError(f"[SchemaRegistry] Non-retryable error {response.status_code} for subject={subject}")

            # ---- Retryable HTTP errors ----
            if response.status_code >= 500:
                raise requests.exceptions.HTTPError(f"Server error {response.status_code}")

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            # ---- Retry logic ----
            if attempt == max_retries:
                raise RuntimeError(
                    f"[SchemaRegistry] Failed after {max_retries} attempts for subject={subject} | last_error={str(e)}"
                )

            sleep_time = base_delay * (2 ** (attempt - 1))

            print(
                f"[SchemaRegistry] Attempt {attempt} failed for subject={subject}. "
                f"Retrying in {sleep_time}s | error={str(e)}"
            )

            time.sleep(sleep_time)
