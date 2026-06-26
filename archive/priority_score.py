import pandas as pd

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

EXCEL_FILE = str(PROJECT_ROOT / "dataset_inventory.xlsx")

# ==================================================
# LOAD EXCEL
# ==================================================

df = pd.read_excel(EXCEL_FILE)

# ==================================================
# CREATE / RESET COLUMN
# ==================================================

df["Demo Priority"] = ""

# ==================================================
# LOW PRIORITY DOCUMENT KEYWORDS
# ==================================================

LOW_PRIORITY_KEYWORDS = [
    "annual_report",
    "bulletin",
    "survey",
    "surveys",
    "speech",
    "transcript",
    "reappointment",
    "meeting",
    "statement",
    "citizens_charter",
    "forex_reserves",
    "balance_of_payments",
    "bsr1",
    "bsr2",
]

# ==================================================
# ASSIGN PRIORITIES
# ==================================================

priorities = []

for _, row in df.iterrows():

    category = str(row["Category"]).strip().lower()
    filename = str(row["File Name"]).strip().lower()
    classification = str(row["Classification"]).strip().lower()

    priority = "Medium"

    # ----------------------------------------------
    # High Priority Categories
    # ----------------------------------------------

    if category in [
        "aml",
        "kyc",
        "cybersecurity"
    ]:
        priority = "High"

    # ----------------------------------------------
    # Source Documents
    # ----------------------------------------------

    if classification == "source":
        priority = "High"

    # ----------------------------------------------
    # Low Priority Informational Documents
    # ----------------------------------------------

    for keyword in LOW_PRIORITY_KEYWORDS:

        if keyword in filename:

            priority = "Low"
            break

    priorities.append(priority)

# ==================================================
# UPDATE DATAFRAME
# ==================================================

df["Demo Priority"] = priorities

# ==================================================
# SAVE
# ==================================================

df.to_excel(EXCEL_FILE, index=False)

# ==================================================
# SUMMARY
# ==================================================

high_count = priorities.count("High")
medium_count = priorities.count("Medium")
low_count = priorities.count("Low")

print("=" * 60)
print("DEMO PRIORITY ASSIGNMENT COMPLETED")
print("=" * 60)
print(f"High   : {high_count}")
print(f"Medium : {medium_count}")
print(f"Low    : {low_count}")
print("=" * 60)
print(f"Updated file: {EXCEL_FILE}")
print("=" * 60)
