# Repo Improvement Plan (Team Lead Review)

## 1) Executive assessment

This repository has a strong foundation and demonstrates substantial end-to-end effort across CDC ingestion, lakehouse transformation, and analytics consumption paths. The biggest gap is **engineering maturity** (repeatability, testability, and operational robustness), not conceptual understanding.

Current strengths:
- Broad architecture coverage from OLTP → CDC → Kafka → Spark/Iceberg/Polaris → Trino/BI.
- Clear intent to separate bronze/silver/gold responsibilities.
- Existing reusable Python helpers and DQ modules.

Primary risks:
- Notebook-first orchestration makes production behavior hard to test and version.
- Data contracts and DQ enforcement are not yet centralized at Gold.
- CI is limited relative to repo size and complexity.
- Documentation is rich but fragmented for different audiences (developer/operator/consumer).

---

## 2) Target-state architecture (what “good” should look like)

Within this repository, we should evolve toward:

1. **Code-first pipeline runtime**
   - Notebooks remain for exploration only.
   - Production logic runs from Python entrypoints (`jobs/` or `pipelines/`) with explicit CLI args and config.

2. **Contract-driven medallion model**
   - Bronze: schema and ingestion fidelity.
   - Silver: standardization + row-level quality checks.
   - Gold: business contracts (uniqueness, referential integrity, SCD validity, freshness SLA).

3. **Single orchestration interface**
   - One command per stage and one command for end-to-end run.
   - Idempotent reruns using watermark/state metadata.

4. **Operationalized lakehouse maintenance**
   - Scheduled compaction, snapshot expiration, manifest rewrite, orphan cleanup.
   - Performance SLOs tracked for Trino-facing analytics tables.

---

## 3) Priority roadmap (first 6 weeks)

## Phase A — Foundation hardening (Week 1)

### A1. Standardize project structure
- Create clear top-level boundaries:
  - `src/` for reusable pipeline code
  - `jobs/` for executable batch jobs
  - `tests/` for unit/integration/contract checks
  - `docs/` with indexed navigation
- Move production logic out of notebooks into callable modules; keep notebooks thin wrappers.

### A2. Define configuration contract
- Consolidate YAML config into one typed schema (Pydantic/dataclass).
- Enforce required keys, defaults, and validation at startup.
- Add `dev`, `test`, `prod-local` profiles.

### A3. Enforce coding standards
- Add strict lint + formatting + import order + type checking in CI.
- Add pre-commit hooks for local consistency.

**Deliverable:** consistent module layout + passing style/type gates.

---

## Phase B — Data quality and correctness (Week 2)

### B1. Central Gold data contract layer
Implement shared contract checks for each Gold table:
- PK/unique constraints
- FK integrity to dimensions
- non-null critical fields
- business rule assertions (money/date/status validity)
- SCD2 interval overlap/current-row assertions

### B2. Fail-fast policy
- Define severity levels (`critical`, `warn`, `info`).
- Block publish on critical breaches.
- Persist all checks to `monitoring.dq_metrics` with run_id/table_name/stage.

### B3. Deterministic validation suite
- Build test command(s) that validate outputs in Spark and Trino.
- Include known-answer tests on small fixture slices.

**Deliverable:** measurable confidence before every release/demo.

---

## Phase C — Performance and scale readiness (Week 3)

### C1. Refactor repeated transformation logic
- Extract reusable utilities for:
  - SCD2 merge/application
  - temporal joins
  - incremental impacted-key expansion
  - surrogate key generation policy

### C2. Writer strategy framework
- Metadata-driven write mode selection:
  - `overwrite` for tiny static dimensions
  - `replace_by_key` for medium incremental tables
  - `merge_into` for large sparse-updated facts

### C3. Iceberg maintenance jobs
- Add recurring tasks for compaction/manifests/snapshots/orphans.
- Track maintenance KPIs (file count, avg file size, planning latency).

**Deliverable:** stable runtime and lower query latency/cost.

---

## Phase D — Operability and release discipline (Week 4)

### D1. Observability baseline
- Emit per-job metrics: status, duration, row deltas, watermark lag, DQ failures.
- Add alert rules for pipeline failure, stale Gold data, and critical DQ breaches.

### D2. Incident runbooks
- Document triage flows for common failures (connector, schema drift, late CDC, DQ fail).
- Add “first 15 minutes” checklist for on-call.

### D3. Release process
- Add versioned release notes and migration notes for schema-changing updates.
- Require green CI + contract suite before merge to main.

**Deliverable:** predictable operations and safer change management.

---

## Phase E — Consumer layer readiness (Weeks 5–6)

### E1. BI semantic contract
- Define canonical Gold marts and metric definitions (GMV, AOV, conversion, delivery lead time).
- Publish metric dictionary and grain definitions.

### E2. Query performance certification
- Benchmark top BI queries through Trino.
- Document SLO and tuning actions (partitioning/sorting/pre-aggregations).

### E3. Consumer-facing docs
- Separate guides by persona:
  - quickstart
  - contributor/developer
  - operator/on-call
  - BI analyst

**Deliverable:** handoff-ready analytics platform behavior.

---

## 4) Engineering standards I would enforce immediately

1. No business-critical transformation logic living only in notebooks.
2. Every Gold table must have explicit tests and contracts.
3. Every pipeline run must produce a run_id and auditable metrics.
4. No merge without passing lint, type checks, and contract tests.
5. Every production table change requires migration note + rollback strategy.

---

## 5) Concrete backlog (high impact, low regret)

1. Create `jobs/build_gold.py` CLI entrypoint using existing `notebooks/src` modules.
2. Add `tests/contracts/test_gold_contracts.py` with table-level assertions.
3. Add centralized `src/gold/contracts.py` and integrate into build flow.
4. Add Make targets:
   - `make test-unit`
   - `make test-contracts`
   - `make pipeline-e2e`
5. Add `docs/00_index.md` to unify documentation navigation.
6. Add CI stages for unit tests + contract checks + style/type gates.

---

## 6) Success criteria (definition of “team-lead quality”)

This repo reaches expected team quality when:
- A new engineer can run end-to-end pipeline in under 30 minutes from docs.
- Gold outputs are contract-validated and fail-fast on critical data issues.
- Pipeline executions are observable with actionable metrics and alerts.
- Trino-facing Gold tables meet documented query SLOs.
- All production logic is testable Python modules, not notebook-only code.

