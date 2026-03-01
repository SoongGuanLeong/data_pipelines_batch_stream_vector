# data_pipelines_batch_stream_vector
This repository captures my hands-on journey in building three core types of data pipelines, serving as a single source of truth for modern Data Engineering practices. All components are **fully runnable locally**, enabling fast iteration, easy debugging, and minimal reliance on cloud infrastructure.

While processing over 10 TB of data per day remains costly and uncommon, such large-scale pipelines are increasingly relevant as LLMs drive demand for massive datasets.

> **Note**: This project is fully open source and developed entirely with **free tools**—no Claude, no Cursor—only ChatGPT Free and other open-source software.

# Pipeline Types
- [batch pipeline](#batch-pipeline-lakehouse---micro-batch)
- realtime streaming pipeline (require flink to get ms latency)
- vector db pipeline

## Batch Pipeline (Lakehouse - Micro batch)
![ETL_pipeline](<ETL_pipeline.png>)

OLTP (postgresql) → Debezium → Kafka + Apicurio + AKHQ → Minio → (attempting iceberg kafka sink connector)

#### Dataset: 
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?resource=download)

#### Tools used

##### Local PC
- [PostgreSQL 18](https://www.postgresql.org/download/) - Source: OLTP DB
- [Docker Compose](https://www.docker.com/) - To run multiple containers

##### Ingestion Stack
- [Debezium 3.4](https://quay.io/repository/debezium/connect) - To enable Change Data Capture CDC
  - [docs](https://debezium.io/)
- [Apache Kafka 4.1.1 - Kraft](https://hub.docker.com/r/apache/kafka) - To handle message queues
  - [docs](https://kafka.apache.org/)
- [Apicurio Registry 3.1.6 & its UI](https://quay.io/repository/apicurio/apicurio-registry) - Schema registry to serialize/deserialize message queues
  - [docs](https://www.apicur.io/registry/docs/apicurio-registry/3.1.x/index.html)
- [AKHQ 0.26.0](https://hub.docker.com/r/tchiotludo/akhq) - - Apache Kafka GUI
  - [docs](https://akhq.io/docs/)
- [Alpine Curl](https://hub.docker.com/r/alpine/curl) - to deploy debezium connector automatically

##### Engineering Stack
- [Minio - RELEASE.2025-09-07T16-13-09Z-cpuv1](https://github.com/minio/minio) - S3 compatible storage
  - [docs](https://docs.min.io/enterprise/aistor-object-store/reference/aistor-server/settings/root-credentials/)
- [Minio Client (mc)](https://hub.docker.com/r/minio/mc)
- [Apache Spark](https://hub.docker.com/r/apache/spark)
  - [docs](https://spark.apache.org/)
- [Apache Iceberg](https://iceberg.apache.org/releases/) - Open table format  (metadata inside table)
- [Apache Polaris](https://polaris.apache.org/) - REST catalog for Apache Iceberg (AWS Glue catalog substitute - metadata outside table)
- [Postman](https://www.postman.com/) - API platform to work with APIs
- [Apache Maven](https://maven.apache.org/) - jar build tool

##### ELK Stack - Logging and Monitoring tool

