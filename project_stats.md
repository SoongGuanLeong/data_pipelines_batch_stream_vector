
This file is created from this command below using [boyter/scc](https://github.com/boyter/scc):
```
scc --exclude-dir .ipynb_checkpoints,venv,.git --exclude-ext csv,json,properties,xml --by-file > project_stats.md
```
```
───────────────────────────────────────────────────────────────────────────────
Language            Files       Lines    Blanks  Comments       Code Complexity
───────────────────────────────────────────────────────────────────────────────
Python                 47       2,472       450       392      1,630         73
───────────────────────────────────────────────────────────────────────────────
~\gold\facts\order_items.py       199        26        40        133          1
~t\notebooks\src\writers.py       127        18        52         57          3
~old\facts\order_reviews.py       124        22        22         80          1
~ld\facts\order_payments.py       117        22        19         76          1
~s\src\gold\dims\sellers.py       116        20        30         66          0
~s\src\gold\facts\orders.py       113        22        29         62          1
~src\gold\dims\customers.py       110        18        25         67          0
~notebooks\src\watermark.py        98        18        42         38          5
~\src\gold\dims\products.py        97        23        15         59          0
~silver\transform\orders.py        75        12         5         58          4
~oks\src\transform_utils.py        72        18        18         36          5
~ransform\order_payments.py        65        11         4         50          3
~lver\transform\products.py        65        12         6         47          5
~ooks\src\metadata_utils.py        61        11         1         49          1
~r\transform\order_items.py        57        12         6         39          4
~ver\transform\customers.py        56        11         6         39          4
~transform\order_reviews.py        55         9         6         40          3
~ilver\transform\sellers.py        54        10         5         39          4
~src\silver\dq\orders_dq.py        51         8         5         38          3
~tebooks\src\gold\common.py        49         8         9         32          1
~otebooks\src\avro_utils.py        46        11         8         27          7
~c\silver\dq\products_dq.py        43        10         5         28          3
~r\transform\geolocation.py        43         8         3         32          1
~\notebooks\src\__init__.py        41         3         0         38          0
~tebooks\src\gold\helper.py        38         8         0         30          0
~ilver\dq\geolocation_dq.py        37         9         0         28          0
~ver\dq\order_reviews_dq.py        36         9         5         22          3
~ilver\dq\order_items_dq.py        34        10         5         19          1
~ooks\src\gold\dims\date.py        33         5         1         27          0
~c\monitoring\dq_metrics.py        30         8         0         22          2
~src\silver\dq\common_dq.py        30         8         3         19          2
~m\product_category_name.py        29         8         1         20          1
~er\dq\order_payments_dq.py        28         6         5         17          1
~roduct_category_name_dq.py        27         7         0         20          0
~oks\src\spark_sql_magic.py        27         3         4         20          0
~\src\silver\dq\__init__.py        25         3         0         22          0
~\silver\dq\customers_dq.py        23         6         3         14          1
~src\gold\facts\__init__.py        23         1         0         22          0
~lver\transform\__init__.py        21         1         0         20          0
~rc\silver\dq\sellers_dq.py        19         5         3         11          0
~\src\gold\dims\__init__.py        17         1         0         16          0
~otebooks\src\file_utils.py        17         2         0         15          0
~books\src\storage_utils.py        14         2         1         11          0
~books\src\gold\__init__.py        12         1         0         11          0
~books\src\config_loader.py        11         2         0          9          2
~oks\src\silver\__init__.py         4         1         0          3          0
~src\monitoring\__init__.py         3         1         0          2          0
───────────────────────────────────────────────────────────────────────────────
Jupyter                17       6,613         0         0      6,613          0
───────────────────────────────────────────────────────────────────────────────
~\notebooks\23_silver.ipynb     1,226         0         0      1,226          0
~ks\20_bronze_cdc_ddl.ipynb       571         0         0        571          0
~bronze_cdc_ingestion.ipynb       542         0         0        542          0
~es_integration_check.ipynb       461         0         0        461          0
~oks\19_raw_ingestion.ipynb       368         0         0        368          0
~oks\33_orchestration.ipynb       352         0         0        352          0
~lookup_ddl_ingestion.ipynb       336         0         0        336          0
~old_fact_order_items.ipynb       328         0         0        328          0
~d_fact_order_reviews.ipynb       321         0         0        321          0
~_fact_order_payments.ipynb       320         0         0        320          0
~\29_gold_fact_orders.ipynb       299         0         0        299          0
~26_gold_dim_products.ipynb       288         0         0        288          0
~\25_gold_dim_sellers.ipynb       287         0         0        287          0
~4_gold_dim_customers.ipynb       286         0         0        286          0
~oks\27_gold_dim_date.ipynb       241         0         0        241          0
~ks\18_init_lakehouse.ipynb       220         0         0        220          0
~_gold_dims_bootstrap.ipynb       167         0         0        167          0
───────────────────────────────────────────────────────────────────────────────
Markdown               17       1,610       370         0      1,240          0
───────────────────────────────────────────────────────────────────────────────
~plementation_strategies.md       276        96         0        180          0
completion_roadmap.md             223        71         0        152          0
~park_pipeline_checklist.md       214        60         0        154          0
~laris\polaris_setup_101.md       171        12         0        159          0
~docs\schema\star_schema.md       155        10         0        145          0
~\schema\original_schema.md       139        19         0        120          0
~ver\transform\checklist.md       123        43         0         80          0
~tors\post_connector_101.md       119        14         0        105          0
README.md                          81        17         0         64          0
~nectors\enable_apicurio.md        55         6         0         49          0
~ium_kafka_apicurio_akhq.md        13         4         0          9          0
~ploy_debezium_connector.md        13         6         0          7          0
~-postgres_kafka-connect.md         7         3         0          4          0
~o_spark_iceberg_polaris.md         7         3         0          4          0
~pts\19_bronze_ingestion.md         7         3         0          4          0
~ripts\18_init_lakehouse.md         7         3         0          4          0
project_stats.md                    0         0         0          0          0
───────────────────────────────────────────────────────────────────────────────
SQL                    11         910       123       133        654          0
───────────────────────────────────────────────────────────────────────────────
~scripts\08_load_tables.sql       256        21        26        209          0
~ch\scripts\13_test_cdc.sql       166        38        10        118          0
~cripts\07_load_staging.sql       117        16        18         83          0
~ripts\03_create_tables.sql       103         8         9         86          0
~ipts\06_create_staging.sql       100         9         9         82          0
~tch\scripts\04_add_FKs.sql        56         9        23         24          0
~scripts\05_add_indexes.sql        50         9        25         16          0
~\09_create_publication.sql        33         6         8         19          0
~ch\scripts\10_prep_cdc.sql        17         4         5          8          0
~_test_schema_evolution.sql        11         3         0          8          0
~ripts\02_create_schema.sql         1         0         0          1          0
───────────────────────────────────────────────────────────────────────────────
YAML                   11         623        46        65        512          0
───────────────────────────────────────────────────────────────────────────────
~onnect\docker-compose.yaml       211        16        29        166          0
~o_akhq\docker-compose.yaml       162        11        31        120          0
~otebooks\configs\gold.yaml        64         0         0         64          0
~toring\docker-compose.yaml        63         5         5         53          0
.github\workflows\CI.yml           51        11         0         40          0
~notebooks\configs\raw.yaml        28         2         0         26          0
~ks\configs\spark_jobs.yaml        17         0         0         17          0
~tebooks\configs\kafka.yaml        11         0         0         11          0
~books\configs\general.yaml         8         0         0          8          0
~ring\filebeat\filebeat.yml         7         1         0          6          0
~notebooks\configs\api.yaml         1         0         0          1          0
───────────────────────────────────────────────────────────────────────────────
Shell                   3         308        43        59        206         21
───────────────────────────────────────────────────────────────────────────────
~ts\16_polaris_bootstrap.sh       248        31        39        178         17
~ectors\deploy_connector.sh        47         9        17         21          3
~atch\scripts\01_init_db.sh        13         3         3          7          1
───────────────────────────────────────────────────────────────────────────────
Dockerfile              1          40         9        11         20          3
───────────────────────────────────────────────────────────────────────────────
~a-connect\spark\Dockerfile        40         9        11         20          3
───────────────────────────────────────────────────────────────────────────────
Makefile                1         119        22         3         94         37
───────────────────────────────────────────────────────────────────────────────
1-batch\Makefile                  119        22         3         94         37
───────────────────────────────────────────────────────────────────────────────
Total                 108      12,695     1,063       663     10,969        134
───────────────────────────────────────────────────────────────────────────────
Estimated Cost to Develop (organic) $334,018
Estimated Schedule Effort (organic) 9.07 months
Estimated People Required (organic) 3.27
───────────────────────────────────────────────────────────────────────────────
Processed 470941 bytes, 0.471 megabytes (SI)
───────────────────────────────────────────────────────────────────────────────
```