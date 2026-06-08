import os
import pandas as pd
import pdfplumber
import re

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
# CLEAN HELPERS
# -------------------------------
def clean_driver(driver_line):
    if not driver_line:
        return None

    # Remove bracket info and car numbers
    driver_line = re.sub(r"\(.*?\)", "", driver_line)
    driver_line = re.sub(r"No\.?\s*\d+", "", driver_line)

    return driver_line.strip()


# -------------------------------
# CORE PARSER (REAL FIX)
# -------------------------------
def parse_decision(text, file_name, folder_name):

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    data = {
        "Event": folder_name,
        "Date": None,
        "Session": None,
        "Time": None,
        "Team": None,
        "Driver Name": None,
        "Car #": None,
        "Decision Number": None,
        "Offence": None,
        "Regulation": None,
        "Decision": None,
        "Reason": None,
    }

    # ✅ 1. DECISION NUMBER (FIXED)
    for line in lines:
        if "Decision No" in line:
            match = re.search(r"Decision\s*No\.?\s*(\d+)", line)
            if match:
                data["Decision Number"] = match.group(1)
            break

    # ✅ 2. DATE / SESSION / TIME
    for line in lines:
        if line.startswith("Date"):
            data["Date"] = line.split(":", 1)[-1].strip()

        elif line.startswith("Session"):
            data["Session"] = line.split(":", 1)[-1].strip()

        elif line.startswith("Time"):
            data["Time"] = line.split(":", 1)[-1].strip()

    # ✅ 3. TRACK LIMITS / MULTIPLE
    if "track limits" in text.lower():
        data["Team"] = "Multiple"
        data["Driver Name"] = "Multiple"

    # ✅ 4. TEAM
    for line in lines:
        if line.startswith("Competitor"):
            data["Team"] = line.split(":", 1)[-1].strip()
            break

    # ✅ 5. DRIVER + CAR
    for line in lines:
        if line.startswith("Driver"):
            driver_line = line.split(":", 1)[-1].strip()

            # Extract car number FROM SAME LINE if present
            car_match = re.search(r"\b(\d{1,3})\b", driver_line)

            if car_match:
                data["Car #"] = car_match.group(1)

            data["Driver Name"] = clean_driver(driver_line)
            break

    # ✅ Backup car extraction if missed
    if not data["Car #"]:
        for line in lines:
            if line.startswith("Car"):
                match = re.search(r"(\d+)", line)
                if match:
                    data["Car #"] = match.group(1)
                break

    # ✅ 6. OFFENCE (REAL FIX)
    for i, line in enumerate(lines):
        if line.startswith("Offence") or line.startswith("Incident"):
            data["Offence"] = line.split(":", 1)[-1].strip()
            break

    # ✅ 7. REGULATION
    for line in lines:
        if line.startswith("Breach") or line.startswith("Regulation"):
            data["Regulation"] = line.split(":", 1)[-1].strip()
            break

    # ✅ 8. DECISION (REAL FIX — must NOT use Decision No)
    for line in lines:
        if line.startswith("Decision:"):
            data["Decision"] = line.split(":", 1)[-1].strip()
            break

    # ✅ 9. REASON (works already)
    for i, line in enumerate(lines):
        if line.startswith("Reason"):
            data["Reason"] = line.split(":", 1)[-1].strip()
            break

    return data


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def process_all_pdfs():

    all_records = []

    for root, dirs, files in os.walk(RAW_DATA_PATH):
        for file in files:

            if file.lower().endswith(".pdf"):

                pdf_path = os.path.join(root, file)

                try:
                    text = extract_text_from_pdf(pdf_path)

                    if not text.strip():
                        continue

                    parsed = parse_decision(
                        text,
                        file_name=file,
                        folder_name=os.path.basename(root),
                    )

                    all_records.append(parsed)

                except Exception as e:
                    print(f"Error: {file} -> {e}")

    df = pd.DataFrame(all_records)

    # ✅ SORTING FIX (already working correctly)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    df = df.sort_values(by=["Date", "Time"])

    # ✅ COLUMN ORDER FIX
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
            "Regulation",
            "Decision",
            "Reason",
        ]
    ]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
