#!/usr/bin/env bash
set -euo pipefail

CONNECT_URL="http://localhost:8083"
CONNECTOR_NAME="olist-postgres"
CONNECTOR_CONFIG="olist-postgres-connector.json"

echo "==> Checking Kafka Connect availability..."
until curl -sf "$CONNECT_URL/" >/dev/null; do
  echo "Kafka Connect not ready, retrying..."
  sleep 3
done
echo "Kafka Connect is up."

echo "==> Removing existing connector if present..."
curl -sf -X DELETE "$CONNECT_URL/connectors/$CONNECTOR_NAME" || true

echo "==> Creating Debezium connector..."
curl -sf -X POST "$CONNECT_URL/connectors" \
  -H "Content-Type: application/json" \
  -d @"$CONNECTOR_CONFIG"

echo "==> Waiting for connector to start..."
sleep 5

echo "==> Verifying connector status..."
curl -sf "$CONNECT_URL/connectors/$CONNECTOR_NAME/status" | jq .

echo "==> Debezium connector deployed successfully."
