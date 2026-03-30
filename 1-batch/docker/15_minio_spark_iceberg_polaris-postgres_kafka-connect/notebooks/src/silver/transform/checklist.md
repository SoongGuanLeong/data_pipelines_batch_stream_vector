# Transformation Checklist
If you are very pro you can try to build one notebook that can do all the different transformations in one go without any human checking. Note that such attempt is hard and prone to error in production.

But for now I'll just stick to:
- writing common codes into silver notebook
- the table-specific transformations into different python files

---

## **1️⃣ String / Categorical Columns**

**Typical columns:** IDs, names, cities, states, categories, free-text titles

**Common transformations / checks:**

* **Trim whitespace** → remove accidental leading/trailing spaces (`trim()`)
* **Null check** → drop or flag rows where mandatory keys are missing
* **Max length / character validation (optional)** → avoid very long strings or illegal characters
* **Optional case standardization** → e.g., uppercase states, lowercase codes
* **Optional normalization for free text** → remove control characters (keep for NLP downstream)

**Examples:**
`customer_id`, `customer_city`, `customer_state`, `review_comment_title`

---

## **2️⃣ Numeric Columns**

**Typical columns:** counts, scores, amounts, decimal metrics

**Common transformations / checks:**

* **Type cast** → explicitly cast to `int`, `float`, `decimal`
* **Domain validation / range check** → e.g., `review_score` between 1–5, `price >= 0`
* **Null handling** → drop or fill missing values for required numeric fields
* **Optional rounding / precision enforcement** → especially for decimal types

**Examples:**
`review_score`, `customer_zip_code_prefix`, `product_weight_g`

---

## **3️⃣ Timestamp / Date Columns**

**Typical columns:** creation/update times, CDC timestamps

**Common transformations / checks:**

* **Convert long → timestamp** → `__ts_ms` / `created_at`
* **Range validation** → avoid future dates or impossible historical values
* **Partitioning column (`ds`)** → `to_date(cdc_ts)` for Iceberg or daily reads
* **Deduplication logic** → if using SCD2 / normalized event log

**Examples:**
`created_at`, `updated_at`, `review_creation_date`, `cdc_ts_ms`

---

## **4️⃣ Key / ID Columns**

**Typical columns:** primary keys, foreign keys

**Common transformations / checks:**

* **Not null / existence check** → primary keys must exist
* **Deduplicate** → remove repeated events or Kafka replays
* **Optional format / regex check** → fixed length, pattern match

**Examples:**
`review_id`, `order_id`, `customer_id`

---

## **5️⃣ Free Text / Descriptions**

**Typical columns:** comments, titles, notes

**Common transformations / checks:**

* **Trim whitespace**
* **Optional max length** → avoid huge text blobs
* **Optional normalization for NLP** → lowercase, remove control chars

**Examples:**
`review_comment_title`, `review_comment_message`

---

## **6️⃣ CDC / Pipeline Metadata Columns** 
**IMPORTANT**: This project dont need this. (We've done this in the notebook.) )

**Typical columns:** Kafka offsets, ingestion timestamps

**Common transformations / checks:**

* **Drop unnecessary metadata** → e.g., `kafka_offset`, `kafka_partition` after silver
* **Keep minimal audit columns** → `spark_ingest_ts`, `batch_id`
* **Normalize CDC operation** → `__op` → `c/u/d`

---

## **7️⃣ Optional Derived Columns**
**IMPORTANT**: This project dont need this. (We are doing cdc.) 
**Common uses:**

* **Row hash** → for SCD2 / change detection
* **Hash of business columns** → efficient delta merge

---

### ✅ **Summary Rule of Thumb**

| Column Type             | Actions                                                  |
| ----------------------- | -------------------------------------------------------- |
| String / categorical    | trim, null check, optional case, max length              |
| Numeric                 | type cast, range check, null handling, optional rounding |
| Timestamp               | convert, range check, partition column, dedupe logic     |
| Keys                    | not null, deduplicate, optional format                   |
| Free text               | trim, optional length limit, optional normalization      |
| CDC / pipeline metadata | drop unnecessary, keep audit, normalize ops              |
| Optional                | row hash for change detection                            |

---
