# Port & Service Inventory

Docker Network: data-pipeline-net

## Externally Exposed Ports (Host → Container)

| Service     | Host Port | Container Port | Protocol | Purpose                |
|-------------|-----------|----------------|----------|------------------------|
| kafka       | 9092      | 9092           | kafka    | event streaming        |
| apicurio    | 8081      | 8081           | http     | schema registry        |
| apicurio-ui | 8888      | 8080           | http     | schema registry UI     |
| connect     | 8083      | 8083           | http     | enable CDC             |
| akhq        | 8082      | 8080           | http     | UI for ingestion stack |