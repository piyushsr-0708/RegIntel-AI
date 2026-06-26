import os
import hashlib

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

ROOT_FOLDER = str(PROJECT_ROOT)

# ============================================================
# HASH FUNCTION
# ============================================================

def file_hash(filepath):

    md5 = hashlib.md5()

    with open(filepath, "rb") as f:

        while True:

            chunk = f.read(8192)

            if not chunk:
                break

            md5.update(chunk)

    return md5.hexdigest()

# ============================================================
# FIND PDFS
# ============================================================

pdf_files = []

for root, dirs, files in os.walk(ROOT_FOLDER):

    for file in files:

        if file.lower().endswith(".pdf"):

            pdf_files.append(
                os.path.join(root, file)
            )

print(f"\nFound {len(pdf_files)} PDFs")

# ============================================================
# DETECT DUPLICATES
# ============================================================

seen_hashes = {}

duplicates = []

for pdf in pdf_files:

    try:

        h = file_hash(pdf)

        if h in seen_hashes:

            duplicates.append(pdf)

        else:

            seen_hashes[h] = pdf

    except Exception as e:

        print(f"Error: {pdf}")
        print(e)

# ============================================================
# DELETE DUPLICATES
# ============================================================

print("\nDuplicate Files Found:")

for file in duplicates:

    print(file)

for file in duplicates:

    try:

        os.remove(file)

    except Exception as e:

        print(f"Could not delete: {file}")
        print(e)

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DUPLICATE CLEANUP COMPLETE")
print("=" * 60)
print(f"Unique PDFs      : {len(seen_hashes)}")
print(f"Duplicates Removed: {len(duplicates)}")
print("=" * 60)
