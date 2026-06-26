import os
import shutil
import pandas as pd

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

EXCEL_FILE = str(PROJECT_ROOT / "dataset_inventory.xlsx")

SOURCE_DATASET = str(PROJECT_ROOT / "dataset/rbi")

HIGH_PRIORITY_FOLDER = str(PROJECT_ROOT / "high_priority")

# ==================================================
# CREATE OUTPUT FOLDER
# ==================================================

os.makedirs(HIGH_PRIORITY_FOLDER, exist_ok=True)

# ==================================================
# LOAD INVENTORY
# ==================================================

df = pd.read_excel(EXCEL_FILE)

# ==================================================
# FILTER HIGH PRIORITY DOCUMENTS
# ==================================================

filtered = df[
    df["Demo Priority"].astype(str).str.strip().str.lower() == "high"
].copy()

# ==================================================
# REMOVE DUPLICATES
# ==================================================

filtered = filtered.drop_duplicates(
    subset=["File Name"]
)

# ==================================================
# COPY FILES
# ==================================================

copied = 0
missing = 0

category_counts = {}

for _, row in filtered.iterrows():

    category = str(row["Category"]).strip()
    filename = str(row["File Name"]).strip()

    source_file = os.path.join(
        SOURCE_DATASET,
        category,
        filename
    )

    target_folder = os.path.join(
        HIGH_PRIORITY_FOLDER,
        category
    )

    os.makedirs(target_folder, exist_ok=True)

    target_file = os.path.join(
        target_folder,
        filename
    )

    if os.path.exists(source_file):

        shutil.copy2(
            source_file,
            target_file
        )

        copied += 1

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    else:

        print(f"Missing: {source_file}")
        missing += 1

# ==================================================
# SUMMARY
# ==================================================

print("=" * 60)
print("HIGH PRIORITY CORPUS CREATED")
print("=" * 60)

for category in sorted(category_counts):
    print(
        f"{category:<20} {category_counts[category]}"
    )

print("-" * 60)

print(f"Total copied : {copied}")
print(f"Missing      : {missing}")

print("-" * 60)

print(
    f"Output folder: {HIGH_PRIORITY_FOLDER}"
)

print("=" * 60)
