
import os
import pdfplumber
import pandas as pd

# Root folder

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "penalties.csv")



def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def parse_decision(text, file_name):
    """
    This function extracts structured fields from the PDF text.
    You will refine this as you learn FIA formats.
    """

    data = {
        "Date": None,
        "Event": None,
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

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if "Date" in line:
            data["Date"] = line.replace("Date:", "").strip()

        elif "Event" in line:
            data["Event"] = line.replace("Event:", "").strip()

        elif "Session" in line:
            data["Session"] = line.replace("Session:", "").strip()

        elif "Time" in line:
            data["Time"] = line.replace("Time:", "").strip()

        elif "Competitor" in line or "Team" in line:
            data["Team"] = line.split(":")[-1].strip()

        elif "Driver" in line:
            data["Driver Name"] = line.split(":")[-1].strip()

        elif "Car" in line:
            data["Car #"] = line.split(":")[-1].strip()

        elif "Decision" in line:
            data["Decision"] = line.split(":")[-1].strip()

        elif "Offence" in line:
            data["Offence"] = line.split(":")[-1].strip()

        elif "Breach" in line or "Regulation" in line:
            data["Regulation"] = line.split(":")[-1].strip()

        elif "Reason" in line:
            data["Reason"] = line.split(":")[-1].strip()

    # Fallback: create Decision Number from file name
    data["Decision Number"] = file_name.replace(".pdf", "")

    return data



def process_all_pdfs():
    print("✅ Parser started")

    all_records = []

    for root, dirs, files in os.walk(RAW_DATA_PATH):
        print(f"📁 Checking folder: {root}")

        for file in files:
            print(f"📄 Found file: {file}")

            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)

                try:
                    text = extract_text_from_pdf(pdf_path)

                    if not text or text.strip() == "":
                        print(f"⚠️ Empty PDF: {file}")
                        continue

                    parsed = parse_decision(
                        text,
                        file_name=file,
                        folder_name=os.path.basename(root)
                    )

                    print(f"✅ Parsed: {parsed}")

                    all_records.append(parsed)

                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")


    df = pd.DataFrame(all_records)

    # Save output
    os.makedirs("data/processed", exist_ok=True)

    
    import pandas as pd
    
    df = pd.DataFrame(all_records)
    
    print(f"📊 Total records collected: {len(df)}")
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"✅ CSV successfully saved at: {OUTPUT_PATH}")


    print(f"\n✅ Data saved to {OUTPUT_PATH}")



