"""
pipeline_logger.py - Pipeline Run Logger

Records every pipeline run to a DuckDB table: observability.pipeline_runs

Each row in the table represents ONE supplier being processed:
  - When it started and finished
  - How many rows were loaded and quarantined
  - Whether it succeeded or failed

This gives full visibility into every pipeline execution.
"""

import duckdb
import uuid
from loguru import logger
from datetime import datetime

def create_log_table(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS observability")
    con.execute("""
        CREATE TABLE IF NOT EXISTS observability.pipeline_runs (
            run_id        VARCHAR,
            supplier_name VARCHAR,
            started_at    VARCHAR,
            finished_at   VARCHAR,
            rows_loaded   INTEGER,
            rows_quarantined INTEGER,
            status        VARCHAR
        )
    """)


def log_run(db_path, supplier_name, started_at, rows_loaded, rows_quarantined, status="success"):
    run_id = str(uuid.uuid4())[:8]
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con = duckdb.connect(db_path)
    create_log_table(con)

    con.execute("""
        INSERT INTO observability.pipeline_runs VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        run_id,
        supplier_name,
        started_at.strftime("%Y-%m-%d %H:%M:%S"),
        finished_at,
        rows_loaded,
        rows_quarantined,
        status
    ])

    con.close()
    logger.info(f"  Logged run [{run_id}]: {supplier_name} → {rows_loaded} loaded, {rows_quarantined} quarantined")

if __name__ == "__main__":
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    db_path = str(project_root / "data" / "cleansweep.duckdb")

    started = datetime.now()
    log_run(db_path, "supplier_a", started, rows_loaded=7, rows_quarantined=3)
    log_run(db_path, "supplier_b", started, rows_loaded=10, rows_quarantined=2)
    log_run(db_path, "supplier_c", started, rows_loaded=10, rows_quarantined=0)

    import duckdb
    con = duckdb.connect(db_path)
    print("\n=== Pipeline Run Log ===")
    print(con.execute("SELECT * FROM observability.pipeline_runs").df().to_string(index=False))
    con.close()


