"""
validator.py - Data Validation Layer

Check every row from the supplier files against these rules:
1. product_name must not be empty
2. price must be a number greater than 0
3. quantity must be a whole number greater than 0
4. order_date must br a whole number greater than 0

Returns two Dataframes:
 - good_df  : rows that passed all checks → go to DuckDB
 - bad_df   : rows that failed any check  → go to Quarantine
"""


import pandas as pd
from loguru import logger
from datetime import datetime

def is_valid_price(price):
    try: 
        return float(price ) > 0
    except (ValueError,TypeError):
        return False


def is_valid_quantity(qty):
    try:
        return int(float(qty)) > 0
    except (ValueError, TypeError):
        return False

def is_valid_date(date_str):
    if not date_str or str(date_str) == "nan":
        return False
    try:
        datetime.strptime(str(date_str),"%Y-%m-%d"
)
        return True
    except ValueError:
        return False

def is_valid_product_name(name):
    if not name or str(name).strip() == "" or str(name) == "nan":
        return False
    return True


def validate_dataframe(df, supplier_name):
    good_rows = []
    bad_rows = []

    for _, row in df.iterrows():
        reasons = []

        if not is_valid_product_name(row.get("product_name")):
            reasons.append("missing or empty product_name")

        if not is_valid_price(row.get("price")):
            reasons.append("price must be > 0")

        if not is_valid_quantity(row.get("quantity")):
            reasons.append("quantity must be > 0")

        if not is_valid_date(row.get("order_date")):
            reasons.append("invalid order_date format")

        if reasons:
            row_dict = row.to_dict()
            row_dict["quarantine_reason"] = "; ".join(reasons)
            row_dict["supplier_name"] = supplier_name
            bad_rows.append(row_dict)
        else:
            good_rows.append(row.to_dict())

    good_df = pd.DataFrame(good_rows)
    bad_df = pd.DataFrame(bad_rows)

    logger.info(f"{supplier_name}: {len(good_df)} valid, {len(bad_df)} quarantined")
    return good_df, bad_df


if __name__ == "__main__":
    import duckdb
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    db_path = str(project_root / "data" / "cleansweep.duckdb")

    con = duckdb.connect(db_path)
    df = con.execute("SELECT * FROM raw.supplier_a").df()
    con.close()

    good_df, bad_df = validate_dataframe(df, "supplier_a")

    print(f"\nSupplier A results:")
    print(f"  Valid rows:      {len(good_df)}")
    print(f"  Quarantined rows: {len(bad_df)}")
    if len(bad_df) > 0:
        print(f"\nBad rows:")
        print(bad_df[["product_name", "price", "quantity", "quarantine_reason"]])
