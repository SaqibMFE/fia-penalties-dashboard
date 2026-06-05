import streamlit as st

import subprocess
import os

# Run parser if data does not exist
if not os.path.exists("data/processed/penalties.csv"):
    subprocess.run(["python", "src/pdf_parser.py"])


import pdfplumber
st.write("✅ pdfplumber loaded successfully")
