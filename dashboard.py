"""
dashboard.py - CleanSweep Pipeline Dashboard

A Streamlit web app that shows:
  - Pipeline summary metrics
  - Rows per supplier (bar chart)
  - Quarantine table (bad rows with reasons)
  - Pipeline run history

Run with: streamlit run dashboard.py
"""

import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="CleanSweep Dashboard",
    page_icon="🧹",
    layout="wide"
)

# Connect to DuckDB
project_root = Path(__file__).parent
db_path = str(project_root / "data" / "cleansweep.duckdb")

# ── Title ──────────────────────────────────────────
st.title("🧹 CleanSweep Pipeline Dashboard")
st.caption("Real-time view of your data ingestion pipeline")
st.divider()

# ── Load data from DuckDB ───────────────────────────
@st.cache_data
def load_data():
    con = duckdb.connect(db_path, read_only=True)
    all_suppliers = con.execute("SELECT * FROM main_conformed.all_suppliers").df()
    quarantine    = con.execute("SELECT * FROM quarantine.bad_rows").df()
    run_log       = con.execute("SELECT * FROM observability.pipeline_runs").df()
    con.close()
    return all_suppliers, quarantine, run_log

all_df, quarantine_df, run_log_df = load_data()

# ── Key Metrics ─────────────────────────────────────
st.subheader("📊 Pipeline Summary")

col1, col2, col3, col4 = st.columns(4)

total_rows = len(all_df)
quarantine_count = len(quarantine_df)
supplier_count = all_df["supplier_id"].nunique()
pass_rate = round((total_rows / (total_rows + quarantine_count)) * 100, 1)

col1.metric("✅ Valid Rows", total_rows)
col2.metric("❌ Quarantined Rows", quarantine_count)
col3.metric("🏭 Suppliers Loaded", supplier_count)
col4.metric("📈 Pass Rate", f"{pass_rate}%")

st.divider()

# ── Charts ──────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("📦 Rows per Supplier")
    supplier_counts = all_df.groupby("supplier_id").size().reset_index(name="rows")
    st.bar_chart(supplier_counts.set_index("supplier_id"))

with right:
    st.subheader("⚠️ Quarantine Reasons")
    if len(quarantine_df) > 0:
        reason_counts = quarantine_df.groupby("quarantine_reason").size().reset_index(name="count")
        st.bar_chart(reason_counts.set_index("quarantine_reason"))
    else:
        st.success("No quarantined rows!")

st.divider()

# ── Quarantine Table ─────────────────────────────────
st.subheader("🚫 Quarantined Rows")
if len(quarantine_df) > 0:
    st.dataframe(
        quarantine_df[["product_name", "quarantine_reason", "quarantined_at"]],
        use_container_width=True
    )
else:
    st.success("No quarantined rows — data is clean!")

st.divider()

# ── Run Log ─────────────────────────────────────────
st.subheader("🕐 Pipeline Run History")
if len(run_log_df) > 0:
    st.dataframe(run_log_df, use_container_width=True)
else:
    st.info("No pipeline runs logged yet.")

