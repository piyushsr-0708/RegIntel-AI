import os
from openpyxl import Workbook
from openpyxl.styles import Font

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = str(PROJECT_ROOT / "dataset/rbi")
OUTPUT_FILE = str(PROJECT_ROOT / "dataset_inventory.xlsx")

# --------------------------------------------------
# CREATE EXCEL WORKBOOK
# --------------------------------------------------

wb = Workbook()
ws = wb.active
ws.title = "Dataset Inventory"

headers = [
    "Category",
    "File Name",
    "Classification",
    "Parent Source",
    "File Size (KB)",
    "Demo Worthy"
]

ws.append(headers)

for cell in ws[1]:
    cell.font = Font(bold=True)

# --------------------------------------------------
# PROCESS EACH CATEGORY FOLDER
# --------------------------------------------------

for category in sorted(os.listdir(BASE_DIR)):

    category_path = os.path.join(BASE_DIR, category)

    if not os.path.isdir(category_path):
        continue

    readme_path = os.path.join(category_path, "README.txt")

    sources = {}
    linked_to_parent = {}

    # ----------------------------------------------
    # READ README IF PRESENT
    # ----------------------------------------------

    if os.path.exists(readme_path):

        current_source = None

        with open(readme_path, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                # Source document
                if not line.startswith("-"):

                    current_source = line
                    sources[current_source] = True

                # Linked document
                else:

                    child = line.replace("-", "").strip()

                    if current_source:
                        linked_to_parent[child] = current_source

    # ----------------------------------------------
    # PROCESS PDF FILES
    # ----------------------------------------------

    for file in sorted(os.listdir(category_path)):

        if not file.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(category_path, file)

        stem = os.path.splitext(file)[0]

        classification = "Unclassified"
        parent = ""

        matched_source = next(
            (
                s
                for s in sources
                if s.lower() == stem.lower()
            ),
            None
        )

        matched_link = next(
            (
                l
                for l in linked_to_parent
                if l.lower() == stem.lower()
            ),
            None
        )

        if matched_source:

            classification = "Source"

        elif matched_link:

            classification = "Linked"
            parent = linked_to_parent[matched_link]

        size_kb = round(
            os.path.getsize(file_path) / 1024,
            2
        )

        ws.append([
            category,
            file,
            classification,
            parent,
            size_kb,
            ""
        ])

# --------------------------------------------------
# AUTO COLUMN WIDTH
# --------------------------------------------------

for column in ws.columns:

    max_length = 0
    column_letter = column[0].column_letter

    for cell in column:

        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass

    ws.column_dimensions[column_letter].width = min(max_length + 3, 60)

# --------------------------------------------------
# SAVE FILE
# --------------------------------------------------

wb.save(OUTPUT_FILE)

print("=" * 50)
print("Dataset Inventory Created Successfully")
print(f"Output: {OUTPUT_FILE}")
print("=" * 50)
