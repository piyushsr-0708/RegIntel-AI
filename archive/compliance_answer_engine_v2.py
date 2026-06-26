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

TOP_K = 10

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ============================================================
# COMPLIANCE KEYWORDS
# ============================================================

COMPLIANCE_WORDS = [
    "shall",
    "must",
    "required",
    "ensure",
    "maintain",
    "report",
    "submit",
    "verify",
    "monitor",
    "record",
    "preserve",
    "review",
    "identify",
    "comply"
]

# ============================================================
# LOAD MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")

# ============================================================
# LOAD CHROMADB
# ============================================================

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(path=DB_PATH)

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
# HELPER FUNCTIONS
# ============================================================

def extract_obligations(text):

    obligations = []

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    for sentence in sentences:

        s = sentence.strip()

        if len(s) < 40:
            continue

        lower = s.lower()

        if any(
            word in lower
            for word in COMPLIANCE_WORDS
        ):
            obligations.append(s)

    return obligations


def remove_duplicates(items):

    unique = []
    seen = set()

    for item in items:

        key = item.lower()[:150]

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return unique


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

    # ========================================================
    # VECTOR SEARCH
    # ========================================================

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # ========================================================
    # EXTRACT OBLIGATIONS
    # ========================================================

    obligations = []

    source_docs = set()

    for doc, meta in zip(
        documents,
        metadatas
    ):

        source_docs.add(
            meta["source_file"]
        )

        obligations.extend(
            extract_obligations(doc)
        )

    obligations = remove_duplicates(
        obligations
    )

    elapsed = round(
        time.time() - start,
        2
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    print("\n" + "=" * 90)
    print("QUESTION")
    print("-" * 90)
    print(query)

    print("\nCOMPLIANCE SUMMARY")
    print("-" * 90)

    if not obligations:

        print(
            "No explicit compliance obligations found."
        )

    else:

        for i, item in enumerate(
            obligations[:10],
            start=1
        ):

            print(
                f"{i}. {item}"
            )

            print()

    print("SOURCE DOCUMENTS")
    print("-" * 90)

    for doc in sorted(source_docs):

        print(f"• {doc}")

    print(
        f"\nResponse Time: {elapsed} sec"
    )

    print("=" * 90)

print("\nGoodbye.")
