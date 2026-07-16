"""
main.py - CleanSweep Pipeline Controller

This is the MASTER script that runs the full pipeline end-to-end:
  Step 1: Load all 5 supplier files into DuckDB (raw layer)
  Step 2: Validate each supplier's data
  Step 3: Save bad rows to quarantine table
  Step 4: Print a summary report

Run this file to execute the entire pipeline:
  python src/main.py
"""


import duckdb
from pathlib import Path
from loguru import logger
from datetime import datetime

from ingestion.loader import load_all_suppliers, SUPPLIER_LOADERS
from validation.validator import validate_dataframe
from validation.quarantine import save_to_quarantine
from observability.pipeline_logger import log_run



def run_pipeline(drop_folder, db_path):
    print("\n" + "="*55)
    print("   CleanSweep Pipeline — Starting")
    print("="*55)

    started_at = datetime.now()

    # Step 1: Load all supplier files into DuckDB raw layer
    logger.info("STEP 1: Loading supplier files...")
    load_all_suppliers(drop_folder, db_path)

    # Step 2 & 3: Validate + Quarantine each supplier
    logger.info("STEP 2: Validating and quarantining bad rows...")

    total_good = 0
    total_bad = 0

    con = duckdb.connect(db_path)

    for supplier_name in SUPPLIER_LOADERS.keys():
        df = con.execute(f"SELECT * FROM raw.{supplier_name}").df()
        good_df, bad_df = validate_dataframe(df, supplier_name)
        save_to_quarantine(bad_df, db_path)
        log_run(db_path, supplier_name, started_at, len(good_df), len(bad_df))
        total_good += len(good_df)
        total_bad += len(bad_df)


    con.close()

    # Step 4: Print summary
    elapsed = (datetime.now() - started_at).seconds
    print("\n" + "="*55)
    print("   PIPELINE SUMMARY")
    print("="*55)
    print(f"   Valid rows loaded:    {total_good}")
    print(f"   Rows quarantined:     {total_bad}")
    print(f"   Time taken:           {elapsed}s")
    print("="*55 + "\n")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    drop_folder = str(project_root / "data" / "supplier_drops")
    db_path = str(project_root / "data" / "cleansweep.duckdb")

    run_pipeline(drop_folder, db_path)


