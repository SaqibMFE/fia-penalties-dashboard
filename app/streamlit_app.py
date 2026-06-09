import streamlit as st
import sys
import os
import pandas as pd

# ✅ Fix import path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from src.pdf_parser import process_all_pdfs

# ✅ Data path
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")

st.title("FIA Penalties Dashboard")

# ✅ Generate dataset if needed
if not os.path.exists(DATA_PATH):
    st.write("⚙️ Generating dataset from PDFs...")
    process_all_pdfs()

# ✅ Load data
if os.path.exists(DATA_PATH):

    df = pd.read_csv(DATA_PATH)

    st.success("✅ Data loaded successfully")
    st.write(f"Total records: {len(df)}")

    # -------------------------------
    # ✅ FILTERS (TOP SECTION)
    # -------------------------------
    st.subheader("🔎 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        event_filter = st.multiselect(
            "Event",
            options=df["Event"].dropna().unique()
        )

        session_filter = st.multiselect(
            "Session",
            options=df["Session"].dropna().unique()
        )

    with col2:
        team_filter = st.multiselect(
            "Team",
            options=df["Team"].dropna().unique()
        )

        driver_filter = st.multiselect(
            "Driver Name",
            options=df["Driver Name"].dropna().unique()
        )

    with col3:
        decision_filter = st.multiselect(
            "Decision Number",
            options=df["Decision Number"].dropna().unique()
        )

    # -------------------------------
    # ✅ APPLY FILTERS
    # -------------------------------
    filtered_df = df.copy()

    if event_filter:
        filtered_df = filtered_df[filtered_df["Event"].isin(event_filter)]

    if session_filter:
        filtered_df = filtered_df[filtered_df["Session"].isin(session_filter)]

    if team_filter:
        filtered_df = filtered_df[filtered_df["Team"].isin(team_filter)]

    if driver_filter:
        filtered_df = filtered_df[filtered_df["Driver Name"].isin(driver_filter)]

    if decision_filter:
        filtered_df = filtered_df[filtered_df["Decision Number"].isin(decision_filter)]

    # -------------------------------
    # ✅ DISPLAY TABLE
    # -------------------------------
    st.subheader("📊 Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)

    # ✅ Download button
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download filtered CSV",
        data=csv,
        file_name="filtered_penalties.csv",
        mime="text/csv",
    )

else:
    st.error("❌ CSV not found")
