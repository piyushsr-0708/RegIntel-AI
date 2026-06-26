import json
import re
from difflib import SequenceMatcher

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

OLD_FILE = str(PROJECT_ROOT / "change_analysis/old_requirements.json")

NEW_FILE = str(PROJECT_ROOT / "change_analysis/new_requirements.json")

SIMILARITY_THRESHOLD = 0.85

# ============================================================
# HELPERS
# ============================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z0-9 ]",
        "",
        text
    )

    return text.strip()


def similarity(a, b):

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


# ============================================================
# LOAD FILES
# ============================================================

print("Loading requirement files...")

with open(
    OLD_FILE,
    "r",
    encoding="utf-8"
) as f:

    old_data = json.load(f)

with open(
    NEW_FILE,
    "r",
    encoding="utf-8"
) as f:

    new_data = json.load(f)

print(
    f"Old Requirements : {len(old_data)}"
)

print(
    f"New Requirements : {len(new_data)}"
)

# ============================================================
# BUILD LOOKUPS
# ============================================================

old_requirements = []

for item in old_data:

    text = item.get(
        "requirement",
        ""
    )

    norm = normalize_text(text)

    old_requirements.append(
        {
            "original": text,
            "normalized": norm
        }
    )

new_requirements = []

for item in new_data:

    text = item.get(
        "requirement",
        ""
    )

    norm = normalize_text(text)

    new_requirements.append(
        {
            "original": text,
            "normalized": norm
        }
    )

old_set = set(
    x["normalized"]
    for x in old_requirements
)

new_set = set(
    x["normalized"]
    for x in new_requirements
)

# ============================================================
# ADDED
# ============================================================

added = []

for item in new_requirements:

    if item["normalized"] not in old_set:

        added.append(item)

# ============================================================
# REMOVED
# ============================================================

removed = []

for item in old_requirements:

    if item["normalized"] not in new_set:

        removed.append(item)

# ============================================================
# POTENTIAL MODIFICATIONS
# ============================================================

print(
    "\nFinding potential modifications..."
)

modifications = []

checked = 0

for old_item in removed:

    old_text = old_item["normalized"]

    best_score = 0
    best_match = None

    for new_item in added:

        score = similarity(
            old_text,
            new_item["normalized"]
        )

        if score > best_score:

            best_score = score
            best_match = new_item

    checked += 1

    if best_score >= SIMILARITY_THRESHOLD:

        modifications.append(
            {
                "old":
                old_item["original"],

                "new":
                best_match["original"],

                "score":
                round(best_score, 3)
            }
        )

# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 80)
print("CHANGE ANALYSIS REPORT")
print("=" * 80)

print(
    f"\nAdded Requirements      : {len(added)}"
)

print(
    f"Removed Requirements    : {len(removed)}"
)

print(
    f"Potential Modifications : {len(modifications)}"
)

# ============================================================
# SAMPLE ADDED
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE ADDED REQUIREMENTS")
print("=" * 80)

for i, item in enumerate(
    added[:10],
    start=1
):

    print(
        f"\n{i}. {item['original'][:300]}"
    )

# ============================================================
# SAMPLE REMOVED
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE REMOVED REQUIREMENTS")
print("=" * 80)

for i, item in enumerate(
    removed[:10],
    start=1
):

    print(
        f"\n{i}. {item['original'][:300]}"
    )

# ============================================================
# SAMPLE MODIFICATIONS
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE POTENTIAL MODIFICATIONS")
print("=" * 80)

for i, item in enumerate(
    modifications[:10],
    start=1
):

    print(f"\nModification #{i}")

    print(
        f"\nSimilarity Score: "
        f"{item['score']}"
    )

    print(
        "\nOLD:\n"
    )

    print(
        item["old"][:400]
    )

    print(
        "\nNEW:\n"
    )

    print(
        item["new"][:400]
    )

    print(
        "\n" + "-" * 80
    )

print("\n" + "=" * 80)
print("PHASE 6A COMPLETE")
print("=" * 80)
