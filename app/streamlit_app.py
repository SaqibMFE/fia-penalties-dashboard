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
    # ✅ PREMIUM TABLE DESIGN
    # -------------------------------
    
    st.markdown("## 📊 Filtered Data")
    
    # ✅ Format dataframe for display
    display_df = filtered_df.copy()
    
    # Format Date
    if "Date" in display_df.columns:
        display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce").dt.strftime("%d %b %Y")
    
    # Format Time
    if "Time" in display_df.columns:
        display_df["Time"] = pd.to_datetime(display_df["Time"], errors="coerce").dt.strftime("%H:%M")
    
    # -------------------------------
    # ✅ STYLING (THE KEY PART)
    # -------------------------------
    styled_df = display_df.style \
        .set_properties(**{
            "text-align": "left",
            "white-space": "normal"
        }) \
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("font-size", "14px"),
                    ("text-align", "left"),
                    ("background-color", "#111111"),
                    ("color", "white"),
                    ("padding", "8px")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "6px"),
                    ("font-size", "13px")
                ]
            }
        ]) \
        .highlight_max(subset=["Decision"], color="#ffeeba") \
        .set_properties(subset=["Offence"], **{
            "max-width": "300px"
        }) \
        .set_properties(subset=["Reason"], **{
            "max-width": "400px"
        })
    
    # -------------------------------
    # ✅ DISPLAY TABLE
    # -------------------------------
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=600
    )
