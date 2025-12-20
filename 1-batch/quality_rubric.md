# Data Pipeline Quality Rubric (2025)

This document is a **final checklist and self‑assessment rubric** for the project:

**PostgreSQL → Debezium → Kafka → Spark → Iceberg → BI / AI**

Use this as:

* A README section
* An interview talking point
* A gap‑analysis tool before calling the project "done"

---

## 1. Correctness & Data Integrity

**Goal:** No lost, duplicated, or corrupted data

**How this project satisfies it**

* OLTP tables have clear primary keys
* CDC captures INSERT / UPDATE / DELETE via WAL
* Iceberg tables use deterministic upsert keys

**Evidence to show**

* Row count comparisons (Postgres vs Iceberg)
* Delete propagation demo

**Status:** ⬜ / ⚠️ / ✅

---

## 2. Idempotency

**Goal:** Safe re‑runs with no manual cleanup

**How this project satisfies it**

* Debezium offsets stored in Kafka
* Spark jobs write via MERGE / upsert
* Table creation and indexes are IF NOT EXISTS

**Evidence to show**

* Re‑run Spark job → no data change

**Status:** ⬜ / ⚠️ / ✅

---

## 3. Observability

**Goal:** Failures are obvious and explainable

**How this project satisfies it**

* Kafka consumer lag visible
* Spark job logs expose row counts
* Clear separation of stages (OLTP / CDC / Batch)

**Evidence to show**

* Screenshot of Kafka lag
* Spark logs with counts

**Status:** ⬜ / ⚠️ / ✅

---

## 4. Schema Evolution Safety

**Goal:** Schema changes do not silently break pipelines

**How this project satisfies it**

* Schema Registry enforces compatibility
* Iceberg supports schema evolution
* No hardcoded column ordering

**Evidence to show**

* Add nullable column → pipeline still runs

**Status:** ⬜ / ⚠️ / ✅

---

## 5. Backfill & Replayability

**Goal:** Ability to rebuild downstream state

**How this project satisfies it**

* Kafka topics are replayable
* Spark can rebuild Iceberg tables
* OLTP snapshot mode supported

**Evidence to show**

* Drop Iceberg table → rebuild from Kafka

**Status:** ⬜ / ⚠️ / ✅

---

## 6. Performance & Scalability

**Goal:** Predictable performance as data grows

**How this project satisfies it**

* Log‑based CDC (no polling)
* FK indexes added for CDC safety
* Columnar Iceberg storage

**Evidence to show**

* No sequential scans on CDC replay

**Status:** ⬜ / ⚠️ / ✅

---

## 7. Fault Tolerance

**Goal:** Failures do not corrupt data

**How this project satisfies it**

* Kafka provides buffering
* Spark jobs restartable
* No side effects before commit

**Evidence to show**

* Kill Spark mid‑run → restart successfully

**Status:** ⬜ / ⚠️ / ✅

---

## 8. Clear Layering

**Goal:** Each layer has one responsibility

**Layers in this project**

* OLTP: Source of truth
* Kafka: Change transport
* Iceberg Bronze: Raw CDC
* Iceberg Silver: Cleaned tables
* Iceberg Gold: Business models

**Status:** ⬜ / ⚠️ / ✅

---

## 9. Minimal Coupling

**Goal:** Components can be swapped

**How this project satisfies it**

* Spark compute decoupled from storage
* Iceberg decoupled from engine
* Kafka decouples producers/consumers

**Swap examples**

* Spark → DuckDB
* Kafka → Pub/Sub

**Status:** ⬜ / ⚠️ / ✅

---

## 10. Deterministic Semantics

**Goal:** Same input → same output

**How this project satisfies it**

* Deterministic primary keys
* Explicit timezones
* No non‑deterministic windowing

**Status:** ⬜ / ⚠️ / ✅

---

## 11. Data Lineage & Documentation

**Goal:** Anyone can understand the pipeline

**How this project satisfies it**

* Mermaid ER diagram
* Clear table naming
* This rubric

**Status:** ⬜ / ⚠️ / ✅

---

## 12. Operational Simplicity

**Goal:** Easy to run and debug

**How this project satisfies it**

* Local‑first setup (Docker / MinIO)
* No cloud lock‑in
* Few moving parts

**Status:** ⬜ / ⚠️ / ✅

---

## 13. Cost Awareness

**Goal:** No unnecessary compute or storage

**How this project satisfies it**

* Columnar formats
* Incremental processing
* No full table recompute

**Status:** ⬜ / ⚠️ / ✅

---

## 14. Security (Basic)

**Goal:** Not reckless

**How this project satisfies it**

* No secrets in code
* Read‑only CDC access
* Controlled write paths

**Status:** ⬜ / ⚠️ / ✅

---

## 15. Replaceability (Senior Engineer Test)

**Goal:** Architecture survives tool changes

**Assessment**

* Storage independent of compute
* CDC independent of sink
* Open formats used

**Status:** ⬜ / ⚠️ / ✅

---

## Final Self‑Assessment

| Area          | Status |
| ------------- | ------ |
| Correctness   |        |
| Idempotency   |        |
| Observability |        |
| Replayability |        |
| Scalability   |        |
| Documentation |        |

---

**If most boxes are ✅, this is a real data engineering project — not a tutorial.**
