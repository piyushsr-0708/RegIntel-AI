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

DEMO_CORPUS = str(PROJECT_ROOT / "demo_corpus")

MIN_PRIORITY_SCORE = 40

# ==================================================
# CREATE OUTPUT FOLDER
# ==================================================

os.makedirs(DEMO_CORPUS, exist_ok=True)

# ==================================================
# LOAD INVENTORY
# ==================================================

df = pd.read_excel(EXCEL_FILE)

# ==================================================
# FILTER DOCUMENTS
# ==================================================

filtered = df[
    (df["Demo Priority"] == "High") &
    (df["Overall Priority"] >= MIN_PRIORITY_SCORE)
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

for _, row in filtered.iterrows():

    category = str(row["Category"])
    filename = str(row["File Name"])

    source_file = os.path.join(
        SOURCE_DATASET,
        category,
        filename
    )

    target_folder = os.path.join(
        DEMO_CORPUS,
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

    else:

        print(f"Missing: {source_file}")
        missing += 1

# ==================================================
# SUMMARY
# ==================================================

print("=" * 60)
print("DEMO CORPUS CREATED")
print("=" * 60)
print(f"Documents copied : {copied}")
print(f"Missing files    : {missing}")
print(f"Output folder    : {DEMO_CORPUS}")
print("=" * 60)
