# Service Config Ownership Plan (Spark, Polaris, and future Trino)

This file clarifies **who owns which settings** so we avoid Spark/Trino overlap and credential confusion.

## Why this exists

Spark and Trino both talk to Polaris + MinIO and can use similar Iceberg settings. When these settings are mixed in one place, it is hard to tell which service should be changed.

## Ownership matrix

| Area | Owner | Source of truth | Notes |
|---|---|---|---|
| Spark runtime and Spark SQL tuning | Spark service | `spark/conf/spark-defaults.conf` | Spark-only keys (`spark.*`) stay here. |
| Polaris bootstrap admin credential | Polaris service | `docker-compose.yaml` env (`POLARIS_BOOTSTRAP_CREDENTIALS`) | Used to get admin token for API setup. |
| Spark principal + client secret for Polaris | Polaris API + bootstrap script | `scripts/16_polaris_bootstrap.sh` updates `spark-defaults.conf` | Script creates/refreshes principal credential and writes `spark.sql.catalog.polaris.credential`. |
| Trino Iceberg/REST catalog settings | Trino service | `trino/etc/catalog/*.properties` (when enabled) | Do **not** put Trino keys into Spark defaults. |
| Shared storage endpoint and bucket naming | Platform/infrastructure | `docker-compose.yaml` + service catalog configs | Keep endpoint/bucket values aligned across services, but each service config owns its own keys. |

## Rules to avoid confusion

1. `spark-defaults.conf` may only contain Spark keys (`spark.*`).
2. Trino catalog keys belong in Trino files only (`connector.name`, `iceberg.*`, etc.).
3. Polaris principal credential used by Spark is managed by `16_polaris_bootstrap.sh`, not manual copy/paste.
4. If a value appears in both Spark and Trino (for example URI or S3 endpoint), treat it as a **shared semantic value** with **service-local config ownership**.

## Polaris credential recovery flow (Spark)

1. Start stack with Polaris healthy.
2. Run:
   ```bash
   bash 1-batch/scripts/16_polaris_bootstrap.sh
   ```
3. Script will:
   - create/verify catalog, principal, and roles,
   - generate or read principal credentials,
   - update `spark.sql.catalog.polaris.credential` in `spark-defaults.conf`.
4. Restart Spark container.

## Pre-Trino enablement checklist

- Keep current Spark Polaris catalog name (`polaris`) stable.
- Add Trino config under `trino/etc` with an explicit catalog name (for example `polaris`).
- Verify both Spark and Trino point to the same Polaris REST base and warehouse semantics.
- Do not reuse Spark config files for Trino settings.
