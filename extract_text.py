import os
import fitz
import pandas as pd

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# =====================================================
# CONFIGURATION
# =====================================================

PDF_FOLDER = str(PROJECT_ROOT / "demo_corpus")

OUTPUT_FOLDER = str(PROJECT_ROOT / "data" / "extracted_text")

REPORT_FILE = str(PROJECT_ROOT / "extraction_report.xlsx")

# =====================================================
# CREATE OUTPUT FOLDER
# =====================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =====================================================
# FIND ALL PDF FILES
# =====================================================

pdf_files = []

for root, dirs, files in os.walk(PDF_FOLDER):

    for file in files:

        if file.lower().endswith(".pdf"):

            pdf_files.append(
                os.path.join(root, file)
            )

# =====================================================
# EXTRACTION REPORT
# =====================================================

report = []

total_files = len(pdf_files)

print("\n")
print("=" * 60)
print(f"FOUND {total_files} PDF FILES")
print("=" * 60)

# =====================================================
# PROCESS FILES
# =====================================================

for idx, pdf_path in enumerate(pdf_files, start=1):

    filename = os.path.basename(pdf_path)

    print(f"[{idx}/{total_files}] {filename}")

    extracted_text = ""

    page_count = 0

    try:

        doc = fitz.open(pdf_path)

        page_count = len(doc)

        for page in doc:

            try:

                extracted_text += page.get_text()

            except Exception:
                pass

        doc.close()

    except Exception as e:

        print(f"ERROR: {e}")

    # ---------------------------------------------

    char_count = len(extracted_text)

    word_count = len(extracted_text.split())

    # ---------------------------------------------

    txt_filename = os.path.splitext(filename)[0] + ".txt"

    txt_path = os.path.join(
        OUTPUT_FOLDER,
        txt_filename
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(extracted_text)

    # ---------------------------------------------

    report.append(
        {
            "File Name": filename,
            "Pages": page_count,
            "Characters": char_count,
            "Words": word_count,
            "TXT File": txt_filename
        }
    )

# =====================================================
# SAVE REPORT
# =====================================================

df = pd.DataFrame(report)

df.to_excel(
    REPORT_FILE,
    index=False
)

# =====================================================
# SUMMARY
# =====================================================

print("\n")
print("=" * 60)
print("TEXT EXTRACTION COMPLETED")
print("=" * 60)

print(f"PDF Folder      : {PDF_FOLDER}")
print(f"Output Folder   : {OUTPUT_FOLDER}")
print(f"Report File     : {REPORT_FILE}")

print("-" * 60)

print(f"Files Processed : {len(report)}")

print("=" * 60)
