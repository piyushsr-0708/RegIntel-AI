import re
import chromadb
from sentence_transformers import SentenceTransformer

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

DB_PATH = str(PROJECT_ROOT / "vector_db")

COLLECTION_NAME = "regintel_rbi"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5

# ============================================================
# LOAD MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Model loaded.")

# ============================================================
# LOAD DATABASE
# ============================================================

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=DB_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)

print(
    f"Collection Loaded: {COLLECTION_NAME}"
)

print(
    f"Indexed Chunks: {collection.count()}"
)

# ============================================================
# KEYWORDS
# ============================================================

COMPLIANCE_KEYWORDS = [

    "shall",
    "must",
    "required to",
    "should",

    "report",
    "maintain",
    "retain",
    "preserve",

    "verify",
    "monitor",

    "ensure",

    "submit",

    "record"
]

# ============================================================
# HELPERS
# ============================================================

def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_sentences(text):

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        clean_text(x)
        for x in parts
        if len(x.strip()) > 40
    ]


def is_compliance_statement(text):

    lower = text.lower()

    for word in COMPLIANCE_KEYWORDS:

        if word in lower:
            return True

    return False


def classify_requirement(text):

    lower = text.lower()

    if (
        "shall" in lower
        or "must" in lower
        or "required to" in lower
    ):
        return "Mandatory"

    if (
        "should" in lower
        or "recommended" in lower
    ):
        return "Recommended"

    return "Informational"


def score_requirement(
    sentence,
    query
):

    score = 0

    lower = sentence.lower()

    query_words = query.lower().split()

    for word in query_words:

        if len(word) < 3:
            continue

        if word in lower:
            score += 10

    if "shall" in lower:
        score += 5

    if "must" in lower:
        score += 5

    if "required to" in lower:
        score += 5

    if "retain" in lower:
        score += 3

    if "maintain" in lower:
        score += 3

    if "report" in lower:
        score += 3

    if "verify" in lower:
        score += 3

    if "monitor" in lower:
        score += 3

    return score


def extract_years(text):

    text = text.lower()

    match = re.search(
        r"(\d+)\s+year",
        text
    )

    if match:
        return int(match.group(1))

    words = {

        "one":1,
        "two":2,
        "three":3,
        "four":4,
        "five":5,
        "six":6,
        "seven":7,
        "eight":8,
        "nine":9,
        "ten":10
    }

    for word, value in words.items():

        if f"{word} year" in text:
            return value

    return None


def extract_day_deadline(text):

    text = text.lower()

    match = re.search(
        r"(\d+)(?:st|nd|rd|th)",
        text
    )

    if match:
        return int(match.group(1))

    return None


def determine_gap(
    requirement,
    policy
):

    req_years = extract_years(
        requirement
    )

    pol_years = extract_years(
        policy
    )

    if req_years and pol_years:

        if pol_years >= req_years:

            return (
                "COMPLIANT",
                "LOW"
            )

        return (
            "NON-COMPLIANT",
            "HIGH"
        )

    req_day = extract_day_deadline(
        requirement
    )

    pol_day = extract_day_deadline(
        policy
    )

    if req_day and pol_day:

        if pol_day <= req_day:

            return (
                "COMPLIANT",
                "LOW"
            )

        return (
            "NON-COMPLIANT",
            "HIGH"
        )

    req_words = set(
        requirement.lower().split()
    )

    pol_words = set(
        policy.lower().split()
    )

    overlap = len(
        req_words.intersection(pol_words)
    )

    if overlap >= 3:

        return (
            "PARTIALLY COMPLIANT",
            "MEDIUM"
        )

    return (
        "REVIEW REQUIRED",
        "UNKNOWN"
    )

# ============================================================
# LOOP
# ============================================================

while True:

    print("\n" + "=" * 80)

    query = input(
        "\nRequirement Area (or exit): "
    ).strip()

    if query.lower() == "exit":
        break

    policy = input(
        "\nCurrent Organization Policy: "
    ).strip()

    if not policy:
        continue

    print("\nSearching regulations...")

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    docs = results["documents"][0]

    candidates = []

    for doc in docs:

        for sentence in split_sentences(doc):

            if not is_compliance_statement(
                sentence
            ):
                continue

            score = score_requirement(
                sentence,
                query
            )

            candidates.append(
                (
                    score,
                    sentence
                )
            )

    if not candidates:

        print(
            "\nNo compliance requirement found."
        )
        continue

    candidates.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    best_requirement = candidates[0][1]

    obligation_type = classify_requirement(
        best_requirement
    )

    status, severity = determine_gap(
        best_requirement,
        policy
    )

    print("\n" + "=" * 80)
    print("GAP ANALYSIS REPORT")
    print("=" * 80)

    print("\nREGULATORY REQUIREMENT")
    print("-" * 80)
    print(best_requirement)

    print("\nOBLIGATION TYPE")
    print("-" * 80)
    print(obligation_type)

    print("\nORGANIZATION POLICY")
    print("-" * 80)
    print(policy)

    print("\nCOMPLIANCE STATUS")
    print("-" * 80)
    print(status)

    print("\nSEVERITY")
    print("-" * 80)
    print(severity)

    print("\nTOP CANDIDATE REQUIREMENTS")
    print("-" * 80)

    for i, (_, req) in enumerate(
        candidates[:5],
        start=1
    ):

        print(f"\n{i}. {req[:300]}")

    print("\n" + "=" * 80)

print("\nGoodbye.")
