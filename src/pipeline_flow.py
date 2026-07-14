"""
pipeline_flow.py - Prefect Orchestrated Pipeline

Converts the CleanSweep pipeline into a Prefect flow with:
  - Individual @task decorators for each step
  - Automatic retry on failure
  - Run logging via observability.pipeline_runs

Run with: python src/pipeline_flow.py
"""

from prefect import flow, task
from pathlib import Path
from datetime import datetime
from loguru import logger

from ingestion.loader import load_all_suppliers, SUPPLIER_LOADERS
from validation.validator import validate_dataframe
from validation.quarantine import save_to_quarantine
from observability.pipeline_logger import log_run

project_root = Path(__file__).parent.parent
DROP_FOLDER  = str(project_root / "data" / "supplier_drops")
DB_PATH      = str(project_root / "data" / "cleansweep.duckdb")

@task(name="Load Suppliers", retries=2, retry_delay_seconds=5)
def task_load(drop_folder, db_path):
    logger.info("TASK: Loading all supplier files...")
    load_all_suppliers(drop_folder, db_path)
    logger.success("TASK: Loading complete!")


@task(name="Validate and Quarantine", retries=1, retry_delay_seconds=5)
def task_validate(db_path):
    import duckdb
    logger.info("TASK: Validating and quarantining...")

    total_good = 0
    total_bad  = 0

    con = duckdb.connect(db_path)
    for supplier_name in SUPPLIER_LOADERS.keys():
        started_at = datetime.now()
        df = con.execute(f"SELECT * FROM raw.{supplier_name}").df()
        good_df, bad_df = validate_dataframe(df, supplier_name)
        save_to_quarantine(bad_df, db_path)
        log_run(db_path, supplier_name, started_at, len(good_df), len(bad_df))
        total_good += len(good_df)
        total_bad  += len(bad_df)
    con.close()

    logger.success(f"TASK: Validation done — {total_good} valid, {total_bad} quarantined")
    return total_good, total_bad
@flow(name="CleanSweep Pipeline")
def cleansweep_flow():
    print("\n" + "="*50)
    print("  CleanSweep Pipeline — Prefect Flow")
    print("="*50)

    # Step 1: Load
    task_load(DROP_FOLDER, DB_PATH)

    # Step 2: Validate + Quarantine + Log
    total_good, total_bad = task_validate(DB_PATH)

    # Summary
    print("\n" + "="*50)
    print("  FLOW SUMMARY")
    print("="*50)
    print(f"  Valid rows:      {total_good}")
    print(f"  Quarantined:     {total_bad}")
    print("="*50 + "\n")


if __name__ == "__main__":
    cleansweep_flow()
