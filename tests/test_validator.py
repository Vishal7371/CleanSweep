"""
test_validator.py - Unit tests for the CleanSweep validator

Tests that the validator correctly:
  - Passes valid rows
  - Rejects negative prices
  - Rejects missing quantities
  - Rejects blank product names

Run with: pytest tests/
"""

import sys
import os
import pandas as pd

# Add src/ to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validation.validator import validate_dataframe


def make_row(product="Widget", price=100, quantity=10,
             order_date="2026-01-15", supplier="TestCo", category="Electronics"):
    """Helper: creates a one-row DataFrame with given values."""
    return pd.DataFrame([{
        "product_name": product,
        "price":        price,
        "quantity":     quantity,
        "order_date":   order_date,
        "supplier":     supplier,
        "category":     category,
    }])

# ── TEST 1: Valid row passes through ─────────────────
def test_valid_row_passes():
    df = make_row()
    good_df, bad_df = validate_dataframe(df, "test_supplier")
    assert len(good_df) == 1, "Valid row should pass"
    assert len(bad_df) == 0, "No rows should be quarantined"


# ── TEST 2: Negative price is rejected ───────────────
def test_negative_price_rejected():
    df = make_row(price=-500)
    good_df, bad_df = validate_dataframe(df, "test_supplier")
    assert len(good_df) == 0, "Row with negative price should be rejected"
    assert len(bad_df) == 1, "Row should go to quarantine"


# ── TEST 3: Zero price is rejected ───────────────────
def test_zero_price_rejected():
    df = make_row(price=0)
    good_df, bad_df = validate_dataframe(df, "test_supplier")
    assert len(bad_df) == 1, "Row with zero price should be quarantined"


# ── TEST 4: Missing quantity is rejected ─────────────
def test_missing_quantity_rejected():
    df = make_row(quantity=None)
    good_df, bad_df = validate_dataframe(df, "test_supplier")
    assert len(bad_df) == 1, "Row with null quantity should be quarantined"


# ── TEST 5: Blank product name is rejected ───────────
def test_blank_product_name_rejected():
    df = make_row(product="")
    good_df, bad_df = validate_dataframe(df, "test_supplier")
    assert len(bad_df) == 1, "Row with empty product name should be quarantined"


# ── TEST 6: Multiple bad rows counted correctly ──────
def test_multiple_bad_rows():
    rows = pd.concat([
        make_row(),               # valid
        make_row(price=-100),     # bad
        make_row(quantity=None),  # bad
        make_row(),               # valid
    ], ignore_index=True)
    good_df, bad_df = validate_dataframe(rows, "test_supplier")
    assert len(good_df) == 2, "Should have 2 valid rows"
    assert len(bad_df) == 2, "Should have 2 quarantined rows"
