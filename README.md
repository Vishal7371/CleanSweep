# CleanSweep 🧹

> Messy supplier file ingestion pipeline — 2nd Year Internship 2026

**Student:** Vishal | **GitHub:** [@Vishal7371](https://github.com/Vishal7371)  
**Problem:** H2 — Messy File Ingestion Pipeline  
**Segment:** Foundations of Data Engineering  
**Internship Duration:** 22 June – 26 July 2026

---

## 🎯 What This Project Does

CleanSweep is a data pipeline that ingests messy supplier files (CSV, XLSX), cleans them, validates the data, and loads clean rows into a DuckDB warehouse — while quarantining bad rows for human review instead of crashing.

**Business context:** SupplySync receives data from 5 suppliers daily. Each file has quirks — wrong date formats, duplicate rows, Spanish headers, merged cells. CleanSweep handles all of it automatically.

---

## 🏗️ Architecture

```
Supplier Files (5 formats)
        ↓
  Ingestion Layer    (file type detection, encoding, schema standardisation)
        ↓
  Validation Layer   (Custom validator + business rules)
        ↓
  ┌──────────────────────────────┐
  │  Good rows → DuckDB warehouse │
  │  Bad rows  → Quarantine table │
  └──────────────────────────────┘
        ↓
  dbt Transformations  (raw → staging → conformed)
        ↓
  Streamlit Dashboard  (observability)
        ↓
  Prefect Orchestration (scheduled runs, retries)
```

---

## 🛠️ Tech Stack

| Component | Tool |
|-----------|------|
| Language | Python 3.12 |
| Warehouse | DuckDB |
| Validation | Custom (validator.py) |
| Transformation | dbt-core + dbt-duckdb |
| Orchestration | Prefect |
| Dashboard | Streamlit |
| Containerisation | Docker + Docker Compose |

---

## 🚀 Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/Vishal7371/CleanSweep.git
cd CleanSweep

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the pipeline
python src/main.py

# 5. View the dashboard
streamlit run dashboard.py

# OR run with Docker
docker build -t cleansweep . && docker run --rm -v $(pwd)/data:/app/data cleansweep
```

---

## 📂 Project Structure

```
CleanSweep/
├── data/
│   ├── supplier_drops/     # Incoming raw supplier files
│   ├── raw/                # Raw data stored in DuckDB
│   ├── staging/            # Cleaned, type-corrected data
│   ├── conformed/          # Canonical schema (all suppliers unified)
│   └── quarantine/         # Bad rows with reasons
├── src/
│   ├── ingestion/          # File detection, encoding, loading
│   ├── validation/         # Pandera schema validation
│   ├── transformation/     # dbt models
│   └── observability/      # Pipeline run logging
├── dashboard/              # Streamlit observability dashboard
├── docs/
│   ├── design_doc.md       # Initial design document
│   └── adr/                # Architecture Decision Records
├── tests/                  # Unit + integration tests
├── .github/workflows/      # GitHub Actions CI/CD
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 📝 ADRs (Architecture Decision Records)

- [ADR-001: Why DuckDB?](docs/adr/ADR-001-duckdb.md) ✅
- [ADR-002: Why Custom Validation?](docs/adr/ADR-002-validation.md) ✅
- [ADR-003: Why Prefect?](docs/adr/ADR-003-prefect.md) ✅

---

## 🔌 Mini-Extension: Schema Drift Detector

When a supplier adds a new column to their file, the pipeline:
- Does NOT fail
- Logs a `schema_change` event
- Stores history in a `schema_history` table
- Sends an alert

---

## 📊 Dashboard

Run locally with:
```bash
streamlit run dashboard.py
```
Shows: valid rows, quarantined rows, pass rate, rows per supplier chart, quarantine reasons, and pipeline run history.

---

## ⚠️ Known Limitations

- DuckDB does not support concurrent writes (single-user only)
- No cloud deployment yet — runs locally only
- Schema drift detector alerts but does not auto-fix drift
- Docker image does not include the Streamlit dashboard (pipeline only)

---

## 🗺️ What I'd Do in 3rd Year

See [3rd Year Roadmap](docs/roadmap_3rd_year.md) *(coming Week 5)*

---

## 📄 License

MIT — See [LICENSE](LICENSE)
