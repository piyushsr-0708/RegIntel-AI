import json
import re
from collections import Counter

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

OLD_FILE = str(PROJECT_ROOT / "change_analysis/old_requirements.json")

NEW_FILE = str(PROJECT_ROOT / "change_analysis/new_requirements.json")

ADDED_FILE = str(PROJECT_ROOT / "change_analysis/added.json")

REMOVED_FILE = str(PROJECT_ROOT / "change_analysis/removed.json")

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

# ============================================================
# LOAD FILES
# ============================================================

print("Loading files...")

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
# BUILD COUNTERS
# ============================================================

old_counter = Counter()

new_counter = Counter()

old_lookup = {}

new_lookup = {}

# ------------------------------------------------------------

for item in old_data:

    requirement = item.get(
        "requirement",
        ""
    ).strip()

    normalized = normalize_text(
        requirement
    )

    old_counter[normalized] += 1

    if normalized not in old_lookup:

        old_lookup[normalized] = item

# ------------------------------------------------------------

for item in new_data:

    requirement = item.get(
        "requirement",
        ""
    ).strip()

    normalized = normalize_text(
        requirement
    )

    new_counter[normalized] += 1

    if normalized not in new_lookup:

        new_lookup[normalized] = item

# ============================================================
# FIND ADDED
# ============================================================

added = []

for text in new_counter:

    difference = (
        new_counter[text]
        - old_counter.get(text, 0)
    )

    if difference > 0:

        for _ in range(difference):

            added.append(
                new_lookup[text]
            )

# ============================================================
# FIND REMOVED
# ============================================================

removed = []

for text in old_counter:

    difference = (
        old_counter[text]
        - new_counter.get(text, 0)
    )

    if difference > 0:

        for _ in range(difference):

            removed.append(
                old_lookup[text]
            )

# ============================================================
# SAVE OUTPUTS
# ============================================================

with open(
    ADDED_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        added,
        f,
        indent=4,
        ensure_ascii=False
    )

with open(
    REMOVED_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        removed,
        f,
        indent=4,
        ensure_ascii=False
    )

# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 80)
print("CHANGE DIFF SUMMARY")
print("=" * 80)

print(
    f"\nAdded Requirements   : {len(added)}"
)

print(
    f"Removed Requirements : {len(removed)}"
)

print(
    f"\nAdded File:"
)

print(
    ADDED_FILE
)

print(
    f"\nRemoved File:"
)

print(
    REMOVED_FILE
)

# ============================================================
# SAMPLE ADDED
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE ADDED")
print("=" * 80)

for i, item in enumerate(
    added[:5],
    start=1
):

    print(
        f"\n{i}. "
        f"{item['requirement'][:300]}"
    )

# ============================================================
# SAMPLE REMOVED
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE REMOVED")
print("=" * 80)

for i, item in enumerate(
    removed[:5],
    start=1
):

    print(
        f"\n{i}. "
        f"{item['requirement'][:300]}"
    )

print("\n" + "=" * 80)
print("PHASE 6A.1 COMPLETE")
print("=" * 80)
