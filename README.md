# data_pipelines_batch_stream_vector
This repository documents my learning journey in building three core types of data pipelines, serving as a single source of truth for everything I currently understand about modern Data Engineering concepts.
The aim is to make all components runnable in a local development environment, enabling faster iteration, easier debugging, and avoiding unnecessary reliance on cloud infrastructure.

## Pipeline Types
- batch pipeline
- realtime streaming pipeline
- vector db pipeline

## Current progress
- batch pipeline
    - dataset: [AdventureWorks sample databases](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure?view=sql-server-ver17&tabs=ssms)
    - OLTP (MSSQL) → Debezium → Kafka + Schema Registry → (attempting iceberg kafka sink connector → Minio)
