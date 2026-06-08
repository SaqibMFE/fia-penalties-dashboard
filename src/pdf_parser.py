import os
import pandas as pd
import pdfplumber
import re

# -------------------------------
# PATHS
# -------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")


# -------------------------------
# READ PDF TEXT
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
# MAIN LINE PARSING (CRITICAL FIX)
# -------------------------------
def extract_main_line(text):

    """
    Extracts:
    Car #
    Driver
    Team
    Session
    Time (FACT TIME ONLY)
    """

    match = re.search(
        r"N[°o]\s*/\s*Driver:\s*(\d+)\s*/\s*(.*?)\s+Competitor:\s*(.*?)\s+Session:\s*(.*?)\s+Time\s*\(fact\):\s*([\d:]+)",
        text,
        re.IGNORECASE
    )

    if match:
        car = match.group(1).strip()
        driver = match.group(2).strip()
        team = match.group(3).strip()
        session = match.group(4).strip()
        time = match.group(5).strip()

        return car, driver, team, session, time

    return None, None, None, None, None


# -------------------------------
# DECISION NUMBER
# -------------------------------
def extract_decision_number(text):
    match = re.search(r"Decision\s*no\.?\s*(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


# -------------------------------
# DATE (BOTTOM BLOCK)
# -------------------------------
def extract_date(text):
    match = re.search(r"Date:\s*(.*)", text)
    return match.group(1).strip() if match else None


# -------------------------------
# OFFENCE / DECISION / REASON
# -------------------------------
def extract_sections(text):

    offence = re.search(r"Offence:\s*(.*)", text)
    decision = re.search(r"Decision:\s*(.*)", text)
    reason = re.search(r"Reason:\s*(.*)", text)

    return (
        offence.group(1).strip() if offence else None,
        decision.group(1).strip() if decision else None,
        reason.group(1).strip() if reason else None,
    )


# -------------------------------
# PARSER
# -------------------------------
def parse_decision(text, filename, folder):

    lower = text.lower()

    # ✅ Multiple / track limits case
    if "track limits" in lower:
        car = None
        driver = "Multiple"
        team = "Multiple"
        session = None
        time = None
    else:
        car, driver, team, session, time = extract_main_line(text)

    decision_number = extract_decision_number(text)
    offence, decision, reason = extract_sections(text)
    date = extract_date(text)

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

    df = pd.DataFrame(all_records)

    if df.empty:
        return df

    # ✅ Correct datetime parsing
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce")

    df = df.sort_values(by=["Date", "Time"])

    # ✅ Final column order
    df = df[
        [
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
    ]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    return df
