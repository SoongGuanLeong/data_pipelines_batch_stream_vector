# Stage A1 Execution: File Placement Map

This document defines **where each existing file category should go** as we execute Stage A1 (project structure standardization).

> Scope: This is a migration map first (safe planning). We can move files in small PR batches after this map is agreed.

---

## 1) Target top-level layout

```text
.
├── README.md
├── Makefile
├── src/
│   └── pipelines/
│       └── batch/
├── jobs/
│   └── batch/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contracts/
├── configs/
│   └── batch/
├── notebooks/
│   └── batch/
├── infra/
│   ├── docker/
│   ├── sql/
│   ├── connectors/
│   ├── bootstrap/
│   └── observability/
├── docs/
│   ├── 00_index.md
│   ├── architecture/
│   ├── operations/
│   ├── quality/
│   └── bi/
└── data/
    └── raw/
        └── olist/
```

---

## 2) Exact mapping from current repo


## 2.1 Reasoning behind the mapping decisions

The placement choices are based on separation of concerns and operational safety:

- **`src/` for production code**: pipeline logic must be importable, testable, and independent of notebook runtime side effects.
- **`jobs/` for execution entrypoints**: orchestration scripts should be explicit about args/config and callable by CI/cron/orchestrators.
- **`notebooks/` for exploration only**: notebooks are valuable for discovery but are weak as production interfaces (hard diffing, hidden state).
- **`configs/` centralized**: avoids config drift and makes environment promotion (`dev` → `test` → `prod-local`) deterministic.
- **`infra/` boundary**: keeps Docker, SQL bootstrap, and connectors together so infra changes are reviewed as one concern.
- **`docs/` persona-friendly navigation**: architecture/ops/quality/BI docs should be discoverable without knowing historical folder names.
- **`data/raw/olist` path**: explicit dataset location improves reproducibility and simplifies Make/CI dataset path configuration.

This structure mirrors common production data-platform repos: code and tests at the center, infra alongside, notebooks at the edge.

---

## A. Root files

- `README.md` → keep at root (entry point).
- `ETL_pipeline.png` → `docs/architecture/images/ETL_pipeline.png`.
- `completion_roadmap.md` → `docs/architecture/legacy/completion_roadmap.md`.
- `project_stats.md` → `docs/architecture/legacy/project_stats.md`.
- `improvement_plan_team_lead.md` → `docs/architecture/improvement_plan_team_lead.md`.

## B. Batch docs and diagrams

- `1-batch/docs/architecture/**` → `docs/architecture/**`.
- `1-batch/docs/schema/**` → `docs/architecture/schema/**`.
- `1-batch/docs/connectors/**` → `docs/operations/connectors/**`.
- `1-batch/docs/polaris/**` → `docs/operations/polaris/**`.
- `1-batch/spark_pipeline_checklist.md` → `docs/operations/spark_pipeline_checklist.md`.

## C. SQL + bootstrap scripts

- `1-batch/scripts/*.sql` → `infra/sql/*.sql`.
- `1-batch/scripts/01_init_db.sh` → `infra/bootstrap/init_db.sh`.
- `1-batch/scripts/16_polaris_bootstrap.sh` → `infra/bootstrap/polaris_bootstrap.sh`.
- `1-batch/scripts/*.md` → `docs/operations/runbooks/*.md`.
- `1-batch/scripts/16_polaris_bootstrap.sh.bak` → remove (or archive under `docs/architecture/legacy/`).

## D. Connector assets

- `1-batch/connectors/*.json` → `infra/connectors/*.json`.
- `1-batch/connectors/deploy_connector.sh` → `infra/connectors/deploy_connector.sh`.

## E. Docker and infra manifests

- `1-batch/docker/11_debezium_kafka_apicurio_akhq/docker-compose.yaml` → `infra/docker/cdc_stack/docker-compose.yaml`.
- `1-batch/docker/15_minio_spark_iceberg_polaris-postgres_kafka-connect/docker-compose.yaml` → `infra/docker/lakehouse_stack/docker-compose.yaml`.
- `1-batch/docker/ELK_stack_logging_monitoring/docker-compose.yaml` → `infra/observability/elk/docker-compose.yaml`.
- `1-batch/docker/ELK_stack_logging_monitoring/filebeat/filebeat.yml` → `infra/observability/elk/filebeat/filebeat.yml`.
- `1-batch/docker/ELK_stack_logging_monitoring/logstash/pipeline/logstash.conf` → `infra/observability/elk/logstash/pipeline/logstash.conf`.
- `1-batch/docker/15_*/spark/**` → `infra/docker/lakehouse_stack/spark/**`.
- `1-batch/docker/15_*/trino/**` → `infra/docker/lakehouse_stack/trino/**`.

## F. Python transformation code (production modules)

- `1-batch/docker/15_*/notebooks/src/**` → `src/pipelines/batch/**`.
  - `.../src/silver/**` → `src/pipelines/batch/silver/**`.
  - `.../src/gold/**` → `src/pipelines/batch/gold/**`.
  - shared helpers (`writers.py`, `watermark.py`, etc.) → `src/pipelines/batch/common/**`.

## G. Notebooks (exploration / demo only)

- `1-batch/docker/15_*/notebooks/*.ipynb` → `notebooks/batch/*.ipynb`.
- Notebook-specific utility snippets that are not production-grade should stay notebook-local or migrate to `notebooks/batch/_utils/`.

## H. Runtime configs

- `1-batch/docker/15_*/notebooks/configs/*.yaml` → `configs/batch/*.yaml`.

## I. Dataset files

- `1-batch/docker/datasets/*.csv` → `data/raw/olist/*.csv`.

## J. Build and task entrypoints

- `1-batch/Makefile` → root `Makefile` (single command surface).
- Add job entrypoints under `jobs/batch/`:
  - `jobs/batch/build_bronze.py`
  - `jobs/batch/build_silver.py`
  - `jobs/batch/build_gold.py`
  - `jobs/batch/run_e2e.py`

---

## 3) What should NOT move in the first migration PR

To reduce breakage, keep these in place temporarily and move later:

1. All `.ipynb` files (first, create wrappers; move notebooks afterward).
2. Docker compose paths referenced by existing docs (move docs and compose in same PR).
3. Large CSV data files (optional move; can remain and be symlinked or referenced by env var).

---

## 4) Recommended migration sequence (safe order)

1. Create new top-level folders and copy docs (no code-path changes yet).
2. Move configs + Python modules; add compatibility import shims.
3. Add `jobs/batch/*` CLI entrypoints that call moved modules.
4. Update Makefile and CI paths.
5. Move infra/docker and connector files.
6. Move notebooks and remove old paths.

---

## 5) Definition of done for Stage A1

- All production Python is importable from `src/pipelines/batch`.
- All executable runs start from `jobs/batch` or `Makefile`.
- Configs are loaded from `configs/batch`.
- Infra artifacts are under `infra/`.
- Docs point only to new paths (no stale references).
