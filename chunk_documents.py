import os
import json

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

INPUT_FOLDER = str(PROJECT_ROOT / "data" / "extracted_text")

OUTPUT_FOLDER = str(PROJECT_ROOT / "data" / "chunks")

CHUNK_SIZE = 1000
OVERLAP = 200

# ==================================================
# CREATE OUTPUT FOLDER
# ==================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==================================================
# CHUNK FUNCTION
# ==================================================

def create_chunks(text, chunk_size=1000, overlap=200):

    chunks = []

    start = 0
    chunk_id = 1

    while start < len(text):

        end = start + chunk_size

        chunk_text = text[start:end]

        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": chunk_text
            }
        )

        chunk_id += 1

        start += (chunk_size - overlap)

    return chunks


# ==================================================
# PROCESS FILES
# ==================================================

txt_files = [
    f for f in os.listdir(INPUT_FOLDER)
    if f.lower().endswith(".txt")
]

total_chunks = 0

for txt_file in txt_files:

    txt_path = os.path.join(
        INPUT_FOLDER,
        txt_file
    )

    with open(
        txt_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        text = f.read()

    chunks = create_chunks(
        text,
        CHUNK_SIZE,
        OVERLAP
    )

    total_chunks += len(chunks)

    # Add metadata

    output_chunks = []

    for chunk in chunks:

        output_chunks.append(
            {
                "source_file": txt_file.replace(".txt", ".pdf"),
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"]
            }
        )

    output_file = txt_file.replace(
        ".txt",
        "_chunks.json"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_file
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output_chunks,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"{txt_file} -> {len(chunks)} chunks"
    )

# ==================================================
# SUMMARY
# ==================================================

print("\n" + "=" * 60)
print("CHUNKING COMPLETED")
print("=" * 60)
print(f"Documents Processed : {len(txt_files)}")
print(f"Total Chunks        : {total_chunks}")
print(f"Output Folder       : {OUTPUT_FOLDER}")
print("=" * 60)
