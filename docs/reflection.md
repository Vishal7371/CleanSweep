# Internship Reflection — CleanSweep Pipeline

**Student:** Vishal  
**Problem:** H2 — Messy File Ingestion Pipeline  
**Duration:** 22 June – 26 July 2026  
**Stack:** Python, DuckDB, dbt, Streamlit, Prefect, Docker

---

## 1. What I Set Out to Do

When I started this internship, I was given a problem statement: build a data pipeline that can ingest messy supplier files. Five different suppliers, five different formats — Spanish headers, footer rows, merged Excel cells, mixed date formats, and duplicate rows.

My goal was to build a system that could handle all five automatically, without crashing, and without losing any data — not even the bad rows.

I had used Python before, but I had never built anything like a data pipeline. I did not know what DuckDB was. I had never heard of dbt or Prefect. Docker was something I had seen mentioned online but never touched.

By the end of Week 5, all of that changed.

---

## 2. What I Actually Built

CleanSweep is a data pipeline with the following layers:

**Ingestion Layer** — `src/ingestion/`
- `loader.py` reads all 6 supplier files and handles their individual quirks
- `detector.py` detects file type (CSV or Excel) automatically
- `schema_drift.py` detects when a supplier changes their column structure

**Validation Layer** — `src/validation/`
- `validator.py` checks every row against 4 business rules
- `quarantine.py` saves bad rows to a separate DuckDB table with a reason

**Transformation Layer** — `dbt_project/`
- 6 staging models clean and type-cast each supplier's data
- 1 conformed model combines all suppliers into a single unified table

**Observability Layer** — `src/observability/`
- `pipeline_logger.py` logs every pipeline run to DuckDB with UUID, timestamps, and row counts

**Orchestration** — `src/pipeline_flow.py`
- Prefect `@flow` and `@task` decorators manage the pipeline with retry logic

**Dashboard** — `dashboard.py`
- Streamlit web app showing metrics, charts, quarantine data, and run history

**Infrastructure** — `Dockerfile`, `docker-compose.yml`
- The entire project runs inside a Docker container with one command

**Tests** — `tests/test_validator.py`
- 6 pytest unit tests prove the validator works correctly

---

## 3. The Hardest Part

The hardest concept for me was understanding **why we quarantine bad rows instead of crashing**.

In my head, if a row has a negative price, the pipeline should stop and show an error. That felt "safer." But my mentor helped me understand the real-world problem with that approach: if 1 bad row out of 51 causes the whole pipeline to crash, then 50 perfectly good rows never get processed either. That's worse.

The quarantine pattern — where bad rows go to a separate table with a reason — was a completely new way of thinking for me. It is fault-tolerant. The pipeline keeps running. The bad data is not lost — it is saved for human review. This is how real production pipelines work.

Another hard part was understanding **dbt**. At first, I thought it was just SQL. But dbt manages the order of models, handles dependencies with `{{ ref() }}`, and separates the "staging" layer (per supplier) from the "conformed" layer (all suppliers combined). Once I understood that it is about organising SQL into layers — not just running SQL — it clicked.

---

## 4. What I Learned

**Technical skills:**
- How to structure a Python project with modules and packages
- How DuckDB works as a local analytical warehouse (single file, fast, no server)
- What dbt does and the difference between staging and conformed layers
- How pandas handles real-world data problems (encoding, date parsing, duplicates)
- What Docker is and how to containerize a Python application
- How Prefect orchestrates pipelines with tasks and retry logic
- How to write unit tests with pytest and why tests matter
- What an Architecture Decision Record (ADR) is and how to write one

**Thinking skills:**
- How to break a big problem into small, testable components
- How to think about "what happens when data is bad" — not just "what happens when it works"
- How to read error messages and debug step by step
- How to explain technical decisions in writing (ADRs)

---

## 5. What I Would Do Differently

**More tests from the start.**  
I wrote tests at the end of Week 5. If I had written them in Week 1, they would have caught bugs earlier and made me more confident when changing code. Test-driven development (TDD) is something I want to practice from Day 1 in future projects.

**Modular loading from the start.**  
When I added Supplier F in Week 4, I had to add a new function, a new dbt model, and update the conformed model. In a real system, a new supplier should be handled by configuration, not code changes. A better design would be a generic loader that reads a config file and knows how to handle any supplier format.

**Better error messages in the validator.**  
Right now, the quarantine reason is a simple string like "negative price." In production, I would want the reason to include the row number, the supplier name, the timestamp, and the exact field value that failed — so the supplier can fix it quickly.

---

## 6. Final Thought

When I ran `python src/main.py` for the first time and saw all 5 suppliers load successfully, it was the best feeling of the internship. Not because the code was perfect — it was not. But because I had built something that actually worked, end-to-end, with real data problems.

By the end, I was running a 6-supplier pipeline with a live dashboard, automated tests, and Docker packaging. Five weeks ago, I did not know what most of those words meant.

That is what I will take from this internship.

---

*Written by Vishal — CleanSweep Internship 2026*
