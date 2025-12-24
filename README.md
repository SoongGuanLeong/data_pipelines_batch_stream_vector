# data_pipelines_batch_stream_vector
This repository documents my learning journey in building three core types of data pipelines, serving as a single source of truth for my current understanding of modern Data Engineering practices. The focus is on making every component fully runnable in a local development environment to enable faster iteration, easier debugging, and reduce reliance on cloud infrastructure. While processing over 10 TB of data per day remains costly and uncommon today, I believe such large-scale pipelines will become increasingly relevant as LLMs continue to demand massive datasets.

# Pipeline Types
- batch pipeline
- realtime streaming pipeline
- vector db pipeline

## Batch Pipeline
OLTP (postgresql) → Debezium → Kafka + Apicurio → (attempting iceberg kafka sink connector → Minio)

#### Dataset: 
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?resource=download)

#### Tools used
- [PostgreSQL 18](https://www.postgresql.org/download/)
- [Docker Compose](https://www.docker.com/)
- [Debezium 3.4](https://quay.io/repository/debezium/connect) 
  - [docs](https://debezium.io/)
- [Apache Kafka 3.4 - Kraft](https://quay.io/repository/debezium/kafka)
  - [docs](https://kafka.apache.org/)
- [Apicurio Registry 3.1.6 & its UI](https://quay.io/repository/apicurio/apicurio-registry)
  - [docs](https://www.apicur.io/registry/docs/apicurio-registry/3.1.x/index.html)
- [AKHQ 0.26.0 - Apache Kafka GUI](https://hub.docker.com/r/tchiotludo/akhq)
  - [docs](https://akhq.io/docs/)
