#!/usr/bin/env bash

# IMPORTANT: This script is not PRODUCTION READY. It is intended for
# demonstration and learning purposes only. Do not use it as-is in a production
# environment.
# PROD READY would require advanced shell scripting.

# -e: exit immediately on error
# -u: error on undefined variables
# -o pipefail: fail if any command in a pipeline fails
set -euo pipefail

CONNECT_URL="http://localhost:8083"
CONNECTOR_NAME="olist-postgres"
CONNECTOR_CONFIG="olist-postgres-connector.json"

# curl -s: silent
# -f: fail on HTTP error
# >/dev/null: discard output
echo "==> Checking Debezium Connect availability..."
until curl -sf "$CONNECT_URL/" >/dev/null; do
  echo "Debezium Connect not ready, retrying..."
  sleep 3
done
echo "Debezium Connect is up."

# for idempotency: delete if exists
# -X: explicit HTTP method (POST / GET / PUT)
echo "==> Removing existing connector if present..."
curl -sf -X DELETE "$CONNECT_URL/connectors/$CONNECTOR_NAME" || true

# -H: HTTP header
# -d: data
# @: get content from file
echo "==> Creating Debezium connector..."
curl -sf -X POST "$CONNECT_URL/connectors" \
  -H "Content-Type: application/json" \
  -d @"$CONNECTOR_CONFIG"

echo "==> Waiting for connector to start..."
sleep 5

# jq: Pipes to jq for readable JSON
echo "==> Verifying connector status..."
curl -sf "$CONNECT_URL/connectors/$CONNECTOR_NAME/status" | jq .

echo "==> Debezium connector deployed successfully."
