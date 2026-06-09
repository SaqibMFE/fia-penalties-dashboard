import streamlit as st
import sys
import os
import pandas as pd

# ✅ FULL WIDTH
st.set_page_config(layout="wide")

# ✅ Fix import path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from src.pdf_parser import process_all_pdfs

# ✅ Data path
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")

st.title("FIA Penalties Dashboard")

# -------------------------------
# ✅ CLASSIFY PENALTIES
# -------------------------------
def classify_penalty(decision_text):
    if pd.isna(decision_text):
        return "Other"

    text = decision_text.lower()

    if "5" in text and "second" in text and "time" in text and "penalty" in text:
        return "5 Second Time Penalty"

    if "10" in text and "second" in text and "time" in text and "penalty" in text:
        return "10 Second Time Penalty"

    if "drive through" in text:
        return "Drive Through"

    if "grid" in text:
        return "Grid Penalty"

    if "fine" in text:
        return "Fine"

    if "reprimand" in text:
        return "Reprimand"

    return "Other"


# ✅ Generate dataset if needed
if not os.path.exists(DATA_PATH):
    st.write("⚙️ Generating dataset from PDFs...")
    process_all_pdfs()

# ✅ Load data
if os.path.exists(DATA_PATH):

    df = pd.read_csv(DATA_PATH)

    # ✅ Add penalty type
    df["Penalty Type"] = df["Decision"].apply(classify_penalty)

    st.success("✅ Data loaded successfully")
    st.write(f"Total records: {len(df)}")

    # -------------------------------
    # ✅ FILTERS (UPDATED ✅)
    # -------------------------------
    st.subheader("🔎 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        event_filter = st.multiselect("Event", df["Event"].dropna().unique())
        session_filter = st.multiselect("Session", df["Session"].dropna().unique())

    with col2:
        team_filter = st.multiselect("Team", df["Team"].dropna().unique())
        driver_filter = st.multiselect("Driver Name", df["Driver Name"].dropna().unique())

    with col3:
        decision_filter = st.multiselect("Decision", df["Decision"].dropna().unique())

    # ✅ Apply filters
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
        filtered_df = filtered_df[filtered_df["Decision"].isin(decision_filter)]

    # -------------------------------
    # ✅ TABS
    # -------------------------------
    tab1, tab2 = st.tabs(["📋 Data", "📊 Analysis"])

    # =======================================
    # ✅ TAB 1 — TABLE
    # =======================================
    with tab1:

        st.markdown("## 📊 Filtered Data")

        display_df = filtered_df.copy()

        # ✅ Fix types
        if "Car #" in display_df.columns:
            display_df["Car #"] = display_df["Car #"].astype(str).replace("nan", "")

        if "Decision Number" in display_df.columns:
            display_df["Decision Number"] = display_df["Decision Number"].astype(str)

        if "Date" in display_df.columns:
            display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce")

        if "Time" in display_df.columns:
            display_df["Time"] = display_df["Time"].astype(str)

        # ✅ Table
        st.data_editor(
            display_df,
            use_container_width=True,
            height=650,
            column_config={
                "Event": st.column_config.TextColumn("Event", width="small"),
                "Date": st.column_config.DateColumn("Date", width="small"),
                "Session": st.column_config.TextColumn("Session", width="small"),
                "Time": st.column_config.TextColumn("Time", width="small"),
                "Team": st.column_config.TextColumn("Team", width="medium"),
                "Driver Name": st.column_config.TextColumn("Driver", width="medium"),
                "Car #": st.column_config.TextColumn("Car #", width="small"),
                "Decision Number": st.column_config.TextColumn("Decision #", width="small"),
                "Offence": st.column_config.TextColumn("Offence", width="large"),
                "Decision": st.column_config.TextColumn("Decision", width="large"),
                "Reason": st.column_config.TextColumn("Reason", width="large"),
            },
            disabled=True,
        )

        # ✅ Download
        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download filtered data",
            data=csv,
            file_name="filtered_penalties.csv",
            mime="text/csv",
        )

    # =======================================
    # ✅ TAB 2 — ANALYTICS
    # =======================================
    with tab2:

        st.markdown("## 📊 Analytics & Insights")

        # ✅ KPIs
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Decisions", len(filtered_df))
        col2.metric("Unique Drivers", filtered_df["Driver Name"].nunique())
        col3.metric("Unique Teams", filtered_df["Team"].nunique())

        # -------------------------------
        # ✅ GRAPH 1
        # -------------------------------
        st.subheader("📈 Graph 1")

        colA, colB = st.columns(2)

        with colA:
            x_axis1 = st.selectbox("X-axis (Graph 1)", filtered_df.columns, key="x1")

        with colB:
            metric1 = st.selectbox(
                "Penalty Type (Graph 1)",
                filtered_df["Penalty Type"].unique(),
                key="m1"
            )

        data1 = filtered_df[filtered_df["Penalty Type"] == metric1]

        if not data1.empty:
            graph1_data = data1[x_axis1].value_counts().reset_index()
            graph1_data.columns = [x_axis1, "Count"]

            st.bar_chart(graph1_data.set_index(x_axis1))

        # -------------------------------
        # ✅ GRAPH 2
        # -------------------------------
        st.subheader("📉 Graph 2")

        colC, colD = st.columns(2)

        with colC:
            x_axis2 = st.selectbox("X-axis (Graph 2)", filtered_df.columns, key="x2")

        with colD:
            metric2 = st.selectbox(
                "Penalty Type (Graph 2)",
                filtered_df["Penalty Type"].unique(),
                key="m2"
            )

        data2 = filtered_df[filtered_df["Penalty Type"] == metric2]

        if not data2.empty:
            graph2_data = data2[x_axis2].value_counts().reset_index()
            graph2_data.columns = [x_axis2, "Count"]

            st.bar_chart(graph2_data.set_index(x_axis2))

else:
    st.error("❌ CSV not found")
