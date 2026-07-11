# ADR-003: Use Prefect for Pipeline Orchestration

**Date:** 2026-07-11  
**Status:** Proposed  
**Author:** Vishal  

---

## Context

CleanSweep currently runs as a manual script (`python src/main.py`).
In production, data pipelines need to run automatically on a schedule
(e.g., every day at 9 AM) and retry automatically if they fail.

An orchestration tool is needed to:
- Schedule pipeline runs automatically
- Retry failed tasks without manual intervention
- Provide a visual dashboard to monitor run history
- Send alerts when something goes wrong

## Options Considered

### Option 1: Apache Airflow
- ✅ Industry standard, used at large companies
- ✅ Rich UI and scheduling features
- ❌ Very heavy — requires Docker, a database, a web server
- ❌ Too complex for a student prototype

### Option 2: Cron Jobs (Linux scheduler)
- ✅ Zero installation — built into every Linux system
- ✅ Simple for basic scheduling
- ❌ No retry logic, no monitoring UI, no alerts
- ❌ Silent failures — if something breaks, you won't know

### Option 3: Prefect ✅ CHOSEN
- ✅ Modern, Python-native orchestration tool
- ✅ Easy to add to existing Python code (just add decorators)
- ✅ Free tier includes a monitoring dashboard
- ✅ Built-in retry logic and failure alerts
- ❌ Requires internet connection for the cloud dashboard

## Decision

We chose **Prefect** as the orchestration tool for CleanSweep.

Prefect integrates with existing Python code using simple decorators
(`@flow` and `@task`). This means our existing `main.py` can be
converted to a Prefect flow with minimal changes.

The Prefect dashboard gives a visual history of every run, making it
easy to see when the pipeline last ran and whether it succeeded.

## Consequences

**Positive:**
- Pipeline can be scheduled to run daily without manual intervention
- Failed runs are retried automatically (configurable retry count)
- Dashboard shows full run history with logs

**Negative:**
- Requires a Prefect account for the cloud dashboard
- For fully offline deployment, Prefect server would need to be self-hosted
- Adds a dependency that must be kept up to date

## Conclusion

Prefect is the right tool for orchestrating CleanSweep at this stage.
It is lightweight enough for a student project but professional enough
to demonstrate real-world orchestration concepts at the showcase.
