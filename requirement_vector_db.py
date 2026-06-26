import json
import chromadb

from sentence_transformers import SentenceTransformer

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ==================================================
# CONFIG
# ==================================================

INPUT_FILE = str(PROJECT_ROOT / "data/requirements/requirements_clean.json")

DB_PATH = str(PROJECT_ROOT / "data" / "requirement_db")

COLLECTION_NAME = "compliance_requirements"

# ==================================================
# MODEL
# ==================================================

print("Loading model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# ==================================================
# LOAD DATA
# ==================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    requirements = json.load(f)

print(
    f"Requirements Loaded: {len(requirements)}"
)

# ==================================================
# DB
# ==================================================

client = chromadb.PersistentClient(
    path=DB_PATH
)

try:
    client.delete_collection(
        COLLECTION_NAME
    )
except:
    pass

collection = client.create_collection(
    COLLECTION_NAME
)

# ==================================================
# PREPARE
# ==================================================

documents = []
ids = []
metadatas = []

for i, req in enumerate(requirements):

    text = req["requirement"]

    documents.append(text)

    ids.append(
        f"req_{i}"
    )

    metadatas.append(
        {
            "source_file":
            req["source_file"],

            "entity":
            req["entity"],

            "deadline":
            req["deadline"],

            "obligation_type":
            req["obligation_type"]
        }
    )

# ==================================================
# EMBEDDINGS
# ==================================================

print("Creating embeddings...")

embeddings = model.encode(
    documents,
    batch_size=32,
    show_progress_bar=True
)

# ==================================================
# STORE
# ==================================================

collection.add(
    ids=ids,
    embeddings=embeddings.tolist(),
    documents=documents,
    metadatas=metadatas
)

print()

print("="*60)
print("REQUIREMENT DATABASE CREATED")
print("="*60)
print(
    f"Indexed : {collection.count()}"
)
print("="*60)
