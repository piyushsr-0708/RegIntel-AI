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

TOP_K = 10

# ============================================================
# KEYWORDS
# ============================================================

COMPLIANCE_KEYWORDS = [
    "shall",
    "must",
    "required",
    "ensure",
    "report",
    "submit",
    "maintain",
    "verify",
    "monitor",
    "preserve",
    "record",
    "review",
    "deadline",
    "within",
    "monthly",
    "quarterly",
    "annually"
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
# SCORE CHUNK
# ============================================================

def score_chunk(text):

    text_lower = text.lower()

    score = 0

    for keyword in COMPLIANCE_KEYWORDS:

        score += text_lower.count(keyword)

    return score

# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()

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

    # ========================================================
    # EMBEDDING
    # ========================================================

    query_embedding = model.encode(
        query
    ).tolist()

    # ========================================================
    # RETRIEVE
    # ========================================================

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # ========================================================
    # RANK RESULTS
    # ========================================================

    ranked_results = []

    for doc, meta in zip(
        documents,
        metadatas
    ):

        score = score_chunk(doc)

        ranked_results.append(
            (
                score,
                doc,
                meta
            )
        )

    ranked_results.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    final_chunks = []

    seen = set()

    for score, doc, meta in ranked_results:

        key = clean_text(doc[:300])

        if key in seen:
            continue

        seen.add(key)

        final_chunks.append(
            (
                score,
                doc,
                meta
            )
        )

    # ========================================================
    # BUILD ANSWER
    # ========================================================

    answer_lines = []

    sources = set()

    entities = set()

    for score, doc, meta in final_chunks[:5]:

        source_file = meta.get(
            "source_file",
            "Unknown"
        )

        category = meta.get(
            "category",
            "Unknown"
        )

        sources.add(source_file)

        entities.add(category)

        cleaned = clean_text(doc)

        if len(cleaned) > 350:
            cleaned = cleaned[:350] + "..."

        answer_lines.append(
            f"• {cleaned}"
        )

    end_time = time.time()

    # ========================================================
    # DISPLAY
    # ========================================================

    print("\n" + "=" * 90)

    print("QUESTION")
    print("-" * 90)
    print(query)

    print("\nCOMPLIANCE GUIDANCE")
    print("-" * 90)

    for line in answer_lines:

        print(line)
        print()

    print("APPLICABLE DOMAINS")
    print("-" * 90)

    for entity in sorted(entities):

        print(entity)

    print()

    print("SOURCE DOCUMENTS")
    print("-" * 90)

    for source in sorted(sources):

        print(source)

    print()

    print(
        f"Response Time: "
        f"{round(end_time-start_time,2)} sec"
    )

    print("=" * 90)

print("\nGoodbye.")
