# Project Completion Roadmap (Batch → BI Ready)

This roadmap is designed for the **final 2–6 weeks** of the project and prioritizes what will create the biggest quality gain with the lowest delivery risk.

## Current state (based on repository review)

- The batch lakehouse stack is already substantial: Postgres CDC → Kafka/Apicurio → Spark → Iceberg/Polaris with Trino wired in compose.  
- Silver-level DQ and reusable helpers already exist (`src/silver/dq`, `src/monitoring/dq_metrics.py`), but Gold quality controls are still mostly table-local validation helpers and not a centralized contract layer.  
- There is partial modularization in Python modules under `notebooks/src`, but there is still repeated SCD2 and incremental-impact logic in Gold dims/facts that can be standardized further.  
- CI currently checks Python lint/syntax only; there is no reproducible end-to-end data contract suite (especially for Trino/DBeaver-facing analytics tables).

---

## Recommended execution order (best course of action)

## Phase 1 — Stabilize and simplify core pipeline code (Week 1)

### 1) Remove repeated transformation patterns first

Create a shared utility module for:
- SCD2 window application (`effective_from`, `effective_to`, `is_current`, surrogate key pattern)
- temporal join helper (fact timestamp between dim validity range)
- impacted-key expansion logic used by incremental fact rebuilds

**Why now:** this gives immediate readability gains and reduces bug surface before adding new features.

**Definition of done:**
- Dim/fact modules call common utilities instead of re-implementing similar logic.
- Gold builders become declarative (what to join) instead of procedural (how each join is written).

### 2) Formalize writer strategy selection

You already have `overwrite_table`, `replace_by_key`, and `merge_into`. Add a strategy selector driven by table metadata/config (size, update frequency, key cardinality):

- default: `replace_by_key` for medium tables
- switch to `merge_into` for very large partitioned facts with sparse updates
- keep full overwrite for tiny dimensions

**Definition of done:**
- A single entrypoint decides write mode per table.
- Runbook includes “when to switch to MERGE”.

---

## Phase 2 — Gold DQ contracts and pipeline completeness (Week 1–2)

### 3) Add centralized Gold DQ checks (not just per-table helper metrics)

Add a `gold/dq/` module and enforce checks after each gold table build:

1. **Uniqueness**
   - `fact_orders`: unique `order_id`
   - `fact_order_items`: unique (`order_id`, `order_item_id`)

2. **Referential integrity**
   - no null surrogate keys when business keys are present
   - orphan-rate check against dimensions

3. **Business rules**
   - non-negative money fields (`price`, `freight_value`, `payment_value`)
   - status/date consistency checks (`delivered` implies delivered date)

4. **Freshness + volume anomalies**
   - row count deviation threshold vs trailing 7-day avg
   - max `cdc_ts` freshness SLA

5. **SCD2 validity checks** for dimensions used by facts
   - no overlapping intervals
   - single current row per business key

Persist these metrics to `monitoring.dq_metrics` with `pipeline_stage='gold'` and fail the job on critical breaches.

### 4) Add a deterministic end-to-end validation suite

Create a lightweight validation command set that can be run locally before demos:

- Spark SQL checks against Polaris tables
- Trino SQL checks (same assertions through Trino endpoint)
- optional seed-based “known answer” tests for curated sample slices

**Definition of done:**
- One command runs sanity checks from Bronze→Silver→Gold.
- Same checks pass from Trino (what BI users hit), not only Spark.

---

## Phase 3 — Performance and scalability hardening (Week 2–3)

### 5) Trino + DBeaver readiness checklist

Before Power BI, verify BI query path with DBeaver to Trino:

- published connection profile (host/port/catalog/schema)
- benchmark queries (top 10 dashboard queries) with timing baselines
- partition pruning evidence (`EXPLAIN` plans saved in docs)
- selective materialized views or pre-aggregated marts if latency misses SLA

Target pragmatic SLA:
- P95 interactive query < 5 seconds for dashboard filters
- heavy ad hoc query < 30 seconds

### 6) Iceberg maintenance workflow (scheduled)

Add scheduled maintenance jobs:

- `rewrite_data_files` (compact small files)
- `rewrite_manifests`
- `expire_snapshots`
- `remove_orphan_files`

Run frequency by table tier:
- hot facts: daily compaction + weekly manifest rewrite
- dims: weekly compaction + snapshot retention policy

Track table health KPIs:
- average file size
- manifests per table
- planning time / scan bytes in Trino

---

## Phase 4 — BI semantic layer and dashboard delivery (Week 3–4)

### 7) Power BI model-first approach

Build a semantic model on Gold star schema:

- relationships: dimensions → facts (single direction)
- DAX measures: GMV, AOV, order count, repeat customers, delivery lead time
- role-playing date handling (purchase vs delivered date)

Recommended delivery artifacts:
- `docs/bi/powerbi_model.md` (tables, relationships, grain)
- `docs/bi/dax_measures.md` (canonical measure definitions)
- `docs/bi/dashboard_spec.md` (pages, visuals, filters, owners)

### 8) Publish dashboard reliability requirements

- refresh schedule + expected runtime
- data freshness watermark shown on dashboard
- “data quality status” card (reads from dq_metrics)

---

## Phase 5 — Documentation and repo UX cleanup (Week 4)

### 9) Reorganize docs for discoverability

Create a single navigation index with explicit reader paths:

- **Quickstart path** (run locally)
- **Developer path** (code structure + pipeline logic)
- **Operator path** (runbooks, DQ failures, maintenance)
- **BI consumer path** (Trino/DBeaver/Power BI)

Minimum structure:
- `docs/01_quickstart.md`
- `docs/02_architecture.md`
- `docs/03_pipeline_contracts.md`
- `docs/04_operations_runbook.md`
- `docs/05_bi_guide.md`

### 10) Add clear “project status and next milestones” section to README

Include:
- what is production-ready
- what is experimental
- what is planned next (with dates)

This prevents readers from getting lost and sets expectations correctly.

---

## Phase 6 — Data services and governance integrations (Week 4–6)

### 11) Monitoring/alerting (Datadog or open-source equivalent)

At minimum emit:
- pipeline run status + duration
- DQ critical failure count
- watermark lag per table
- compaction job outcomes

Alert tiers:
- P1: pipeline failure or stale Gold > SLA
- P2: DQ critical breach
- P3: performance degradation trend

### 12) Metadata and lineage (DataHub/OpenMetadata)

Start with automated ingestion from:
- Iceberg/Trino metadata
- Spark job metadata
- DQ metrics tables

Outcome:
- searchable dataset catalog
- lineage graph for fact tables
- ownership + glossary tags

---

## Prioritized backlog (if you can only do 6 things)

1. Refactor repeated SCD2/incremental logic into shared utilities.
2. Implement Gold DQ contracts with fail-fast thresholds.
3. Add Spark + Trino end-to-end validation command suite.
4. Introduce scheduled Iceberg maintenance jobs.
5. Deliver Power BI semantic model + dashboard spec.
6. Rework docs navigation and README status section.

---

## Suggested acceptance criteria for “project complete”

You can declare the project complete when all are true:

- reproducible local runbook from raw load to dashboard refresh
- Gold DQ checks running and enforcing thresholds automatically
- Trino/DBeaver query SLA documented and met on benchmark set
- Iceberg maintenance scheduled with measurable table-health improvements
- dashboard definitions versioned and understandable by a new contributor
- docs lead first-time readers to success in under 30 minutes
