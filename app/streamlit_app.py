import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



import pandas as pd
import os


import os
from src.pdf_parser import process_all_pdfs

if not os.path.exists("data/processed/penalties.csv"):
    process_all_pdfs()

import pdfplumber
st.write("✅ pdfplumber is installed and working")
