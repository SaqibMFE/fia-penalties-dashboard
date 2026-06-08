import os
import pandas as pd
import pdfplumber
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")


# -------------------------------
# READ PDF
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
# DRIVER + CAR (ROBUST FIX)
# -------------------------------
def extract_driver_and_car(text):

    # Handles line breaks + flexible spacing
    match = re.search(
        r"N[°o]\s*/\s*Driver\s*:\s*(\d+)\s*/\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if match:
        car = match.group(1).strip()

        # Remove everything after "Competitor"
        driver = re.split(r"Competitor", match.group(2))[0].strip()

        return car, driver

    return None, None


# -------------------------------
# TEAM (ROBUST)
# -------------------------------
def extract_team(text):

    match = re.search(r"Competitor\s*:\s*(.*)", text)

    if match:
        value = match.group(1)

        # stop at next known field
        value = re.split(r"(Session|Time|Fact)", value)[0].strip()

        return value

    return None


# -------------------------------
# SESSION (ROBUST)
# -------------------------------
def extract_session(text):

    match = re.search(r"Session\s*:\s*(.*)", text)

    if match:
        value = match.group(1)
        value = re.split(r"(Time|Fact)", value)[0].strip()
        return value

    return None


# -------------------------------
# TIME (FACT ONLY ✅)
# -------------------------------
def extract_time(text):

    match = re.search(r"Time\s*\(fact\)\s*:\s*([\d:]+)", text, re.IGNORECASE)

    if match:
        return match.group(1)

    return None


# -------------------------------
# DATE (BOTTOM BLOCK)
# -------------------------------
def extract_date(text):
    match = re.search(r"Date\s*:\s*(.*)", text)
    return match.group(1).strip() if match else None


# -------------------------------
# DECISION NUMBER
# -------------------------------
def extract_decision_number(text):
    match = re.search(r"Decision\s*no\.?\s*(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


# -------------------------------
# SECTIONS
# -------------------------------
def extract_sections(text):

    offence = re.search(r"Offence\s*:\s*(.*)", text)
    decision = re.search(r"Decision\s*:\s*(.*)", text)
    reason = re.search(r"Reason\s*:\s*(.*)", text)

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

    car, driver = extract_driver_and_car(text)
    team = extract_team(text)
    session = extract_session(text)
    time = extract_time(text)

    # ✅ TRACK LIMITS FIX
    if "track limits" in lower:
        driver = "Multiple"
        team = "Multiple"

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

    # ✅ CLEAN TIME
    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.time

    # ✅ CLEAN DATE
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.sort_values(by=["Date", "Time"])

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
