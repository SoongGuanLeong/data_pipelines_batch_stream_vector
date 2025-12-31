# data_pipelines_batch_stream_vector
This repository documents my learning journey in building three core types of data pipelines, serving as a single source of truth for my current understanding of modern Data Engineering practices. The focus is on making every component fully runnable in a local development environment to enable faster iteration, easier debugging, and reduce reliance on cloud infrastructure. While processing over 10 TB of data per day remains costly and uncommon today, I believe such large-scale pipelines will become increasingly relevant as LLMs continue to demand massive datasets.

# Pipeline Types
- batch pipeline
- realtime streaming pipeline
- vector db pipeline

## Batch Pipeline (Lakehouse)
OLTP (postgresql) → Debezium → Kafka + Apicurio + AKHQ → Minio → (attempting iceberg kafka sink connector)

#### Dataset: 
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?resource=download)

#### Tools used
- [PostgreSQL 18](https://www.postgresql.org/download/) - OLTP DB
- [Docker Compose](https://www.docker.com/) - To run multiple containers
- [Debezium 3.4](https://quay.io/repository/debezium/connect) - To enable Change Data Capture CDC
  - [docs](https://debezium.io/)
- [Apache Kafka 4.1.1 - Kraft](https://hub.docker.com/r/apache/kafka) - To handle message queues
  - [docs](https://kafka.apache.org/)
- [Apicurio Registry 3.1.6 & its UI](https://quay.io/repository/apicurio/apicurio-registry) - Schema registry to make Kafka messages shorter
  - [docs](https://www.apicur.io/registry/docs/apicurio-registry/3.1.x/index.html)
- [AKHQ 0.26.0](https://hub.docker.com/r/tchiotludo/akhq) - - Apache Kafka GUI
  - [docs](https://akhq.io/docs/)
- [Minio - RELEASE.2025-09-07T16-13-09Z-cpuv1](https://github.com/minio/minio) - S3 compatible storage
  - [docs](https://docs.min.io/enterprise/aistor-object-store/reference/aistor-server/settings/root-credentials/)
- [Minio Client (mc)](https://hub.docker.com/r/minio/mc)
- [Apache Spark](https://hub.docker.com/r/apache/spark)
  - [docs](https://spark.apache.org/)
- [Apache Iceberg](https://iceberg.apache.org/releases/) - Open table format
- [Apache Polaris](https://polaris.apache.org/) - REST catalog for Apache Iceberg (AWS Glue catalog substitute)
