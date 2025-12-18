# data_pipelines_batch_stream_vector
This repository documents my learning journey in building three core types of data pipelines, serving as a single source of truth for my current understanding of modern Data Engineering practices. The focus is on making every component fully runnable in a local development environment to enable faster iteration, easier debugging, and reduce reliance on cloud infrastructure. While processing over 10 TB of data per day remains costly and uncommon today, I believe such large-scale pipelines will become increasingly relevant as LLMs continue to demand massive datasets.

# Pipeline Types
- batch pipeline
- realtime streaming pipeline
- vector db pipeline

## Batch Pipeline
OLTP (MSSQL) → OLTP (postgresql) → Debezium → Kafka + Schema Registry → (attempting iceberg kafka sink connector → Minio)

### Dataset: [AdventureWorks sample databases](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure?view=sql-server-ver17&tabs=ssms)

### Tools used
- [SQL Server 2025 Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
- [SQL Server Management Studio](https://learn.microsoft.com/en-us/ssms/install/install)
- [PostgreSQL](https://www.postgresql.org/download/)
- [PGLOADER](https://pgloader.readthedocs.io/en/latest/install.html)
