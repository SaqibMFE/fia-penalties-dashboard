import streamlit as st
import sys
import os
import pandas as pd

# ✅ Fix import path for src
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# ✅ Import parser
from src.pdf_parser import process_all_pdfs

# ✅ Correct absolute paths
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")

st.title("FIA Penalties Dashboard")

# ✅ Run parser if CSV does not exist
if not os.path.exists(DATA_PATH):
    st.write("⚙️ Generating dataset from PDFs...")
    process_all_pdfs()

# ✅ Try loading data
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)

    st.success("✅ Data loaded successfully")

    # Show basic info
    st.write("Total records:", len(df))
    st.dataframe(df)

else:
    st.error("❌ CSV file was not created. Check logs.")
