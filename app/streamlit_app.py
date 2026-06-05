
import streamlit as st
import pandas as pd
import os


import os
from src.pdf_parser import process_all_pdfs

if not os.path.exists("data/processed/penalties.csv"):
    process_all_pdfs()

import pdfplumber
st.write("✅ pdfplumber is installed and working")
