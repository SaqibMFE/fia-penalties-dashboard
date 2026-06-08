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
# MAIN LINE (PRIMARY METHOD)
# -------------------------------
def extract_main_line(text):

    pattern = re.search(
        r"N[°o]\s*/\s*Driver:\s*(\d+)\s*/\s*(.*?)\s+Competitor:\s*(.*?)\s+Session:\s*(.*?)\s+Time\s*\(fact\):\s*([\d:]+)",
        text,
        re.IGNORECASE
    )

    if pattern:
        return (
            pattern.group(1).strip(),  # car
            pattern.group(2).strip(),  # driver
            pattern.group(3).strip(),  # team
            pattern.group(4).strip(),  # session
            pattern.group(5).strip(),  # time
        )

    return None, None, None, None, None


# -------------------------------
# FALLBACK DRIVER + CAR
# -------------------------------
def fallback_driver_car(text):

    # fallback when line breaks differently
    match = re.search(
        r"N[°o]\s*/\s*Driver:\s*(\d+)\s*/\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if match:
        car = match.group(1).strip()

        # remove trailing stuff like Competitor:
        driver = re.split(r"Competitor:", match.group(2))[0].strip()

        return car, driver

    return None, None


# -------------------------------
# DECISION NUMBER
# -------------------------------
def extract_decision_number(text):
    match = re.search(r"Decision\s*no\.?\s*(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


# -------------------------------
# DATE
# -------------------------------
def extract_date(text):
    match = re.search(r"Date:\s*(.*)", text)
    return match.group(1).strip() if match else None


# -------------------------------
# SECTIONS
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

    if "track limits" in lower:
        car, driver, team, session, time = None, "Multiple", "Multiple", None, None

    else:
        car, driver, team, session, time = extract_main_line(text)

        # ✅ fallback if main fails
        if not driver or not car:
            fallback_car, fallback_driver = fallback_driver_car(text)
            car = car or fallback_car
            driver = driver or fallback_driver

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

    # ✅ TIME CLEANING
    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce").dt.time

    # ✅ DATE CLEANING
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
