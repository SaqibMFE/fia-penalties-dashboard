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
    # ✅ PREMIUM TABLE DISPLAY
    # -------------------------------
    
    st.markdown("## 📊 Filtered Data")
    
    # ✅ Format display copy
    display_df = filtered_df.copy()
    
    # Format Date
    if "Date" in display_df.columns:
        display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce")
    
    # Format Time
    if "Time" in display_df.columns:
        display_df["Time"] = display_df["Time"].astype(str)
    
    # -------------------------------
    # ✅ REAL UI IMPROVEMENT
    # -------------------------------
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
    
        disabled=True,  # read-only table
    )
      
        
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

# -------------------------------
# ✅ CREATE TABS
# -------------------------------
tab1, tab2 = st.tabs(["📋 Data", "📊 Analysis"])

# -------------------------------
# ✅ TAB 1 (YOUR EXISTING TABLE)
# -------------------------------
with tab1:
    st.markdown("## 📊 Filtered Data")

    st.data_editor(
        filtered_df,
        use_container_width=True,
        height=650,
        disabled=True
    )

# -------------------------------
# ✅ TAB 2 (NEW ANALYSIS)
# -------------------------------
with tab2:

    st.markdown("## 📊 Analytics & Insights")

    # -------------------------------
    # ✅ KPI SECTION
    # -------------------------------
    st.subheader("🔢 Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Decisions", len(filtered_df))
    col2.metric("Unique Drivers", filtered_df["Driver Name"].nunique())
    col3.metric("Unique Teams", filtered_df["Team"].nunique())

    # -------------------------------
    # ✅ GRAPH 1 CONTROLS
    # -------------------------------
    st.subheader("📈 Graph 1")

    colA, colB = st.columns(2)

    with colA:
        x_axis1 = st.selectbox(
            "Select X-axis (Graph 1)",
            options=filtered_df.columns,
            key="x1"
        )

    with colB:
        metric1 = st.selectbox(
            "Select Metric (Graph 1)",
            options=["Count"],
            key="m1"
        )

    # -------------------------------
    # ✅ GRAPH 1 DATA
    # -------------------------------
    if x_axis1:
        graph1_data = filtered_df[x_axis1].value_counts().reset_index()
        graph1_data.columns = [x_axis1, "Count"]

        st.bar_chart(graph1_data.set_index(x_axis1))

    # -------------------------------
    # ✅ GRAPH 2 CONTROLS
    # -------------------------------
    st.subheader("📉 Graph 2")

    colC, colD = st.columns(2)

    with colC:
        x_axis2 = st.selectbox(
            "Select X-axis (Graph 2)",
            options=filtered_df.columns,
            key="x2"
        )

    with colD:
        metric2 = st.selectbox(
            "Select Metric (Graph 2)",
            options=["Count"],
            key="m2"
        )

    # -------------------------------
    # ✅ GRAPH 2 DATA
    # -------------------------------
    if x_axis2:
        graph2_data = filtered_df[x_axis2].value_counts().reset_index()
        graph2_data.columns = [x_axis2, "Count"]

        st.bar_chart(graph2_data.set_index(x_axis2))
