# ADR-001: Use DuckDB as the Local Warehouse

**Date:** 2026-07-03  
**Status:** Accepted  
**Author:** Vishal  

---

## Context

CleanSweep is a file ingestion pipeline that reads messy CSV and Excel files
from 5 different suppliers and stores clean data for analysis.

The pipeline needed a database to:
- Store raw supplier data after ingestion
- Store validated (clean) rows separately from quarantined (bad) rows
- Support SQL queries for dbt transformation models
- Run locally without any server setup or cloud costs

The project is a student internship prototype, so simplicity and zero 
infrastructure cost were important constraints.

## Options Considered

### Option 1: SQLite
- ✅ Serverless, file-based, zero setup
- ✅ Built into Python standard library
- ❌ Poor support for analytical queries (slow on aggregations)
- ❌ Not supported by dbt-core natively

### Option 2: PostgreSQL
- ✅ Industry standard, full SQL support
- ✅ Works well with dbt
- ❌ Requires a running server (Docker or local install)
- ❌ Too heavy for a local prototype

### Option 3: DuckDB ✅ CHOSEN
- ✅ Serverless, file-based (single `.duckdb` file)
- ✅ Designed for analytical queries (columnar storage)
- ✅ Native Python integration (`pip install duckdb`)
- ✅ Official dbt adapter (`dbt-duckdb`)
- ✅ Zero infrastructure cost

## Decision

We chose **DuckDB** as the local warehouse for CleanSweep.

DuckDB is ideal for this use case because it behaves like a full SQL database
but requires zero server setup. The entire database is a single file
(`cleansweep.duckdb`) that can be committed to git or shared easily.

The official `dbt-duckdb` adapter means our transformation models run
without any changes if we migrate to a cloud warehouse like BigQuery later.

## Consequences

**Positive:**
- Pipeline runs with a single `python src/main.py` command, no Docker needed
- DuckDB file is portable — share it like a regular file
- dbt models work identically on DuckDB locally and BigQuery in production
- Query speed is fast enough for our 51-row prototype dataset

**Negative / Trade-offs:**
- DuckDB is not suitable for concurrent writes (multiple users writing at once)
- For production with millions of rows, we would migrate to BigQuery or Snowflake
- DuckDB has no built-in access control (no user permissions)

## Conclusion

For a student internship prototype that runs locally, DuckDB is the right tool.
If CleanSweep were deployed to production, the migration path is clear:
swap `dbt-duckdb` for `dbt-bigquery` and update the profiles.yml.
