import os
import pandas as pd
import pdfplumber
import re

# ✅ Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")


# -------------------------------
# PDF TEXT EXTRACTION
# -------------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


# -------------------------------
# DRIVER + CAR EXTRACTION
# -------------------------------
def extract_driver_and_car(text):
    match = re.search(
        r"N[°o]\s*/\s*Driver\s*\n?\s*(\d+)\s*/\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        car = match.group(1).strip()
        driver = match.group(2).strip()
        return car, driver

    return None, None


# -------------------------------
# DECISION NUMBER
# -------------------------------
def extract_decision_number(text):
    match = re.search(r"Decision\s*No\.?\s*(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


# -------------------------------
# TEAM
# -------------------------------
def extract_team(text):
    match = re.search(r"Competitor\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# -------------------------------
# META (DATE / SESSION / TIME)
# -------------------------------
def extract_meta(text):

    date = re.search(r"Date\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    session = re.search(r"Session\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    time = re.search(r"Time\s*[:\-]?\s*(.*)", text, re.IGNORECASE)

    return (
        date.group(1).strip() if date else None,
        session.group(1).strip() if session else None,
        time.group(1).strip() if time else None,
    )


# -------------------------------
# SECTIONS (OFFENCE / DECISION / REASON)
# -------------------------------
def extract_sections(text):

    offence = re.search(r"Offence\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    decision = re.search(r"Decision\s*[:\-]\s*(.*)", text, re.IGNORECASE)
    reason = re.search(r"Reason\s*[:\-]?\s*(.*)", text, re.IGNORECASE)

    return (
        offence.group(1).strip() if offence else None,
        decision.group(1).strip() if decision else None,
        reason.group(1).strip() if reason else None,
    )


# -------------------------------
# MAIN PARSER
# -------------------------------
def parse_decision(text, filename, folder):

    lower = text.lower()

    # ✅ MULTIPLE CASE
    if "track limits" in lower:
        car = None
        driver = "Multiple"
        team = "Multiple"
    else:
        car, driver = extract_driver_and_car(text)
        team = extract_team(text)

    decision_number = extract_decision_number(text)

    offence, decision, reason = extract_sections(text)

    date, session, time = extract_meta(text)

    return {
        "Event": folder,
        "Date": date,
        "Session": session,
        "Time": time,
        "Team": team,
        "Driver Name": driver,
        "Car #": car,
        "Decision Number": decision_number,
        "Offence": offence,
        "Decision": decision,
        "Reason": reason,
    }


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def process_all_pdfs():

    all_records = []

    for root, _, files in os.walk(RAW_DATA_PATH):

        event = os.path.basename(root)

        for file in files:

            if file.lower().endswith(".pdf"):

                path = os.path.join(root, file)

                try:
                    text = extract_text_from_pdf(path)

                    if not text.strip():
                        continue

                    row = parse_decision(text, file, event)

                    all_records.append(row)

                except Exception as e:
                    print(f"Error processing {file}: {e}")

    # ✅ CREATE DATAFRAME SAFELY
    df = pd.DataFrame(all_records)

    if df.empty:
        print("⚠️ No data extracted")
        return df

    # ✅ SAFE DATE + TIME HANDLING
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    # ✅ SORT (only if columns exist)
    if "Date" in df.columns and "Time" in df.columns:
        df = df.sort_values(by=["Date", "Time"], na_position="last")

    # ✅ SAFE COLUMN ORDERING
    columns_order = [
        "Event",
        "Date",
        "Session",
        "Time",
        "Team",
        "Driver Name",
        "Car #",
        "Decision Number",
        "Offence",
        "Decision",
        "Reason",
    ]

    df = df[[col for col in columns_order if col in df.columns]]

    # ✅ SAVE CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ CSV saved with {len(df)} rows")

    return df
