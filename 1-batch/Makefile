SHELL := /usr/bin/env bash

# Local PostgreSQL defaults (override on command line if needed)
DB_USER ?= postgres
DB_NAME ?= olist
DB_HOST ?= localhost
DB_PORT ?= 5432

# Folder that contains olist_*.csv files
DATASET_DIR ?= $(CURDIR)/docker/datasets

PSQL ?= psql
PSQL_ADMIN := $(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER)
PSQL_DB := $(PSQL_ADMIN) -d $(DB_NAME)

.PHONY: help init-db create-schema create-tables add-fk add-indexes create-staging load-staging load-oltp create-publication setup-all check-cdc prep-cdc

help:
	@echo "Available targets:"
	@echo "  init-db            - Create database $(DB_NAME) if it does not exist"
	@echo "  create-schema      - Create OLTP schema"
	@echo "  create-tables      - Create OLTP tables"
	@echo "  add-fks             - Add foreign keys"
	@echo "  add-indexes        - Add performance indexes"
	@echo "  create-staging     - Create staging schema and tables"
	@echo "  load-staging       - Load CSV files from DATASET_DIR into staging"
	@echo "  load-tables          - Load OLTP tables from staging"
	@echo "  create-publication - Create Debezium publication"
	@echo "  setup-all          - Run full setup in correct order"
	@echo ""
	@echo "Variables (override like: make setup-all DB_USER=postgres DATASET_DIR=/path/to/csvs):"
	@echo "  DB_USER, DB_NAME, DB_HOST, DB_PORT, DATASET_DIR, PSQL"

init-db:
	@DB_USER="$(DB_USER)" DB_NAME="$(DB_NAME)" $(SHELL) scripts/01_init_db.sh

create-schema:
	$(PSQL_DB) -f scripts/02_create_schema.sql

create-tables:
	$(PSQL_DB) -f scripts/03_create_tables.sql

add-fks:
	$(PSQL_DB) -f scripts/04_add_FKs.sql

add-indexes:
	$(PSQL_DB) -f scripts/05_add_indexes.sql

create-staging:
	$(PSQL_DB) -f scripts/06_create_staging.sql

load-staging:
	@test -d "$(DATASET_DIR)" || (echo "DATASET_DIR does not exist: $(DATASET_DIR)" && exit 1)
	$(PSQL_DB) -v dataset_dir="$(DATASET_DIR)" -f scripts/07_load_staging.sql

load-tables:
	$(PSQL_DB) -f scripts/08_load_tables.sql

create-publication:
	$(PSQL_DB) -f scripts/09_create_publication.sql

prep-cdc:
	$(PSQL_DB) -f scripts/10_prep_cdc.sql

test-cdc:
	$(PSQL_DB) -f scripts/13_test_cdc.sql -f scripts/14_test_schema_evolution.sql

setup-all: init-db create-schema create-tables add-fks add-indexes create-staging load-staging load-tables
	@echo "Setup complete. Next: make create-publication"