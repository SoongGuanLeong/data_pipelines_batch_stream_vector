#!/usr/bin/env bash

# exit immediately if any command fails
set -e

DB_NAME="olist"
DB_USER="postgres"

# Create the database if it does not exist
psql -U "${DB_USER}" -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" \
| grep -q 1 || psql -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME}"