import os
import pandas as pd
import pdfplumber
import re

# ✅ Base paths (works in Streamlit Cloud)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")


# ✅ Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {pdf_path} -> {e}")
    return text


# ✅ Regex helper (SAFE dash handling)
def extract(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# ✅ Clean driver names
def clean_driver(driver_text):
    if not driver_text:
        return None
    driver_text = re.sub(r"\(.*?\)", "", driver_text)
    driver_text = re.sub(r"\d+$", "", driver_text)
    return driver_text.strip()


# ✅ Parse FIA decision
def parse_decision(text, file_name, folder_name):

    lower_text = text.lower()

    # ✅ MULTIPLE (track limits)
    if "track limits" in lower_text:
        team = "Multiple"
        driver = "Multiple"
        car_no = None
    else:
        team = extract(r"Competitor\s*[:\-]?\s*(.+)", text)

        driver_raw = extract(r"Driver\s*[:\-]?\s*(.+)", text)
        driver = clean_driver(driver_raw)

        car_match = re.search(r"Car\s*(No\.?|#)?\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
        car_no = car_match.group(2) if car_match else None

    # ✅ Decision Number (correct field)
    decision_number = extract(r"Decision\s*(No\.?|Number)\s*[:\-]?\s*(\d+)", text)

    # ✅ Offence
    offence = extract(r"(Offence|Incident)\s*[:\-]?\s*(.+)", text)

    # ✅ Regulation
    regulation = extract(r"(Breach|Regulation)\s*[:\-]?\s*(.+)", text)

    # ✅ Decision (stewards)
    decision_text = extract(r"Decision\s*[:\-]?\s*(.+)", text)

    # ✅ Reason
    reason = extract(r"Reason\s*[:\-]?\s*(.+)", text)

    # ✅ Meta
    date = extract(r"Date\s*[:\-]?\s*(.+)", text)
    session = extract(r"Session\s*[:\-]?\s*(.+)", text)
    time = extract(r"Time\s*[:\-]?\s*(.+)", text)

    return {
        "Event": folder_name,
        "Date": date,
        "Session": session,
        "Time": time,
        "Team": team,
        "Driver Name": driver,
        "Car #": car_no,
        "Decision Number": decision_number,
        "Offence": offence,
        "Regulation": regulation,
        "Decision": decision_text,
        "Reason": reason,
    }


# ✅ Main processing function
def process_all_pdfs():
    print("Parser started")

    all_records = []

    for root, dirs, files in os.walk(RAW_DATA_PATH):
        print(f"Checking folder: {root}")

        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)

                print(f"Processing: {file}")

                try:
                    text = extract_text_from_pdf(pdf_path)

                    if not text or text.strip() == "":
                        print(f"Empty PDF: {file}")
                        continue

                    parsed = parse_decision(
                        text,
                        file_name=file,
                        folder_name=os.path.basename(root)
                    )

                    all_records.append(parsed)

                except Exception as e:
                    print(f"Error processing {file}: {e}")

    # ✅ Prevent empty CSV
    if len(all_records) == 0:
        print("No records extracted — adding debug row")

        all_records.append({
            "Event": "DEBUG",
            "Date": "DEBUG",
            "Session": "DEBUG",
            "Time": "DEBUG",
            "Team": "DEBUG",
            "Driver Name": "DEBUG",
            "Car #": "0",
            "Decision Number": "DEBUG",
            "Offence": "DEBUG",
            "Regulation": "DEBUG",
            "Decision": "DEBUG",
            "Reason": "DEBUG",
        })

    df = pd.DataFrame(all_records)

    print(f"Total records: {len(df)}")

    # ✅ Convert and sort
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    df = df.sort_values(by=["Date", "Time"])

    # ✅ Reorder columns
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

    # ✅ Save CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"CSV saved at: {OUTPUT_PATH}")
