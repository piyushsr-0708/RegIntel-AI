import re
import chromadb
from sentence_transformers import SentenceTransformer

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

DB_PATH = str(PROJECT_ROOT / "data" / "vector_db")

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

    # ====================================================
    # QUERY MATCH
    # ====================================================

    for word in query_words:

        if len(word) < 3:
            continue

        if word in lower:
            score += 25

    # ====================================================
    # MANDATORY LANGUAGE BOOST
    # ====================================================

    if "shall" in lower:
        score += 40

    if "must" in lower:
        score += 40

    if "required to" in lower:
        score += 40

    if "should" in lower:
        score += 15

    # ====================================================
    # DOMAIN SPECIFIC BOOSTS
    # ====================================================

    query_lower = query.lower()

    # CTR

    if "ctr" in query_lower:

        if "ctr" in lower:
            score += 100

        if "15th" in lower:
            score += 80

        if "succeeding month" in lower:
            score += 80

    # FIU

    if "fiu" in query_lower:

        if "fiu-ind" in lower:
            score += 80

        if "shall furnish" in lower:
            score += 80

        if "reporting format" in lower:
            score += 20

    # BENEFICIAL OWNERSHIP

    if (
        "beneficial" in query_lower
        or "ownership" in query_lower
    ):

        if "beneficial owner" in lower:
            score += 100

        if "verify the identity" in lower:
            score += 40

        if "identify the beneficial owners" in lower:
            score += 60

    # RECORD RETENTION

    if (
        "retention" in query_lower
        or "record" in query_lower
    ):

        if "ten years" in lower:
            score += 80

        if "maintain" in lower:
            score += 40

        if "preserve" in lower:
            score += 40

    # CYBERSECURITY MONITORING

    if (
        "cyber" in query_lower
        or "monitoring" in query_lower
    ):

        if "real time" in lower:
            score += 60

        if "continuous monitoring" in lower:
            score += 60

        if "siem" in lower:
            score += 50

        if "soc" in lower:
            score += 50

    # ====================================================
    # COMPLIANCE ACTIONS
    # ====================================================

    if "report" in lower:
        score += 5

    if "maintain" in lower:
        score += 5

    if "retain" in lower:
        score += 5

    if "preserve" in lower:
        score += 5

    if "verify" in lower:
        score += 5

    if "monitor" in lower:
        score += 5

    if "screen" in lower:
        score += 5

    if "submit" in lower:
        score += 5

    # ====================================================
    # DEADLINE BOOST
    # ====================================================

    if "latest by" in lower:
        score += 25

    if "at least" in lower:
        score += 25

    if "within" in lower:
        score += 20

    if "not later than" in lower:
        score += 25

    # ====================================================
    # TIME PERIOD BOOST
    # ====================================================

    if "year" in lower:
        score += 15

    if "years" in lower:
        score += 15

    if "month" in lower:
        score += 15

    if "months" in lower:
        score += 15

    if "day" in lower:
        score += 15

    if "days" in lower:
        score += 15

    # ====================================================
    # NUMERIC REQUIREMENTS
    # ====================================================

    if re.search(r"\b\d+\b", sentence):
        score += 15

    if re.search(
        r"\b\d+(st|nd|rd|th)\b",
        lower
    ):
        score += 20

    # ====================================================
    # PENALIZE DEFINITIONS
    # ====================================================

    if lower.startswith("where the client"):
        score -= 10

    if "means" in lower:
        score -= 15

    if "definition" in lower:
        score -= 15

    if "beneficial owner is" in lower:
        score -= 10

    return score


def extract_years(text):

    text = text.lower()

    match = re.search(
        r"(\d+)\s+year",
        text
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
        "ten":10,
        "eleven":11,
        "twelve":12
    }

    for word, value in word_map.items():

        if f"{word} year" in text:
            return value

        if f"{word} years" in text:
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

    # ============================================
    # RETENTION PERIOD COMPARISON
    # ============================================

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

    # ============================================
    # DEADLINE COMPARISON
    # ============================================

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

    # ============================================
    # ACTION MATCHING
    # ============================================

    important_words = [

        "verify",
        "verified",
        "verifies",

        "monitor",
        "monitors",
        "monitoring",

        "report",
        "reported",
        "reporting",

        "maintain",
        "maintained",

        "retain",
        "retained",

        "preserve",
        "preserved",

        "screen",
        "screening",

        "submit",
        "submitted",

        "identify",
        "identified",

        "review",
        "reviewed",

        "record",
        "records"
    ]

    matches = 0

    req_lower = requirement.lower()
    pol_lower = policy.lower()

    # Verify family
    if (
        ("verify" in req_lower or "verified" in req_lower)
        and
        ("verify" in pol_lower or "verified" in pol_lower or "verifies" in pol_lower)
    ):
        matches += 1

    # Beneficial owner family
    if (
        "beneficial owner" in req_lower
        and
        "beneficial owner" in pol_lower
    ):
        matches += 1

    # Monitoring family
    if (
        "monitor" in req_lower
        and
        "monitor" in pol_lower
    ):
        matches += 1

    # Reporting family
    if (
        "report" in req_lower
        and
        "report" in pol_lower
    ):
        matches += 1

    # Maintenance family
    if (
        (
            "maintain" in req_lower
            or "retain" in req_lower
            or "preserve" in req_lower
        )
        and
        (
            "maintain" in pol_lower
            or "retain" in pol_lower
            or "preserve" in pol_lower
        )
    ):
        matches += 1
    
    if matches >= 1:

        return (
            "PARTIALLY COMPLIANT",
            "MEDIUM"
        )

    # ============================================
    # FALLBACK
    # ============================================

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

    unique_candidates = []

    seen = set()

    for score, text in candidates:

        key = text.lower()[:150]

        if key in seen:
            continue

        seen.add(key)

        unique_candidates.append(
            (
                score,
                text
            )
        )

    candidates = unique_candidates

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
