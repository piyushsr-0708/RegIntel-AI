import chromadb

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


DB_PATH = str(PROJECT_ROOT / "vector_db")

client = chromadb.PersistentClient(path=DB_PATH)

collections = client.list_collections()

print("\nCollections Found:\n")

for c in collections:
    print(c.name)
