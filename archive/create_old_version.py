import json
import random
import copy

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

OLD_FILE = str(PROJECT_ROOT / "change_analysis/old_requirements.json")

# ============================================================
# LOAD
# ============================================================

with open(
    OLD_FILE,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)

print(f"Loaded {len(data)} requirements")

# ============================================================
# MODIFY SOME DEADLINES
# ============================================================

modified = 0

for item in random.sample(
    data,
    min(250, len(data))
):

    text = item["requirement"]

    text = text.replace(
        "ten years",
        "five years"
    )

    text = text.replace(
        "10 years",
        "5 years"
    )

    text = text.replace(
        "15th of the succeeding month",
        "20th of the succeeding month"
    )

    text = text.replace(
        "within three months",
        "within six months"
    )

    item["requirement"] = text

    modified += 1

# ============================================================
# REMOVE SOME REQUIREMENTS
# ============================================================

remove_count = min(
    250,
    len(data) // 20
)

indices = random.sample(
    range(len(data)),
    remove_count
)

data = [
    item
    for idx, item in enumerate(data)
    if idx not in indices
]

# ============================================================
# ADD FAKE HISTORICAL REQUIREMENTS
# ============================================================

extra_requirements = [

    {
        "source_file": "OLD_MASTER_DIRECTION.pdf",
        "chunk_id": 1,
        "trigger_word": "shall",
        "requirement":
        "Banks shall retain customer records for five years.",
        "obligation_type":
        "Mandatory",
        "entity":
        "banks",
        "deadline":
        "five years"
    },

    {
        "source_file": "OLD_MASTER_DIRECTION.pdf",
        "chunk_id": 2,
        "trigger_word": "shall",
        "requirement":
        "Banks shall submit CTR reports by the 20th of the succeeding month.",
        "obligation_type":
        "Mandatory",
        "entity":
        "banks",
        "deadline":
        "20th"
    },

    {
        "source_file": "OLD_MASTER_DIRECTION.pdf",
        "chunk_id": 3,
        "trigger_word": "shall",
        "requirement":
        "Banks shall review KYC records every six months.",
        "obligation_type":
        "Mandatory",
        "entity":
        "banks",
        "deadline":
        "six months"
    }
]

data.extend(extra_requirements)

# ============================================================
# SAVE
# ============================================================

with open(
    OLD_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        data,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\n================================================")
print("OLD VERSION GENERATED")
print("================================================")
print(f"Final Requirements : {len(data)}")
print(f"Modified Records   : {modified}")
print(f"Removed Records    : {remove_count}")
print(f"Added Fake Records : {len(extra_requirements)}")
print("================================================")
