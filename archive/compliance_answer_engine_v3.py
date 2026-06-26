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

TOP_K = 15

# ============================================================
# OBLIGATION KEYWORDS
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
    "may ensure",
    "advised to"
]

DEADLINE_PATTERNS = [
    r"\b\d{1,2}(st|nd|rd|th)\b",
    r"within\s+\d+\s+days",
    r"within\s+\d+\s+months",
    r"before\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4}",
    r"monthly",
    r"quarterly",
    r"annually",
    r"daily",
    r"15th of the succeeding month"
]

# ============================================================
# LOAD MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")

# ============================================================
# LOAD DB
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

print("Ready.")

# ============================================================
# HELPERS
# ============================================================

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def classify_obligation(text):

    lower = text.lower()

    for word in MANDATORY_WORDS:
        if word in lower:
            return "Mandatory"

    for word in RECOMMENDED_WORDS:
        if word in lower:
            return "Recommended"

    return "Informational"


def extract_deadlines(text):

    deadlines = []

    for pattern in DEADLINE_PATTERNS:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        deadlines.extend(matches)

    return deadlines


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

    start = time.time()

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # ========================================================
    # EXTRACT OBLIGATIONS
    # ========================================================

    mandatory = []
    recommended = []
    informational = []

    deadlines = set()
    sources = set()

    seen = set()

    for doc, meta in zip(docs, metas):

        sources.add(
            meta["source_file"]
        )

        for sentence in sentence_split(doc):

            sentence = clean_text(sentence)

            key = sentence[:150]

            if key in seen:
                continue

            seen.add(key)

            obligation_type = classify_obligation(
                sentence
            )

            found_deadlines = extract_deadlines(
                sentence
            )

            for d in found_deadlines:
                deadlines.add(str(d))

            if obligation_type == "Mandatory":
                mandatory.append(sentence)

            elif obligation_type == "Recommended":
                recommended.append(sentence)

            else:
                informational.append(sentence)

    # ========================================================
    # OUTPUT
    # ========================================================

    print("\n" + "=" * 90)
    print("COMPLIANCE ANSWER")
    print("=" * 90)

    print("\nQUESTION")
    print("-" * 90)
    print(query)

    # --------------------------------------------------------

    print("\nMANDATORY OBLIGATIONS")
    print("-" * 90)

    if mandatory:

        for i, item in enumerate(
            mandatory[:10],
            start=1
        ):
            print(f"{i}. {item}")

    else:
        print("No mandatory obligations identified.")

    # --------------------------------------------------------

    print("\nRECOMMENDED ACTIONS")
    print("-" * 90)

    if recommended:

        for i, item in enumerate(
            recommended[:5],
            start=1
        ):
            print(f"{i}. {item}")

    else:
        print("No recommendations identified.")

    # --------------------------------------------------------

    print("\nDEADLINES")
    print("-" * 90)

    if deadlines:

        for d in sorted(deadlines):
            print(f"• {d}")

    else:
        print("No explicit deadlines found.")

    # --------------------------------------------------------

    print("\nREFERENCE DOCUMENTS")
    print("-" * 90)

    for doc in sorted(sources):
        print(f"• {doc}")

    # --------------------------------------------------------

    end = time.time()

    print(
        f"\nResponse Time: "
        f"{round(end-start,2)} sec"
    )

    print("=" * 90)

print("\nGoodbye.")
