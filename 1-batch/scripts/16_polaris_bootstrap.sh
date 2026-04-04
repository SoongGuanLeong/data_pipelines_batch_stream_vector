#!/usr/bin/env bash
set -euo pipefail

# IMPORTANT: This script is not PRODUCTION READY. It is intended for
# demonstration and learning purposes only. Do not use it as-is in a production
# environment.
# PROD READY would require advanced shell scripting.

# This script now also manages Spark Polaris credentials in spark-defaults.conf
# so credentials are not copied manually.

# ==============================================================
# Define variables
# ==============================================================
POLARIS_URL="${POLARIS_URL:-http://localhost:8181}"
CLIENT_ID="${POLARIS_ADMIN_CLIENT_ID:-admin}"
CLIENT_SECRET="${POLARIS_ADMIN_CLIENT_SECRET:-password123}"
SCOPE="${POLARIS_SCOPE:-PRINCIPAL_ROLE:ALL}"
CATALOG_NAME="${POLARIS_CATALOG_NAME:-learning_catalog}"
BUCKET="${POLARIS_BUCKET:-s3a://olist-ecommerce}"
REALM="${POLARIS_REALM:-POLARIS}"
PRINCIPAL_NAME="${POLARIS_PRINCIPAL_NAME:-spark_user}"
ROLE_NAME="${POLARIS_ROLE_NAME:-spark_role}"
CATALOG_ROLE="${POLARIS_CATALOG_ROLE:-catalog_admin}"
SPARK_DEFAULTS_PATH="${SPARK_DEFAULTS_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../docker/15_minio_spark_iceberg_polaris-postgres_kafka-connect/spark/conf" && pwd)/spark-defaults.conf}"

# ==============================================================
# Helpers
# ==============================================================
require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1"
    exit 1
  }
}

upsert_spark_credential() {
  local credential="$1"

  if [[ ! -f "$SPARK_DEFAULTS_PATH" ]]; then
    echo "WARNING: Spark defaults file not found at '$SPARK_DEFAULTS_PATH'."
    echo "Generated credential: $credential"
    return
  fi

  cp "$SPARK_DEFAULTS_PATH" "${SPARK_DEFAULTS_PATH}.bak"

  if grep -q '^spark\.sql\.catalog\.polaris\.credential' "$SPARK_DEFAULTS_PATH"; then
    sed -i "s|^spark\.sql\.catalog\.polaris\.credential.*$|spark.sql.catalog.polaris.credential   ${credential}|" "$SPARK_DEFAULTS_PATH"
  else
    printf '\n# Managed by 16_polaris_bootstrap.sh\nspark.sql.catalog.polaris.credential   %s\n' "$credential" >> "$SPARK_DEFAULTS_PATH"
  fi

  echo "==> Updated Spark credential in: $SPARK_DEFAULTS_PATH"
}

get_or_create_principal_credential() {
  local principal_name="$1"

  # Try to create a fresh client secret first (recommended because secret is returned once).
  local create_response
  create_response=$(curl -s -X POST "$POLARIS_URL/api/management/v1/principals/$principal_name/credentials" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -H "Polaris-Realm: $REALM" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{}') || true

  local created_id
  local created_secret
  created_id=$(echo "$create_response" | jq -r '.credentials[0].clientId // .credentials.clientId // .credential.clientId // .clientId // empty')
  created_secret=$(echo "$create_response" | jq -r '.credentials[0].clientSecret // .credentials.clientSecret // .credential.clientSecret // .clientSecret // empty')

  if [[ -n "$created_id" && -n "$created_secret" ]]; then
    echo "${created_id}:${created_secret}"
    return
  fi

  # Fallback: read current credentials endpoint (may not include secret depending on API behavior).
  local read_response
  read_response=$(curl -s -X GET "$POLARIS_URL/api/management/v1/principals/$principal_name/credentials" \
      -H "Accept: application/json" \
      -H "Polaris-Realm: $REALM" \
      -H "Authorization: Bearer $TOKEN")

  local read_id
  local read_secret
  read_id=$(echo "$read_response" | jq -r '.credentials[0].clientId // .credentials.clientId // .credential.clientId // .clientId // empty')
  read_secret=$(echo "$read_response" | jq -r '.credentials[0].clientSecret // .credentials.clientSecret // .credential.clientSecret // .clientSecret // empty')

  if [[ -n "$read_id" && -n "$read_secret" ]]; then
    echo "${read_id}:${read_secret}"
    return
  fi

  echo ""
}

require_command curl
require_command jq

# ==============================================================
# Request Access Token
# ==============================================================
echo "==> Obtaining OAuth2 token for Polaris API..."
TOKEN=$(curl -s -X POST "$POLARIS_URL/api/catalog/v1/oauth/tokens" \
    -H "Polaris-Realm: $REALM" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "client_id=$CLIENT_ID" \
    -d "client_secret=$CLIENT_SECRET" \
    -d "scope=$SCOPE" \
    | jq -r '.access_token'
)

if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "Failed to obtain OAuth token. Check admin client id/secret and Polaris availability."
  exit 1
fi

echo "==> Token obtained."

# ==============================================================
# Create Catalog
# ==============================================================
echo "==> Creating catalog: $CATALOG_NAME"
curl -s -X POST "$POLARIS_URL/api/management/v1/catalogs" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Polaris-Realm: $REALM" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF_JSON
{
  "catalog": {
    "name": "$CATALOG_NAME",
    "type": "INTERNAL",
    "storageConfigInfo": {
      "storageType": "S3",
      "allowedLocations": ["$BUCKET/"],
      "endpoint": "http://minio:9000",
      "endpointInternal": "http://minio:9000",
      "pathStyleAccess": true
    },
    "properties": {
      "default-base-location": "$BUCKET/"
    }
  }
}
EOF_JSON
echo "==> Catalog created (or already exists)"

# ==============================================================
# Create Principal
# ==============================================================
echo "==> Creating principal: $PRINCIPAL_NAME"
PRINCIPAL_CREATE_RESPONSE=$(curl -s -X POST "$POLARIS_URL/api/management/v1/principals" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Polaris-Realm: $REALM" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF_JSON
{
  "principal": {
    "name": "$PRINCIPAL_NAME"
  }
}
EOF_JSON
)
echo "$PRINCIPAL_CREATE_RESPONSE"
PRINCIPAL_CREATE_CREDENTIAL=$(echo "$PRINCIPAL_CREATE_RESPONSE" | jq -r '.credentials.clientId as $id | .credentials.clientSecret as $secret | if ($id and $secret) then "\($id):\($secret)" else "" end')
echo "==> Principal created (or already exists)"

# ==============================================================
# Create Principal Role
# ==============================================================
echo "==> Creating principal role: $ROLE_NAME"
curl -s -X POST "$POLARIS_URL/api/management/v1/principal-roles" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF_JSON
{
  "principalRole": {
    "name": "$ROLE_NAME"
  }
}
EOF_JSON
echo "==> Principal role created (or already exists)"

# ==============================================================
# Assign Principal Role to Principal
# ==============================================================
echo "==> Attaching role '$ROLE_NAME' to principal '$PRINCIPAL_NAME'"
curl -s -X PUT "$POLARIS_URL/api/management/v1/principals/$PRINCIPAL_NAME/principal-roles" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF_JSON
{
  "principalRole": {
    "name": "$ROLE_NAME"
  }
}
EOF_JSON
echo "==> Role attached to principal"

# ==============================================================
# Assign Catalog Role to Principal Role
# ==============================================================
echo "==> Granting catalog role '$CATALOG_ROLE' to role '$ROLE_NAME' on catalog '$CATALOG_NAME'"
curl -s -X PUT "$POLARIS_URL/api/management/v1/principal-roles/$ROLE_NAME/catalog-roles/$CATALOG_NAME" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF_JSON
{
  "catalogRole": {
    "name": "$CATALOG_ROLE"
  }
}
EOF_JSON
echo "==> Catalog role granted"

# ==============================================================
# List Catalog Role for Principal Role (to verify previous step)
# ==============================================================
echo "==> Verifying catalog roles for role '$ROLE_NAME' on catalog '$CATALOG_NAME'"
curl -s -X GET "$POLARIS_URL/api/management/v1/principal-roles/$ROLE_NAME/catalog-roles/$CATALOG_NAME" \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TOKEN"
echo "==> Verification complete"

# ==============================================================
# Generate / refresh principal credentials and sync to Spark config
# ==============================================================
echo "==> Generating Polaris client credentials for principal '$PRINCIPAL_NAME'"
POLARIS_SPARK_CREDENTIAL="${PRINCIPAL_CREATE_CREDENTIAL:-}"

if [[ -z "$POLARIS_SPARK_CREDENTIAL" ]]; then
  POLARIS_SPARK_CREDENTIAL=$(get_or_create_principal_credential "$PRINCIPAL_NAME")
fi

if [[ -z "$POLARIS_SPARK_CREDENTIAL" ]]; then
  echo "WARNING: Could not retrieve Polaris principal client_id/client_secret via API."
  echo "Please create principal credentials in Polaris UI/API and update spark-defaults.conf manually."
  exit 0
fi

upsert_spark_credential "$POLARIS_SPARK_CREDENTIAL"
echo "==> Credential sync done. Restart Spark container to apply changes."