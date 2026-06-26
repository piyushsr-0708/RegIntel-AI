import chromadb
from sentence_transformers import SentenceTransformer

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ==========================================
# CONFIG
# ==========================================

VECTOR_DB_PATH = str(PROJECT_ROOT / "data" / "vector_db")
MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 5

# ==========================================
# LOAD MODEL
# ==========================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")

# ==========================================
# LOAD CHROMADB
# ==========================================

print("Connecting to vector database...")

client = chromadb.PersistentClient(
    path=VECTOR_DB_PATH
)

collection = client.get_collection(
    "regintel_rbi"
)

print(
    f"Collection loaded. "
    f"Documents: {collection.count()}"
)

# ==========================================
# QUERY LOOP
# ==========================================

while True:

    query = input(
        "\nEnter Query (or 'exit'): "
    ).strip()

    if query.lower() == "exit":
        break

    print("\nGenerating embedding...")

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    print("\n" + "=" * 80)
    print("TOP MATCHES")
    print("=" * 80)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(docs)):

        print("\n")
        print("-" * 80)

        print(
            f"Rank       : {i+1}"
        )

        print(
            f"Source     : "
            f"{metas[i]['source_file']}"
        )

        print(
            f"Distance   : "
            f"{round(distances[i], 4)}"
        )

        print("\nChunk:\n")

        preview = docs[i][:1200]

        print(preview)

        print("\n" + "-" * 80)
