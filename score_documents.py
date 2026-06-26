import os
import math
import fitz
import pandas as pd

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

DATASET_DIR = str(PROJECT_ROOT / "data/dataset/rbi")
EXCEL_FILE = str(PROJECT_ROOT / "dataset_inventory.xlsx")

MAX_PAGES_TO_READ = 20

# ==================================================
# KEYWORDS
# ==================================================

COMPLIANCE_KEYWORDS = {
    "shall": 4,
    "must": 4,
    "required": 3,
    "compliance": 5,
    "regulatory": 4,
    "regulated entity": 5,
    "guidelines": 3,
    "framework": 3,
    "direction": 4,
    "audit": 3,
    "monitoring": 3,
    "risk": 3,
    "governance": 3,
    "reporting": 3,
    "oversight": 3,
    "obligation": 4,
    "policy": 2
}

CYBER_KEYWORDS = {
    "cyber": 10,
    "cybersecurity": 10,
    "information security": 8,
    "security": 5,
    "authentication": 6,
    "digital": 4,
    "fraud": 6,
    "encryption": 8,
    "network": 4,
    "incident": 5,
    "threat": 5,
    "vulnerability": 6,
    "account aggregator": 8,
    "digital rupee": 6,
    "payment system": 6
}

KYC_KEYWORDS = {
    "kyc": 15,
    "know your customer": 15,
    "customer due diligence": 12,
    "cdd": 8,
    "beneficial owner": 10,
    "customer identification": 10,
    "ckycr": 10,
    "video kyc": 12,
    "customer onboarding": 8
}

AML_KEYWORDS = {
    "aml": 15,
    "money laundering": 15,
    "anti money laundering": 15,
    "suspicious transaction": 12,
    "str": 8,
    "ctr": 8,
    "fatf": 10,
    "pmla": 12,
    "terrorist financing": 12,
    "enhanced due diligence": 10
}

NEGATIVE_KEYWORDS = {
    "speech": -10,
    "annual report": -8,
    "survey": -8,
    "bulletin": -8,
    "reappointment": -12,
    "meeting": -10,
    "transcript": -10,
    "statistical return": -8
}

# ==================================================
# TEXT EXTRACTION
# ==================================================

def extract_text_and_pages(pdf_path):

    try:

        doc = fitz.open(pdf_path)

        page_count = len(doc)

        text = ""

        pages_to_read = min(page_count, MAX_PAGES_TO_READ)

        for page_num in range(pages_to_read):
            page = doc[page_num]
            text += page.get_text()

        doc.close()

        return text.lower(), page_count

    except Exception as e:

        print(f"Error reading: {pdf_path}")
        print(e)

        return "", 0


# ==================================================
# SCORING
# ==================================================

def calculate_score(text, keyword_dict):

    score = 0

    for keyword, weight in keyword_dict.items():

        count = text.count(keyword)

        if count > 0:
            score += weight * (1 + math.log(count))

    return score


def normalize(score):

    return min(round(score), 100)


# ==================================================
# LOAD INVENTORY
# ==================================================

df = pd.read_excel(EXCEL_FILE)

# ==================================================
# PROCESS FILES
# ==================================================

total_files = len(df)

for idx, row in df.iterrows():

    category = str(row["Category"])
    filename = str(row["File Name"])

    pdf_path = os.path.join(
        DATASET_DIR,
        category,
        filename
    )

    if not os.path.exists(pdf_path):

        print(f"Missing: {filename}")
        continue

    print(
        f"[{idx+1}/{total_files}] Processing: {filename}"
    )

    text, pages = extract_text_and_pages(pdf_path)

    compliance_score = calculate_score(
        text,
        COMPLIANCE_KEYWORDS
    )

    cyber_score = calculate_score(
        text,
        CYBER_KEYWORDS
    )

    kyc_score = calculate_score(
        text,
        KYC_KEYWORDS
    )

    aml_score = calculate_score(
        text,
        AML_KEYWORDS
    )

    penalty = calculate_score(
        text,
        NEGATIVE_KEYWORDS
    )

    compliance_score += penalty

    compliance_score = normalize(max(compliance_score, 0))
    cyber_score = normalize(max(cyber_score, 0))
    kyc_score = normalize(max(kyc_score, 0))
    aml_score = normalize(max(aml_score, 0))

    overall_priority = round(
        (
            0.40 * compliance_score
            + 0.20 * cyber_score
            + 0.20 * kyc_score
            + 0.20 * aml_score
        ),
        2
    )

    df.at[idx, "Compliance Score"] = compliance_score
    df.at[idx, "Cyber Score"] = cyber_score
    df.at[idx, "KYC Score"] = kyc_score
    df.at[idx, "AML Score"] = aml_score
    df.at[idx, "Overall Priority"] = overall_priority
    df.at[idx, "Pages"] = pages

# ==================================================
# SAVE
# ==================================================

df.to_excel(EXCEL_FILE, index=False)

print()
print("=" * 60)
print("SCORING COMPLETED")
print(f"Updated: {EXCEL_FILE}")
print("=" * 60)
