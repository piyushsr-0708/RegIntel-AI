import os
import json
import re

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==========================================================
# CONFIG
# ==========================================================

CHUNK_FOLDER = str(PROJECT_ROOT / "chunks")

OUTPUT_FOLDER = str(PROJECT_ROOT / "requirements")

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "requirements.json"
)

# ==========================================================
# CREATE OUTPUT FOLDER
# ==========================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# ==========================================================
# OBLIGATION KEYWORDS
# ==========================================================

OBLIGATION_WORDS = [

    "shall",
    "must",
    "required to",
    "requirement",

    "ensure",
    "maintain",
    "monitor",
    "verify",

    "report",
    "submit",
    "preserve",

    "identify",
    "obtain",
    "record",

    "retain",
    "conduct",
    "review"
]

# ==========================================================
# SENTENCE SPLITTER
# ==========================================================

def split_sentences(text):

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    cleaned = []

    for s in sentences:

        s = s.strip()

        if len(s) > 20:
            cleaned.append(s)

    return cleaned

# ==========================================================
# REQUIREMENT DETECTOR
# ==========================================================

def detect_requirement(sentence):

    sentence_lower = sentence.lower()

    for keyword in OBLIGATION_WORDS:

        if keyword in sentence_lower:

            return keyword

    return None

# ==========================================================
# PROCESS FILES
# ==========================================================

all_requirements = []

json_files = [

    f
    for f in os.listdir(CHUNK_FOLDER)
    if f.endswith(".json")
]

total_chunks = 0
total_requirements = 0

print("\nScanning chunk files...\n")

for file in json_files:

    path = os.path.join(
        CHUNK_FOLDER,
        file
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    for chunk in chunks:

        total_chunks += 1

        chunk_text = chunk["text"]

        sentences = split_sentences(
            chunk_text
        )

        for sentence in sentences:

            keyword = detect_requirement(
                sentence
            )

            if keyword:

                record = {

                    "source_file":
                    chunk["source_file"],

                    "chunk_id":
                    chunk["chunk_id"],

                    "trigger_word":
                    keyword,

                    "requirement":
                    sentence
                }

                all_requirements.append(
                    record
                )

                total_requirements += 1

# ==========================================================
# SAVE JSON
# ==========================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_requirements,
        f,
        indent=4,
        ensure_ascii=False
    )

# ==========================================================
# SUMMARY
# ==========================================================

print("\n" + "=" * 60)
print("REQUIREMENT EXTRACTION COMPLETED")
print("=" * 60)

print(
    f"Chunk Files Processed : {len(json_files)}"
)

print(
    f"Chunks Scanned        : {total_chunks}"
)

print(
    f"Requirements Found    : {total_requirements}"
)

print(
    f"Output File           : {OUTPUT_FILE}"
)

print("=" * 60)
