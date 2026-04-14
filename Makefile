SHELL := /bin/bash
.DEFAULT_GOAL := help
.NOTPARALLEL:

# Local PostgreSQL defaults (override on command line if needed)
DB_USER ?= postgres
DB_NAME ?= olist
DB_HOST ?= localhost
DB_PORT ?= 5432

# Folder that contains olist_*.csv files
DATASET_DIR ?= $(CURDIR)/data/raw/olist

PSQL ?= psql
PSQL_FLAGS ?= -v ON_ERROR_STOP=1
PSQL_ADMIN := $(PSQL) $(PSQL_FLAGS) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER)
PSQL_DB := $(PSQL_ADMIN) -d $(DB_NAME)

REQUIRED_CSVS := \
	olist_customers_dataset.csv \
	olist_orders_dataset.csv \
	olist_geolocation_dataset.csv \
	olist_products_dataset.csv \
	olist_order_items_dataset.csv \
	olist_sellers_dataset.csv \
	olist_order_payments_dataset.csv \
	product_category_name_translation.csv \
	olist_order_reviews_dataset.csv

.PHONY: help check-tools check-sql check-dataset \
	init-db create-schema create-tables add-fks add-indexes create-staging load-staging \
	load-tables create-publication prep-cdc setup-postgres \
	test-cdc \
	init-polaris

help:
	@echo "Available targets:"
	@echo "  check-tools         - Validate required CLI tools are installed"
	@echo "  check-sql           - Validate required SQL/bootstrap files exist"
	@echo "  check-dataset       - Validate required dataset files exist"
	@echo "  init-db             - Create database $(DB_NAME) if it does not exist"
	@echo "  create-schema       - Create OLTP schema"
	@echo "  create-tables       - Create OLTP tables"
	@echo "  add-fks             - Add foreign keys"
	@echo "  add-indexes         - Add performance indexes"
	@echo "  create-staging      - Create staging schema and tables"
	@echo "  load-staging        - Load CSV files from DATASET_DIR into staging"
	@echo "  load-tables         - Load OLTP tables from staging"
	@echo "  create-publication  - Create Debezium publication"
	@echo "  prep-cdc            - Prepare postgres for CDC"
	@echo "  setup-postgres      - Run postgres setup in correct order"
	@echo "  test-cdc            - Test if CDC is working"
	@echo "  init-polaris		 - Run Polaris bootstrap script"
	@echo ""
	@echo "Variables (override like: make setup-postgres DB_USER=postgres DATASET_DIR=/path/to/csvs):"
	@echo "  DB_USER, DB_NAME, DB_HOST, DB_PORT, DATASET_DIR, PSQL, PSQL_FLAGS"

check-tools:
	@command -v "$(PSQL)" >/dev/null 2>&1 || (echo "Required tool not found: $(PSQL)" && exit 1)
	@command -v docker >/dev/null 2>&1 || (echo "Required tool not found: docker" && exit 1)

check-sql:
	@test -f infra/bootstrap/01_init_db.sh || (echo "Missing file: infra/bootstrap/01_init_db.sh" && exit 1)
	@test -f infra/sql/02_create_schema.sql || (echo "Missing file: infra/sql/02_create_schema.sql" && exit 1)
	@test -f infra/sql/03_create_tables.sql || (echo "Missing file: infra/sql/03_create_tables.sql" && exit 1)
	@test -f infra/sql/04_add_FKs.sql || (echo "Missing file: infra/sql/04_add_FKs.sql" && exit 1)
	@test -f infra/sql/05_add_indexes.sql || (echo "Missing file: infra/sql/05_add_indexes.sql" && exit 1)
	@test -f infra/sql/06_create_staging.sql || (echo "Missing file: infra/sql/06_create_staging.sql" && exit 1)
	@test -f infra/sql/07_load_staging.sql || (echo "Missing file: infra/sql/07_load_staging.sql" && exit 1)
	@test -f infra/sql/08_load_tables.sql || (echo "Missing file: infra/sql/08_load_tables.sql" && exit 1)
	@test -f infra/sql/09_create_publication.sql || (echo "Missing file: infra/sql/09_create_publication.sql" && exit 1)
	@test -f infra/sql/10_prep_cdc.sql || (echo "Missing file: infra/sql/10_prep_cdc.sql" && exit 1)
	@test -f infra/sql/13_test_cdc.sql || (echo "Missing file: infra/sql/13_test_cdc.sql" && exit 1)
	@test -f infra/sql/14_test_schema_evolution.sql || (echo "Missing file: infra/sql/14_test_schema_evolution.sql" && exit 1)
	@test -f infra/bootstrap/16_polaris_bootstrap.sh || (echo "Missing file: infra/bootstrap/16_polaris_bootstrap.sh" && exit 1)

check-dataset:
	@test -d "$(DATASET_DIR)" || (echo "DATASET_DIR does not exist: $(DATASET_DIR)" && exit 1)
	@for file in $(REQUIRED_CSVS); do \
		test -f "$(DATASET_DIR)/$$file" || (echo "Missing dataset file: $(DATASET_DIR)/$$file" && exit 1); \
	done

init-db:
	@DB_USER="$(DB_USER)" DB_NAME="$(DB_NAME)" bash infra/bootstrap/01_init_db.sh

create-schema:
	$(PSQL_DB) -f infra/sql/02_create_schema.sql

create-tables:
	$(PSQL_DB) -f infra/sql/03_create_tables.sql

add-fks:
	$(PSQL_DB) -f infra/sql/04_add_FKs.sql

add-indexes:
	$(PSQL_DB) -f infra/sql/05_add_indexes.sql

create-staging:
	$(PSQL_DB) -f infra/sql/06_create_staging.sql

load-staging:
	@test -d "$(DATASET_DIR)" || (echo "DATASET_DIR does not exist: $(DATASET_DIR)" && exit 1)
	$(PSQL_DB) -v dataset_dir="$(DATASET_DIR)" -f infra/sql/07_load_staging.sql

load-tables:
	$(PSQL_DB) -f infra/sql/08_load_tables.sql

create-publication:
	$(PSQL_DB) -f infra/sql/09_create_publication.sql

prep-cdc:
	$(PSQL_DB) -f infra/sql/10_prep_cdc.sql

setup-postgres: check-tools check-sql check-dataset init-db create-schema create-tables add-fks add-indexes create-staging load-staging load-tables create-publication prep-cdc
	@echo "Postgres setup complete."

test-cdc:
	$(PSQL_DB) -f infra/sql/13_test_cdc.sql -f infra/sql/14_test_schema_evolution.sql

init-polaris:
	bash infra/bootstrap/16_polaris_bootstrap.sh