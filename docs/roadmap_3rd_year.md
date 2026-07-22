# CleanSweep — 3rd Year Roadmap

**What I would build if I had another year**

---

## What CleanSweep Does Now (End of Year 2)

At the end of this internship, CleanSweep can:

- Ingest 6 supplier files (CSV and Excel) with individual quirks
- Validate every row against 4 business rules
- Quarantine bad rows with reasons (without crashing)
- Transform raw data into a conformed DuckDB warehouse via dbt
- Detect schema drift when suppliers change their file format
- Log every pipeline run to an observability table
- Display metrics on a Streamlit dashboard
- Run the entire pipeline inside a Docker container
- Orchestrate runs via Prefect with retry logic

This is a solid local pipeline. But it is not production-ready.

---

## What I Would Add in Year 3

### 1. 🌐 Cloud Deployment (GCP / AWS)

**The problem:** CleanSweep runs on my laptop. If I turn it off, the pipeline stops.

**The fix:** Deploy to Google Cloud Platform (GCP):
- Move DuckDB → **BigQuery** (cloud data warehouse)
- Run the pipeline on **Cloud Run** (serverless containers)
- Store supplier files in **Google Cloud Storage** instead of a local folder
- Use **Cloud Scheduler** to trigger the pipeline daily at 9 AM automatically

**What I'd learn:** GCP services, Infrastructure as Code (Terraform), IAM roles

---

### 2. 🔔 Alerting System

**The problem:** If a supplier sends 0 rows, or the quarantine rate jumps to 90%, nobody knows until they check the dashboard manually.

**The fix:** Add automatic alerts:
- Email alert if quarantine rate > 20%
- Slack notification if a supplier file is missing after 10 AM
- PagerDuty alert if the pipeline crashes

**Tool I'd use:** Prefect notifications, or a dedicated alerting service like Grafana

---

### 3. 🤖 Auto-Fix Common Errors

**The problem:** The same errors repeat every week. Supplier D always sends wrong date formats. Supplier A always uses Spanish headers. We know this — but the human still has to manually review the quarantine table.

**The fix:** Add an auto-correction layer:
- For known patterns, attempt to fix the row automatically
- If the fix succeeds → move to `fixed_rows` table instead of quarantine
- Log what was fixed and why
- Only quarantine rows that could not be auto-fixed

---

### 4. 📁 Hot Folder — Any Supplier, Any Time

**The problem:** Adding a new supplier (e.g., Supplier G) requires a code change — a new Python function and a new dbt model.

**The fix:** Build a configuration-driven loader:
- Supplier config is a YAML file, not Python code
- Drop a file → pipeline detects it → loads it automatically
- A new supplier = add a YAML file, not write new code

This is called a **"hot folder"** pattern. It is used in enterprise ETL systems.

---

### 5. 📊 Data Quality Score

**The problem:** Right now I can see "13 rows quarantined." But I cannot see trends — is data quality getting better or worse over time?

**The fix:** Build a data quality scoring system:
- Score each supplier 0–100% based on their historical pass rate
- Show a trend chart: "Supplier D was 80% last week, 60% this week"
- Automatically flag suppliers whose score drops more than 10% in a week

---

### 6. 🧪 Integration Tests

**The problem:** My 6 pytest tests only test the validator in isolation. They do not test the full end-to-end pipeline.

**The fix:** Add integration tests that:
- Load a test CSV file
- Run the full pipeline against it
- Check the DuckDB output matches expected results
- Run automatically on every Git push via **GitHub Actions CI/CD**

---

### 7. 📝 Data Catalogue

**The problem:** If a new team member joins, they have to read the code to understand what data is in the warehouse.

**The fix:** Build a data catalogue:
- Document every table, every column, every business rule
- Use **dbt's built-in documentation** (`dbt docs generate`)
- Host it as a website so anyone can browse the data without touching code

---

## Summary Table

| Feature | Priority | Effort |
|---------|----------|--------|
| Cloud deployment (GCP) | 🔴 High | 3 weeks |
| Alerting system | 🔴 High | 1 week |
| Auto-fix common errors | 🟡 Medium | 2 weeks |
| Hot folder (config-driven) | 🟡 Medium | 2 weeks |
| Data quality score | 🟡 Medium | 1 week |
| Integration tests + CI/CD | 🔴 High | 1 week |
| Data catalogue | 🟢 Low | 3 days |

---

## The One Thing I Would Do First

If I had one week to make CleanSweep production-ready, I would add **cloud deployment + alerting**.

A pipeline that runs on a laptop and fails silently is not useful in production. The most important property of a production pipeline is that it runs reliably, and that someone knows immediately when it does not.

Everything else — auto-fix, hot folders, data quality scores — is valuable. But reliability comes first.

---

*Written by Vishal — CleanSweep Internship 2026*
