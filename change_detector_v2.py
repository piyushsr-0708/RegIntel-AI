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

OUTPUT_FILE = str(PROJECT_ROOT / "change_analysis/change_report.json")

SIMILARITY_THRESHOLD = 0.75

# ============================================================
# HELPERS
# ============================================================

def normalize(text):

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


def classify_change(
    old_text,
    new_text
):

    old_l = old_text.lower()
    new_l = new_text.lower()

    # ----------------------------------

    if (
        "year" in old_l or
        "years" in old_l
    ) and (
        "year" in new_l or
        "years" in new_l
    ):
        return "Retention Change"

    # ----------------------------------

    if (
        "month" in old_l or
        "months" in old_l or
        "day" in old_l or
        "days" in old_l
    ) and (
        "month" in new_l or
        "months" in new_l or
        "day" in new_l or
        "days" in new_l
    ):
        return "Deadline Change"

    # ----------------------------------

    if (
        "report" in old_l and
        "report" in new_l
    ):
        return "Reporting Change"

    # ----------------------------------

    if (
        "verify" in old_l and
        "verify" in new_l
    ):
        return "Verification Change"

    # ----------------------------------

    if (
        "monitor" in old_l and
        "monitor" in new_l
    ):
        return "Monitoring Change"

    # ----------------------------------

    return "Other Change"


def determine_severity(
    change_type
):

    if change_type in [

        "Retention Change",
        "Deadline Change",
        "Reporting Change"

    ]:
        return "HIGH"

    if change_type in [

        "Verification Change",
        "Monitoring Change"

    ]:
        return "MEDIUM"

    return "LOW"

# ============================================================
# LOAD DATA
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

old_map = {}

for item in old_data:

    req = item.get(
        "requirement",
        ""
    )

    old_map[
        normalize(req)
    ] = req

new_map = {}

for item in new_data:

    req = item.get(
        "requirement",
        ""
    )

    new_map[
        normalize(req)
    ] = req

# ============================================================
# ADDED / REMOVED
# ============================================================

old_keys = set(
    old_map.keys()
)

new_keys = set(
    new_map.keys()
)

added_keys = list(
    new_keys - old_keys
)

removed_keys = list(
    old_keys - new_keys
)

# ============================================================
# FIND MODIFICATIONS
# ============================================================

print(
    "\nFinding modifications..."
)

modifications = []

used_removed = set()

for added in added_keys:

    best_match = None
    best_score = 0

    for idx, removed in enumerate(
        removed_keys
    ):

        if idx in used_removed:
            continue

        score = similarity(
            added,
            removed
        )

        if score > best_score:

            best_score = score
            best_match = idx

    if (
        best_match is not None
        and best_score >= SIMILARITY_THRESHOLD
    ):

        old_text = old_map[
            removed_keys[best_match]
        ]

        new_text = new_map[
            added
        ]

        change_type = classify_change(
            old_text,
            new_text
        )

        severity = determine_severity(
            change_type
        )

        modifications.append({

            "change_type":
            change_type,

            "severity":
            severity,

            "similarity":
            round(
                best_score,
                3
            ),

            "old_requirement":
            old_text,

            "new_requirement":
            new_text

        })

        used_removed.add(
            best_match
        )

# ============================================================
# TRUE ADDED
# ============================================================

true_added = []

for key in added_keys:

    matched = False

    for mod in modifications:

        if (
            mod["new_requirement"]
            == new_map[key]
        ):
            matched = True
            break

    if not matched:

        true_added.append(
            new_map[key]
        )

# ============================================================
# TRUE REMOVED
# ============================================================

true_removed = []

for idx, key in enumerate(
    removed_keys
):

    if idx in used_removed:
        continue

    true_removed.append(
        old_map[key]
    )

# ============================================================
# SAVE REPORT
# ============================================================

report = {

    "summary": {

        "added":
        len(true_added),

        "removed":
        len(true_removed),

        "modified":
        len(modifications)
    },

    "added":
    true_added,

    "removed":
    true_removed,

    "modified":
    modifications
}

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        report,
        f,
        indent=4,
        ensure_ascii=False
    )

# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 80)
print("CHANGE DETECTOR V2")
print("=" * 80)

print(
    f"\nAdded Requirements    : {len(true_added)}"
)

print(
    f"Removed Requirements  : {len(true_removed)}"
)

print(
    f"Modified Requirements : {len(modifications)}"
)

print(
    f"\nOutput File : {OUTPUT_FILE}"
)

# ============================================================
# SAMPLE MODIFICATIONS
# ============================================================

print("\n" + "=" * 80)
print("SAMPLE MODIFICATIONS")
print("=" * 80)

for i, item in enumerate(
    modifications[:5],
    start=1
):

    print(
        f"\n{i}. "
        f"{item['change_type']}"
    )

    print(
        f"Severity : "
        f"{item['severity']}"
    )

    print(
        f"Similarity : "
        f"{item['similarity']}"
    )

    print(
        "\nOLD:"
    )

    print(
        item["old_requirement"][:250]
    )

    print(
        "\nNEW:"
    )

    print(
        item["new_requirement"][:250]
    )

print("\n" + "=" * 80)
print("PHASE 6B COMPLETE")
print("=" * 80)
