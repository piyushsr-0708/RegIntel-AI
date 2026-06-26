import re
import time
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

TOP_K = 8

# ============================================================
# KEYWORDS
# ============================================================

MANDATORY_WORDS = [
    "shall",
    "must",
    "required to",
    "mandatory",
    "obliged to"
]

RECOMMENDED_WORDS = [
    "should",
    "recommended",
    "advised to",
    "may ensure"
]

DEADLINE_PATTERNS = [

    r"\b\d{1,2}(?:st|nd|rd|th)\b",

    r"within\s+\d+\s+days",

    r"within\s+\d+\s+months",

    r"before\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4}",

    r"monthly",

    r"quarterly",

    r"annually",

    r"daily",

    r"five years",

    r"ten years",

    r"15th of the succeeding month"
]

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
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Indexed Chunks: {collection.count()}"
)

print("Ready.")

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


def normalize_sentence(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9 ]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def sentence_split(text):

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        p.strip()
        for p in parts
        if len(p.strip()) > 40
    ]


# ============================================================
# FIX A
# TABLE NOISE REMOVAL
# ============================================================

def is_table_noise(text):

    if text.count("Mandatory") >= 3:
        return True

    if text.count("Category") >= 3:
        return True

    if text.count("Exempted") >= 2:
        return True

    if len(text.split()) > 120:
        return True

    return False


# ============================================================
# FIX B
# FRAGMENT REMOVAL
# ============================================================

def is_fragment(text):

    text = text.strip()

    words = text.split()

    if len(words) < 8:
        return True

    if not text[0].isupper():
        return True

    return False


# ============================================================
# OBLIGATION CLASSIFICATION
# ============================================================

def classify_obligation(text):

    lower = text.lower()

    for word in MANDATORY_WORDS:

        if word in lower:
            return "Mandatory"

    for word in RECOMMENDED_WORDS:

        if word in lower:
            return "Recommended"

    return "Informational"


# ============================================================
# FIX C
# QUERY-AWARE SCORING
# ============================================================

def obligation_score(text, query):

    score = 0

    lower = text.lower()

    for word in MANDATORY_WORDS:

        if word in lower:
            score += 10

    for word in RECOMMENDED_WORDS:

        if word in lower:
            score += 5

    if "report" in lower:
        score += 2

    if "maintain" in lower:
        score += 2

    if "verify" in lower:
        score += 2

    if "monitor" in lower:
        score += 2

    if "ensure" in lower:
        score += 1

    query_words = query.lower().split()

    for word in query_words:

        if len(word) < 3:
            continue

        if word in lower:
            score += 5

    return score


# ============================================================
# DEADLINE EXTRACTION
# ============================================================

def extract_deadlines(text):

    deadlines = []

    for pattern in DEADLINE_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            if isinstance(match, tuple):

                deadlines.append(
                    " ".join(match)
                )

            else:

                deadlines.append(
                    str(match)
                )

    return deadlines


# ============================================================
# QUERY LOOP
# ============================================================

while True:

    query = input(
        "\nEnter Query (or type exit): "
    ).strip()

    if query.lower() == "exit":
        break

    if not query:
        continue

    start_time = time.time()

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    mandatory = []
    recommended = []
    informational = []

    deadlines = set()
    sources = set()

    seen = set()

    # ========================================================
    # PROCESS RESULTS
    # ========================================================

    for doc, meta in zip(docs, metas):

        sources.add(
            meta.get(
                "source_file",
                "Unknown"
            )
        )

        for sentence in sentence_split(doc):

            sentence = clean_text(
                sentence
            )

            if is_table_noise(sentence):
                continue

            if is_fragment(sentence):
                continue

            words = normalize_sentence(
                sentence
            ).split()

            key = " ".join(
                words[:20]
            )

            if key in seen:
                continue

            seen.add(key)

            obligation_type = classify_obligation(
                sentence
            )

            score = obligation_score(
                sentence,
                query
            )

            found_deadlines = extract_deadlines(
                sentence
            )

            for d in found_deadlines:

                deadlines.add(d)

            if obligation_type == "Mandatory":

                mandatory.append(
                    (score, sentence)
                )

            elif obligation_type == "Recommended":

                recommended.append(
                    (score, sentence)
                )

            else:

                informational.append(
                    (score, sentence)
                )

    # ========================================================
    # SORT
    # ========================================================

    mandatory.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    recommended.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    informational.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    end_time = time.time()

    # ========================================================
    # OUTPUT
    # ========================================================

    print("\n" + "=" * 90)
    print("COMPLIANCE ANSWER")
    print("=" * 90)

    print("\nQUESTION")
    print("-" * 90)
    print(query)

    print("\nMANDATORY OBLIGATIONS")
    print("-" * 90)

    if mandatory:

        for i, (_, item) in enumerate(
            mandatory[:6],
            start=1
        ):

            print(f"{i}. {item}")

    else:

        print(
            "No mandatory obligations identified."
        )

    print("\nRECOMMENDED ACTIONS")
    print("-" * 90)

    if recommended:

        for i, (_, item) in enumerate(
            recommended[:4],
            start=1
        ):

            print(f"{i}. {item}")

    else:

        print(
            "No recommendations identified."
        )

    print("\nDEADLINES")
    print("-" * 90)

    if deadlines:

        for d in sorted(deadlines):

            print(f"• {d}")

    else:

        print(
            "No explicit deadlines found."
        )

    print("\nREFERENCE DOCUMENTS")
    print("-" * 90)

    for doc in sorted(sources):

        print(f"• {doc}")

    print(
        f"\nResponse Time: "
        f"{round(end_time-start_time,2)} sec"
    )

    print("=" * 90)

print("\nGoodbye.")
