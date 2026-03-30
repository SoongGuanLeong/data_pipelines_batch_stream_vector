# SCD Type 2 Implementation Strategies in a Lakehouse

## Overview

Slowly Changing Dimension Type 2 (SCD2) is used to track historical changes in dimensional data by maintaining versioned records with:

* `effective_from`
* `effective_to`
* `is_current`

In a modern lakehouse (Spark + Iceberg), there are **two primary implementation strategies**:

1. **Stateless Recompute (Full / Selective Rebuild)**
2. **Stateful Incremental (MERGE-based)**

This document explains their differences, tradeoffs, and when to use each.

---

# 1. Approach A — Stateless Recompute

## Concept

Rebuild the SCD2 table entirely (or partially) from the source-of-truth (Silver layer):

```python
gold = f(silver)
```

No dependency on previous Gold state.

---

## Variants

### 1. Full Rebuild

* Scan entire Silver table
* Recompute full SCD2
* Overwrite Gold

### 2. Selective Rebuild (Recommended)

* Identify changed business keys (e.g. `customer_id`)
* Recompute SCD2 **only for those keys**
* Overwrite affected portion in Gold

---

## Characteristics

| Aspect       | Behavior             |
| ------------ | -------------------- |
| Idempotency  | ✅ Always             |
| State-free   | ✅ Yes                |
| Reproducible | ✅ Deterministic      |
| Complexity   | ✅ Low–Medium         |
| Performance  | ❌ Expensive at scale |

---

## Strengths

* Simple mental model
* Easy to debug and test
* Backfill-safe (late data handled naturally)
* No risk of historical corruption

---

## Weaknesses

* High compute cost for large datasets
* Rewrites unchanged data
* Higher latency

---

## Example Pattern

```python
changed_keys = (
    spark.read.table("silver.customers")
    .where("ds >= last_run_ds")
    .select("customer_id")
    .distinct()
)

df = (
    spark.read.table("silver.customers")
    .join(changed_keys, "customer_id")
)

# apply SCD2 logic (window + lead)
```

---

# 2. Approach B — Stateful MERGE

## Concept

Incrementally update the existing Gold table using new data:

```sql
MERGE INTO gold_table t
USING updates s
ON t.customer_id = s.customer_id
```

Depends on the current state of Gold.

---

## Characteristics

| Aspect       | Behavior         |
| ------------ | ---------------- |
| Idempotency  | ❌ Not guaranteed |
| State-free   | ❌ No             |
| Reproducible | ❌ Hard           |
| Complexity   | ❌ High           |
| Performance  | ✅ Efficient      |

---

## Strengths

* Processes only new/changed data
* Lower compute cost
* Lower latency
* Scales to very large datasets

---

## Weaknesses

* Complex logic (especially SCD2 updates)
* Hard to debug
* Sensitive to data ordering issues
* Late-arriving data requires record rewrites
* Bugs can corrupt historical data

---

## Key Challenges

### 1. Late Arriving Data

Requires:

* reopening closed records
* shifting `effective_to`

---

### 2. Ordering Guarantees

Requires strict ordering using:

```text
cdc_ts + ingest_ts
```

---

### 3. State Dependency

* Output depends on previous runs
* Hard to recompute from scratch

---

# 3. Storage Layer Considerations

MERGE is **independent** of storage optimization.

Iceberg provides:

## Copy-on-Write (COW)

* Rewrites files on update
* Simpler reads
* Heavier writes

## Merge-on-Read (MOR)

* Writes deltas
* Requires compaction
* Faster writes, slightly slower reads

---

# 4. Key Differences

| Dimension     | Stateless Recompute | MERGE         |
| ------------- | ------------------- | ------------- |
| Logic model   | Functional          | Mutating      |
| Dependency    | Silver only         | Silver + Gold |
| Debuggability | Easy                | Hard          |
| Cost          | High                | Low           |
| Latency       | Higher              | Lower         |
| Safety        | High                | Medium–Low    |
| Complexity    | Low–Medium          | High          |

---

# 5. When to Use Which

## Use Stateless Recompute when:

* Dataset size is manageable
* You need strong correctness guarantees
* You expect backfills / late data
* You want simple, maintainable pipelines
* You are in early-stage or learning phase

---

## Use Selective Rebuild when:

* Data is growing
* Full rebuild is becoming slow
* You still want stateless guarantees

👉 Recommended default for most production systems

---

## Use MERGE when:

* Data is very large (100M–1B+ rows)
* Full rebuild exceeds SLA
* Near real-time processing is required
* Team can handle operational complexity

---

# 6. Recommended Evolution Path

```text
1. Full Rebuild
2. Selective Stateless Rebuild   ← Best balance
3. MERGE (if needed)
4. Add MOR + compaction (scale optimization)
```

---

# 7. Key Takeaway

The real tradeoff is:

```text
Stateless correctness vs Stateful efficiency
```

Best practice:

```text
Start stateless → optimize with selective recompute → adopt MERGE only when necessary
```

---

# 8. Practical Recommendation

For this project:

* Keep current **stateless SCD2**
* Upgrade to **selective recompute by business key**
* Avoid MERGE until scaling demands it

---

# End
