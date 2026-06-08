import os
import pandas as pd
import pdfplumber
import re

# ✅ Set correct base directory
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
        print(f"❌ Error reading PDF: {pdf_path} -> {e}")

    return text


# ✅ Helper function for regex
def extract(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# ✅ Parse FIA decision
def parse_decision(text, file_name, folder_name):
    return {
        "Date": extract(r"Date\s*[:\-]?\s*(.+)", text),
        "Event": folder_name,
        "Session": extract(r"Session\s*[:\-]?\s*(.+)", text),
        "Time": extract(r"Time\s*[:\-]?\s*(.+)", text),
        "Team": extract(r"(Competitor|Team)\s*[:\-]?\s*(.+)", text),
        "Driver Name": extract(r"Driver\s*[:\-]?\s*(.+)", text),
        "Car #": extract(r"Car\s*#?\s*[:\-]?\s*(\d+)", text),
        "Decision Number": file_name.replace(".pdf", ""),
        "Offence": extract(r"(Offence|Incident)\s*[:\-]?\s*(.+)", text),
        "Regulation": extract(r"(Breach|Regulation)\s*[:\-]?\s*(.+)", text),
        "Decision": extract(r"Decision\s*[:\-]?\s*(.+)", text),
        "Reason": extract(r"Reason\s*[:\-]?\s*(.+)", text),
    }


# ✅ Main function
def process_all_pdfs():
    print("✅ Parser started")

    all_records = []

    # Walk through all folders
    for root, dirs, files in os.walk(RAW_DATA_PATH):
        print(f"📁 Checking folder: {root}")

        for file in files:
            print(f"📄 Found file: {file}")

            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)

                try:
                    text = extract_text_from_pdf(pdf_path)

                    # ✅ Check empty text
                    if not text or text.strip() == "":
                        print(f"⚠️ Empty PDF text: {file}")
                        continue

                    # ✅ Show preview (first 300 chars)
                    print("------ TEXT PREVIEW ------")
                    print(text[:300])
                    print("--------------------------")

                    # ✅ Parse data
                    parsed = parse_decision(
                        text,
                        file_name=file,
                        folder_name=os.path.basename(root)
                    )

                    print(f"✅ Parsed result: {parsed}")

                    all_records.append(parsed)

                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")

    # ✅ If nothing parsed → add fallback row
    if len(all_records) == 0:
        print("⚠️ No records found — inserting test row")

        all_records.append({
            "Date": "DEBUG",
            "Event": "DEBUG",
            "Session": "DEBUG",
            "Time": "DEBUG",
            "Team": "DEBUG",
            "Driver Name": "DEBUG",
            "Car #": "0",
            "Decision Number": "DEBUG",
            "Offence": "DEBUG",
            "Regulation": "DEBUG",
            "Decision": "DEBUG",
            "Reason": "DEBUG"
        })

    # ✅ Create dataframe
    df = pd.DataFrame(all_records)

    print(f"📊 Total records collected: {len(df)}")

    # ✅ Save CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ CSV saved at: {OUTPUT_PATH}")
