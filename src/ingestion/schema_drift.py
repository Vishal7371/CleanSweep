"""
schema_drift.py - Schema Drift Detector

Detects when a supplier file has new or missing columns compared to what
the pipeline expects. This prevents silent data corruption.

How it works:
  1. A dictionary stores the EXPECTED columns for each supplier
  2. When a file is loaded, actual columns are compared to expected
  3. If columns were added or removed, an alert is raised

This is a lightweight alternative to tools like Great Expectations.
"""
from loguru import logger

# Expected columns for each supplier (after loader renames them)
EXPECTED_SCHEMAS = {
    "supplier_a": {"product_name", "price", "quantity", "order_date", "supplier", "category"},
    "supplier_b": {"product_name", "price", "quantity", "order_date", "supplier", "category"},
    "supplier_c": {"product_name", "price", "quantity", "order_date", "supplier", "category"},
    "supplier_d": {"product_name", "price", "quantity", "order_date", "supplier", "category"},
    "supplier_e": {"product_name", "price", "quantity", "order_date", "supplier", "category"},
}

def detect_drift(df, supplier_name):
    if supplier_name not in EXPECTED_SCHEMAS:
        logger.warning(f"No expected schema for {supplier_name} — skipping drift check")
        return False

    expected = EXPECTED_SCHEMAS[supplier_name]
    actual = set(df.columns)

    # Remove metadata columns added by loader (not part of original schema)
    actual = actual - {"source_file", "loaded_at"}

    new_columns = actual - expected
    missing_columns = expected - actual

    if not new_columns and not missing_columns:
        logger.success(f"  {supplier_name}: No schema drift detected ✅")
        return False

    if new_columns:
        logger.warning(f"  {supplier_name}: NEW columns detected: {new_columns}")

    if missing_columns:
        logger.warning(f"  {supplier_name}: MISSING columns detected: {missing_columns}")

    return True
if __name__ == "__main__":
    import duckdb
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    db_path = str(project_root / "data" / "cleansweep.duckdb")

    con = duckdb.connect(db_path)

    print("\n=== Schema Drift Check — All Suppliers ===\n")

    for supplier_name in ["supplier_a", "supplier_b", "supplier_c", "supplier_d", "supplier_e"]:
        df = con.execute(f"SELECT * FROM raw.{supplier_name}").df()
        detect_drift(df, supplier_name)

    print("\n--- Simulating drift: supplier_a gets a new column 'discount' ---\n")
    import pandas as pd
    fake_df = con.execute("SELECT * FROM raw.supplier_a").df()
    fake_df["discount"] = 10
    detect_drift(fake_df, "supplier_a")

    con.close()
