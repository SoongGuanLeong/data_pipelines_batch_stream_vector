-- if have time do RPA

- load data into sql server (was done with ssms)

- create a docker network (so that it can be used by multiple docker-compose)
```
docker network create my-network
```

- create a random id as cluster_id, put it into docker compose
```
docker run --rm -it confluentinc/cp-kafka:7.5.0 bash
kafka-storage random-uuid
```

- sql server enable tcp/ip, then restart sql server (MSSQLSERVER) (using sql server configuration manager)
  - later need to figure out how to follow the "principle of least privilage" 

- test connection
```bash
docker exec -it connect bash
timeout 5 bash -c "echo > /dev/tcp/host.docker.internal/1433" && echo "✅ Connected" || echo "❌ Connection failed"
```

- [enable database for CDC](https://debezium.io/documentation/reference/stable/connectors/sqlserver.html#_enabling_cdc_on_the_sql_server_database)
- [enable table for CDC](https://debezium.io/documentation/reference/stable/connectors/sqlserver.html#_enabling_cdc_on_a_sql_server_table)
- verify with 
```
USE AdventureWorks2022;
SELECT name, is_tracked_by_cdc FROM sys.tables;
```
- create sa and password for sql server

- make a post request to debezium to use sql server connector
```terminal
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @sqlserver-connector.json
```

- download the files listed below, put them in docker/connect-plugins
  - [Kafka Connect Avro Converter](https://www.confluent.io/hub/confluentinc/kafka-connect-avro-converter)
  - [Debezium-SQL Server Connector](https://repo1.maven.org/maven2/io/debezium/debezium-connector-sqlserver/3.3.1.Final/debezium-connector-sqlserver-3.3.1.Final-plugin.tar.gz)
  - if not working still, find and add the jar files mentioned in this [link](https://debezium.io/documentation/reference/3.3/configuration/avro.html#confluent-schema-registry)