import os
import json
import hashlib
import chromadb

from sentence_transformers import SentenceTransformer

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

CHUNK_FOLDER = str(PROJECT_ROOT / "data" / "chunks")
VECTOR_DB_FOLDER = str(PROJECT_ROOT / "data" / "vector_db")

COLLECTION_NAME = "regintel_rbi"

MODEL_NAME = "all-MiniLM-L6-v2"

MIN_CHARS = 50

# ==================================================
# LOAD MODEL
# ==================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Model loaded.")

# ==================================================
# CHROMADB
# ==================================================

client = chromadb.PersistentClient(
    path=VECTOR_DB_FOLDER
)

try:
    client.delete_collection(
        COLLECTION_NAME
    )
    print("Old collection deleted.")
except:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME
)

# ==================================================
# LOAD CHUNKS
# ==================================================

documents = []
ids = []
metadatas = []

valid_chunks = 0
removed_small = 0
removed_duplicates = 0

seen_hashes = set()

print("\nScanning chunk files...")

for file in os.listdir(CHUNK_FOLDER):

    if not file.endswith(".json"):
        continue

    category = (
        file
        .replace("_chunks.json", "")
        .replace(".json", "")
    )

    filepath = os.path.join(
        CHUNK_FOLDER,
        file
    )

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    for chunk in chunks:

        text = chunk["text"].strip()

        # --------------------------------------
        # Tiny chunk removal
        # --------------------------------------

        if len(text) < MIN_CHARS:

            removed_small += 1
            continue

        # --------------------------------------
        # Duplicate removal
        # --------------------------------------

        text_hash = hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()

        if text_hash in seen_hashes:

            removed_duplicates += 1
            continue

        seen_hashes.add(text_hash)

        source_file = chunk.get(
            "source_file",
            "unknown"
        )

        chunk_id = str(
            chunk.get(
                "chunk_id",
                "0"
            )
        )

        unique_id = (
            f"{source_file}_{chunk_id}"
        )

        documents.append(text)

        ids.append(unique_id)

        metadatas.append(
            {
                "source_file": source_file,
                "chunk_id": chunk_id,
                "category": category,
                "document_name": source_file
            }
        )

        valid_chunks += 1

# ==================================================
# SUMMARY
# ==================================================

print("\n" + "=" * 60)

print("CHUNK CLEANING SUMMARY")

print("=" * 60)

print(
    f"Valid Chunks        : {valid_chunks}"
)

print(
    f"Removed Tiny Chunks : {removed_small}"
)

print(
    f"Removed Duplicates  : {removed_duplicates}"
)

print("=" * 60)

# ==================================================
# EMBEDDINGS
# ==================================================

print("\nGenerating embeddings...")

embeddings = model.encode(
    documents,
    batch_size=32,
    show_progress_bar=True
)

print("Embeddings created.")

# ==================================================
# WRITE TO CHROMA
# ==================================================

print("\nWriting to ChromaDB...")

collection.add(
    ids=ids,
    embeddings=embeddings.tolist(),
    documents=documents,
    metadatas=metadatas
)

# ==================================================
# VERIFY
# ==================================================

sample = collection.get(
    limit=1,
    include=["metadatas"]
)

print("\nSample Metadata:")

print(
    sample["metadatas"][0]
)

# ==================================================
# FINAL
# ==================================================

print("\n" + "=" * 60)

print("VECTOR DATABASE CREATED")

print("=" * 60)

print(
    f"Chunks Indexed : {collection.count()}"
)

print(
    f"Database Path  : {VECTOR_DB_FOLDER}"
)

print("=" * 60)
