"""
quarantine.py - Quarantine System

Saves bad rows (that failed validation) into DuckDB quarantine table.
Bad rows are NOT deleted - they are stored with the reason they failed.
A human can later review, fix, and re-inject them into the pipeline.
Table: quarantine.bad_rows

"""

import pandas as pd
import duckdb
from loguru import logger
from datetime import datetime


def save_to_quarantine(bad_df, db_path):
    if bad_df.empty:
        logger.info("No bad rows to quarantine.")
        return 0

    bad_df["quarantined_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS quarantine")

    con.execute("""
        CREATE TABLE IF NOT EXISTS quarantine.bad_rows AS
        SELECT * FROM bad_df WHERE 1=0
    """)

    con.execute("INSERT INTO quarantine.bad_rows SELECT * FROM bad_df")

    count = con.execute("SELECT COUNT(*) FROM quarantine.bad_rows").fetchone()[0]
    con.close()

    logger.success(f"Quarantined {len(bad_df)} rows. Total in quarantine: {count}")
    return len(bad_df)

if __name__ == "__main__":
    from pathlib import Path
    from validator import validate_dataframe

    project_root = Path(__file__).parent.parent.parent
    db_path = str(project_root / "data" / "cleansweep.duckdb")

    con = duckdb.connect(db_path)
    df = con.execute("SELECT * FROM raw.supplier_a").df()
    con.close()

    good_df, bad_df = validate_dataframe(df, "supplier_a")

    print(f"\nBad rows found: {len(bad_df)}")
    save_to_quarantine(bad_df, db_path)

    print("\nChecking quarantine table in DuckDB...")
    con = duckdb.connect(db_path)
    result = con.execute("SELECT * FROM quarantine.bad_rows").df()
    con.close()
    print(result[["product_name", "quarantine_reason", "quarantined_at"]])
