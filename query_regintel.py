import time
import chromadb

from sentence_transformers import SentenceTransformer

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

DB_PATH = str(PROJECT_ROOT / "data" / "vector_db")

COLLECTION_NAME = "regintel_rbi"

TOP_K = 5

MODEL_NAME = "all-MiniLM-L6-v2"

# ==================================================
# LOAD MODEL
# ==================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Model loaded.")

# ==================================================
# LOAD DB
# ==================================================

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=DB_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)

print(
    f"Collection loaded: {COLLECTION_NAME}"
)

print(
    f"Indexed Chunks: {collection.count()}"
)

print("Ready.")

# ==================================================
# LOOP
# ==================================================

while True:

    query = input(
        "\nEnter Query (or type exit): "
    ).strip()

    if query.lower() == "exit":
        break

    if not query:
        continue

    print("\nSearching...")

    start = time.time()

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=TOP_K
    )

    end = time.time()

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n" + "=" * 90)

    print("TOP RETRIEVAL RESULTS")

    print("=" * 90)

    print(
        f"Query Time : "
        f"{round(end-start,2)} sec"
    )

    for i in range(len(documents)):

        metadata = metadatas[i]

        print("\n" + "-" * 90)

        print(
            f"Result #{i+1}"
        )

        print(
            f"Source File : "
            f"{metadata.get('source_file')}"
        )

        print(
            f"Chunk ID    : "
            f"{metadata.get('chunk_id')}"
        )

        print(
            f"Category    : "
            f"{metadata.get('category')}"
        )

        print(
            f"Distance    : "
            f"{round(distances[i],4)}"
        )

        print("\nChunk Text:\n")

        text = documents[i]

        if len(text) > 1200:

            text = text[:1200] + "..."

        print(text)

    print("\n" + "=" * 90)

print("\nGoodbye.")
