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
# MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Model loaded.")

# ============================================================
# CHROMADB
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
# HELPERS
# ============================================================

def classify_requirement(text):

    lower = text.lower()

    if "shall" in lower:
        return "Mandatory"

    if "must" in lower:
        return "Mandatory"

    if "required to" in lower:
        return "Mandatory"

    if "should" in lower:
        return "Recommended"

    return "Informational"


def extract_years(text):

    match = re.search(
        r"(\d+)\s+year",
        text.lower()
    )

    if match:
        return int(match.group(1))

    word_map = {
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

    for word, value in word_map.items():

        if f"{word} year" in text.lower():
            return value

    return None


def determine_gap(requirement, policy):

    req_years = extract_years(requirement)

    pol_years = extract_years(policy)

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

    req = requirement.lower()
    pol = policy.lower()

    important_words = [
        "verify",
        "monitor",
        "report",
        "maintain",
        "record",
        "screen",
        "review",
        "audit"
    ]

    matched = 0

    for word in important_words:

        if word in req and word in pol:
            matched += 1

    if matched >= 2:

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

    print("\n" + "="*80)

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

    requirement = docs[0]

    obligation = classify_requirement(
        requirement
    )

    status, severity = determine_gap(
        requirement,
        policy
    )

    print("\n" + "="*80)
    print("GAP ANALYSIS REPORT")
    print("="*80)

    print("\nREGULATORY REQUIREMENT")
    print("-"*80)

    print(
        requirement[:1200]
    )

    print("\nOBLIGATION TYPE")
    print("-"*80)

    print(obligation)

    print("\nORGANIZATION POLICY")
    print("-"*80)

    print(policy)

    print("\nCOMPLIANCE STATUS")
    print("-"*80)

    print(status)

    print("\nSEVERITY")
    print("-"*80)

    print(severity)

    print("\n" + "="*80)

print("\nGoodbye.")
