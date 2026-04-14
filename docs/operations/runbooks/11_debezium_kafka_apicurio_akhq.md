# 11_debezium_kafka_apicurio_akhq

This step corresponds to the Docker Compose setup for CDC stack - **Debezium + Kafka + Apicurio + AKHQ**.

## Location

The actual Docker Compose files are located [here](../../../infra\docker\cdc_stack\docker-compose.yaml).

## Usage
```pwsh
docker network create data-pipeline-net
docker compose up -d
```
