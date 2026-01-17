#!/usr/bin/env bash
set -euo pipefail

# IMPORTANT: This script is not PRODUCTION READY. It is intended for
# demonstration and learning purposes only. Do not use it as-is in a production
# environment.
# PROD READY would require advanced shell scripting.

# After running this script, copy CLIENT_ID and CLIENT_SECRET and put them into spark-defaults.conf

# ==============================================================
# Define variables
# ==============================================================
POLARIS_URL="http://localhost:8181"
CLIENT_ID="admin"
CLIENT_SECRET="password123"
SCOPE="PRINCIPAL_ROLE:ALL"
CATALOG_NAME="learning_catalog"
BUCKET="s3://olist-ecommerce"
REALM="POLARIS"
PRINCIPAL_NAME="spark_user"
ROLE_NAME="spark_role"
CATALOG_ROLE="catalog_admin"

# ==============================================================
# Request Access Token
# ==============================================================
echo "==> Obtaining OAuth2 token for Polaris API..."
TOKEN=$(curl -s -X POST "$POLARIS_URL/api/catalog/v1/oauth/tokens" \
    -H "Polaris-Realm: POLARIS" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "client_id=$CLIENT_ID" \
    -d "client_secret=$CLIENT_SECRET" \
    -d "scope=$SCOPE" \
    | jq -r '.access_token'
)
echo "==> Token obtained."

# ==============================================================
# Create Catalog
# ==============================================================
echo "==> Creating catalog: $CATALOG_NAME"
curl -s -X POST "$POLARIS_URL/api/management/v1/catalogs" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Polaris-Realm: POLARIS" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF
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
EOF
echo "==> Catalog created (or already exists)"

# ==============================================================
# Create Principal
# ==============================================================
echo "==> Creating principal: $PRINCIPAL_NAME"
curl -s -X POST "$POLARIS_URL/api/management/v1/principals" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Polaris-Realm: $REALM" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF
{
  "principal": {
    "name": "$PRINCIPAL_NAME"
  }
}
EOF
echo "==> Principal created (or already exists)"

# ==============================================================
# Create Principal Role
# ==============================================================
echo "==> Creating principal role: $ROLE_NAME"
curl -s -X POST "$POLARIS_URL/api/management/v1/principal-roles" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF
{
  "principalRole": {
    "name": "$ROLE_NAME"
  }
}
EOF
echo "==> Principal role created (or already exists)"

# ==============================================================
# Assign Principal Role to Principal
# ==============================================================
echo "==> Attaching role '$ROLE_NAME' to principal '$PRINCIPAL_NAME'"
curl -s -X PUT "$POLARIS_URL/api/management/v1/principals/$PRINCIPAL_NAME/principal-roles" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF
{
  "principalRole": {
    "name": "$ROLE_NAME"
  }
}
EOF
echo "==> Role attached to principal"

# ==============================================================
# Assign Catalog Role to Principal Role
# ==============================================================
echo "==> Granting catalog role '$CATALOG_ROLE' to role '$ROLE_NAME' on catalog '$CATALOG_NAME'"
curl -s -X PUT "$POLARIS_URL/api/management/v1/principal-roles/$ROLE_NAME/catalog-roles/$CATALOG_NAME" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d @- <<EOF
{
  "catalogRole": {
    "name": "$CATALOG_ROLE"
  }
}
EOF
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
# Save Polaris credentials for Spark - not working (removed)
# ==============================================================
# echo "==> Saving Polaris credentials to $SHARED/polaris.env"

# POLARIS_CLIENT_ID=$(curl -s -X GET "$POLARIS_URL/api/management/v1/principals/$PRINCIPAL_NAME" \
#     -H "Authorization: Bearer $TOKEN" \
#     | grep -oP '"clientId"\s*:\s*"\K[^"]+')

# POLARIS_CLIENT_SECRET=$(curl -s -X GET "$POLARIS_URL/api/management/v1/principals/$PRINCIPAL_NAME/credentials" \
#     -H "Authorization: Bearer $TOKEN" \
#     | grep -oP '"clientSecret"\s*:\s*"\K[^"]+')

# cat > "$SHARED/polaris.env" <<EOF
# POLARIS_CLIENT_ID=$POLARIS_CLIENT_ID
# POLARIS_CLIENT_SECRET=$POLARIS_CLIENT_SECRET
# EOF

# echo "==> Polaris credentials written to $SHARED/polaris.env"
