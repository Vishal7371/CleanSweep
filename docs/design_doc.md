# CleanSweep — Initial Design Document

**Student:** Vishal (GitHub: Vishal7371)  
**Problem Code:** H2 — Messy File Ingestion Pipeline  
**Segment:** Foundations of Data Engineering  
**Date:** 24 June 2026  
**Mentor Review Status:** Pending

---

## 1. Problem Statement

In the real world, companies receive data from multiple external suppliers in different formats — CSVs with different column names, Excel files with merged cells, files with inconsistent date formats, duplicate rows, and even headers in other languages.

My goal is to build **CleanSweep**: a data pipeline that ingests messy supplier files, cleans them, validates the data, and loads clean rows into a warehouse — while quarantining bad rows for human review instead of crashing.

**Business scenario:** I am a Junior Data Engineer at "SupplySync", which aggregates data from 5 suppliers. Each supplier sends daily file drops with different quirks and formats.

---

## 2. What I Will Build

### Core Pipeline (3 layers)

```
Raw Files (5 CSVs/XLSXs)
        ↓
  Ingestion Layer       ← detects file type, encoding, schema
        ↓
  Validation Layer      ← schema rules, business rules (price > 0)
        ↓
  ┌─────────────┐
  │  Good rows  │ → DuckDB (raw → staging → conformed)
  │  Bad rows   │ → Quarantine table (with reason)
  └─────────────┘
        ↓
  Observability         ← dashboard: rows ingested, quarantined, top errors
        ↓
  Orchestration         ← Prefect schedules + retries the pipeline
```

### The 5 Simulated Supplier Files (and their quirks)

| Supplier | File Type | Quirk |
|----------|-----------|-------|
| Supplier A | CSV | Header row in Spanish |
| Supplier B | CSV | Footer summary row at the bottom |
| Supplier C | XLSX | Merged cells in header |
| Supplier D | CSV | Inconsistent date formats (DD/MM/YYYY vs YYYY-MM-DD) |
| Supplier E | CSV | Duplicate rows |

### Mini-Extension: Schema Drift Detector
When a supplier adds a new column that wasn't there before, the pipeline:
- Does NOT fail
- Logs a `schema_change` event
- Stores it in a `schema_history` table
- Sends an alert (log or email stub)

---

## 3. Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python 3.11 | Industry standard for DE |
| Warehouse | DuckDB | Zero-config, fast, no server needed |
| Validation | Pandera | Declarative schema validation in Python |
| Transformation | dbt-core + dbt-duckdb | SQL models, version-controlled, testable |
| Orchestration | Prefect | Modern, easy to use, great free tier |
| Observability | Streamlit | Simple dashboard, Python-native |
| Containerisation | Docker + Docker Compose | Reproducible environment |
| CI/CD | GitHub Actions | Free, integrates with GitHub |
| Encoding detection | chardet | Detects file encoding automatically |

---

## 4. Data Flow (Detailed)

1. **File Drop** → Supplier files land in `data/supplier_drops/`
2. **Ingestion Layer** (`src/ingestion/`)
   - Detects file type (CSV, XLSX)
   - Detects encoding (chardet)
   - Standardises column names (lowercase, underscores)
   - Reports per-file diagnostics
3. **Validation Layer** (`src/validation/`)
   - Schema enforcement via Pandera
   - Business rules: `price > 0`, valid dates, non-null required fields
   - Good rows → `data/staging/`
   - Bad rows → `data/quarantine/` with reason column
4. **dbt Transformation** (`dbt_project/`)
   - `staging` models: clean column types
   - `conformed` models: canonical schema across all suppliers
   - At least 6 models, tests on conformed layer
5. **Observability** (`dashboard/`)
   - Streamlit dashboard: files processed, rows accepted/quarantined, top 3 quarantine reasons
6. **Replay / Idempotency**
   - Pipeline can re-process yesterday's file
   - Uses file hash + date check to avoid duplicate loads

---

## 5. Storage Design (DuckDB)

```sql
-- Three-layer architecture
raw.*           -- original data, preserved as-is
staging.*       -- cleaned column names, correct types
conformed.*     -- canonical schema, all suppliers unified

-- Special tables
quarantine.bad_rows        -- bad rows with reason + source file
pipeline.pipeline_runs     -- metadata: run time, rows in/out, errors
schema_history.changes     -- schema drift log
```

---

## 6. Risks & Open Questions

| Risk | Mitigation |
|------|-----------|
| Supplier file format changes mid-project | Schema drift detector handles this |
| DuckDB not suitable for large files | Acceptable at 2nd year scale (< 1M rows) |
| Prefect setup complexity | Start with simple flows, add retries in Week 4 |
| dbt learning curve | Start with staging models only in Week 3 |

---

## 7. Weekly Milestones

| Week | Goal |
|------|------|
| Week 1 | Repo setup, 5 supplier CSVs created, 1 CSV ingested into DuckDB |
| Week 2 | All 5 files ingested, validated, quarantine working, end-to-end demo |
| Week 3 | dbt models (6+), mini-extension (schema drift), 3 ADRs |
| Week 4 | Prefect orchestration, Streamlit dashboard, Docker Compose, Milestone 1 |
| Week 5 | Polish, reflection, Loom, final submission |

---

## 8. What "Done" Looks Like

- [ ] 5 supplier files ingested automatically
- [ ] Bad rows quarantined (not crashing)
- [ ] dbt conformed layer with passing tests
- [ ] Streamlit dashboard showing pipeline stats
- [ ] Prefect flow running on schedule
- [ ] Schema drift detector working
- [ ] Docker Compose for full stack
- [ ] 3 ADRs written
- [ ] README: clone → run in < 20 minutes
- [ ] Live deployment URL
- [ ] 3-min Loom recording
