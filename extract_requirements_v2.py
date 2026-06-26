import os
import json
import re

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==========================================================
# CONFIG
# ==========================================================

INPUT_FILE = str(PROJECT_ROOT / "data/requirements/requirements.json")

OUTPUT_FILE = str(PROJECT_ROOT / "data/requirements/requirements_clean.json")

# ==========================================================
# EXCLUSION RULES
# ==========================================================

EXCLUDE_PATTERNS = [

    "click here",
    "website -",
    "http://",
    "https://",

    "date:",
    "time:",
    "address:",

    "reported to rbi - date",
    "reported to cert",
    "reported to nciip",

    "please indicate",
    "is this a",

    "annex",
    "appendix",

    "hotel samrat",
    "chanakyapuri",

    "report no",

    "electronic file structure",

    "☐",
    "□"
]

# ==========================================================
# VERY SHORT SENTENCE FILTER
# ==========================================================

MIN_LENGTH = 50

# ==========================================================
# OBLIGATION CLASSIFIER
# ==========================================================

def classify_obligation(text):

    t = text.lower()

    if "shall" in t:
        return "Mandatory"

    if "must" in t:
        return "Mandatory"

    if "required to" in t:
        return "Mandatory"

    if "are required to" in t:
        return "Mandatory"

    if "is required to" in t:
        return "Mandatory"

    if "should" in t:
        return "Recommended"

    return "Informational"


# ==========================================================
# DEADLINE EXTRACTOR
# ==========================================================

def extract_deadline(text):

    patterns = [

        r"before\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}",

        r"by\s+\d{1,2}(st|nd|rd|th)?\s+of",

        r"within\s+\d+\s+(day|days|month|months|year|years)",

        r"for\s+\d+\s+(day|days|month|months|year|years)",

        r"at least\s+\d+\s+(day|days|month|months|year|years)",

        r"ten years",
        r"five years",
        r"three months"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return ""


# ==========================================================
# ENTITY EXTRACTOR
# ==========================================================

ENTITY_PATTERNS = [

    "banks",
    "bank",

    "nbfcs",
    "nbfc",

    "regulated entities",
    "res",

    "financial institutions",

    "rnbcs",
    "rnbc",

    "customers",

    "depositors"
]


def extract_entity(text):

    t = text.lower()

    for entity in ENTITY_PATTERNS:

        if entity in t:
            return entity

    return "Unknown"


# ==========================================================
# CLEANING
# ==========================================================

def should_exclude(text):

    t = text.lower()

    if len(t) < MIN_LENGTH:
        return True

    for pattern in EXCLUDE_PATTERNS:

        if pattern in t:
            return True

    return False


# ==========================================================
# LOAD DATA
# ==========================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    requirements = json.load(f)

# ==========================================================
# PROCESS
# ==========================================================

clean_requirements = []

removed = 0

for item in requirements:

    text = item["requirement"]

    if should_exclude(text):

        removed += 1
        continue

    item["obligation_type"] = classify_obligation(text)

    item["entity"] = extract_entity(text)

    item["deadline"] = extract_deadline(text)

    clean_requirements.append(item)

# ==========================================================
# SAVE
# ==========================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        clean_requirements,
        f,
        indent=4,
        ensure_ascii=False
    )

# ==========================================================
# SUMMARY
# ==========================================================

print("\n" + "=" * 60)
print("PHASE 2B COMPLETED")
print("=" * 60)

print(
    f"Original Requirements : {len(requirements)}"
)

print(
    f"Removed Noise         : {removed}"
)

print(
    f"Final Requirements    : {len(clean_requirements)}"
)

print(
    f"Output File           : {OUTPUT_FILE}"
)

print("=" * 60)
