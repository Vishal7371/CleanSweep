"""
loader.py - Supplier File Loader

Reads all 5 supplier files, handles their quirks, and saves to DuckDB.

Supplier A - headers in Spanish    - rename columns to English
Supplier B - footer summary rows   - remove rows where price is not a number
Supplier C - Excel merged cells    - skip first 2 rows
Supplier D - mixed date formats    - standardise all dates to YYYY-MM-DD
Supplier E - duplicate rows        - drop exact duplicates
 

"""


import pandas as pd
import duckdb
from pathlib import Path
from loguru import logger
from datetime import datetime

# Supplier A sends headers in Spanish - this maps them to English
SUPPLIER_A_COLUMN_MAP = {
    "producto": "product_name",
    "precio": "price",
    "cantidad": "quantity",
    "fecha_pedido": "order_date",
    "proveedor": "supplier",
    "categoria": "category",
}
def load_supplier_a(filepath):
    logger.info("Loading Supplier A (Spanish headers)...")
    df = pd.read_csv(filepath, encoding="utf-8")
    df = df.rename(columns=SUPPLIER_A_COLUMN_MAP)
    logger.success(f"  Supplier A: {len(df)} rows loaded")
    return df

def load_supplier_b(filepath):
    logger.info("Loading Supplier B (footer rows)...")
    df = pd.read_csv(filepath, encoding="utf-8")
    original_count = len(df)                                          # ← new
    df = df[pd.to_numeric(df["price"], errors="coerce").notna()]     # ← new
    logger.success(f"  Supplier B: {len(df)} rows kept, {original_count - len(df)} removed")
    return df

def load_supplier_c(filepath):
    logger.info("Loading Supplier C (Excel merged cells)...")
    df = pd.read_excel(filepath, skiprows=2, header=0, engine="openpyxl")
    logger.success(f"  Supplier C: {len(df)} rows loaded, merged rows skipped")
    return df

def load_supplier_d(filepath):
    logger.info("Loading Supplier D (mixed date formats)...")
    df = pd.read_csv(filepath, encoding="utf-8")
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True, errors="coerce")
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
    logger.success(f"  Supplier D: {len(df)} rows loaded, dates standardised")
    return df


def load_supplier_e(filepath):
    logger.info("Loading Supplier E (duplicate rows)...")
    df = pd.read_csv(filepath, encoding="utf-8")
    original_count = len(df)
    df = df.drop_duplicates()
    logger.success(f"  Supplier E: {len(df)} rows kept, {original_count - len(df)} duplicates removed")
    return df

def save_to_duckdb(df, supplier_name, db_path):
    table_name = f"raw.{supplier_name}"
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    con.close()
    logger.success(f"  Saved {row_count} rows to DuckDB: {table_name}")
    return row_count


SUPPLIER_LOADERS = {
    "supplier_a": load_supplier_a,
    "supplier_b": load_supplier_b,
    "supplier_c": load_supplier_c,
    "supplier_d": load_supplier_d,
    "supplier_e": load_supplier_e,
}

def load_all_suppliers(drop_folder, db_path):
    results = {}
    drop_path = Path(drop_folder)
    print("\n=== CleanSweep Loader ===\n")
    for supplier_name, loader_fn in SUPPLIER_LOADERS.items():
        matches = list(drop_path.glob(f"{supplier_name}.*"))
        matches = [f for f in matches if f.suffix in (".csv", ".xlsx")]
        if not matches:
            logger.warning(f"No file found for {supplier_name}, skipping.")
            continue
        filepath = str(matches[0])
        df = loader_fn(filepath)
        df["source_file"] = supplier_name
        df["loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_count = save_to_duckdb(df, supplier_name, db_path)
        results[supplier_name] = row_count
    print(f"\nTotal rows loaded: {sum(results.values())}")
    return results

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    drop_folder = str(project_root / "data" / "supplier_drops")
    db_path = str(project_root / "data" / "cleansweep.duckdb")
    load_all_suppliers(drop_folder, db_path)
