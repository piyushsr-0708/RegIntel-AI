# Dependency Audit Report

This report documents the dependencies discovered via an AST (Abstract Syntax Tree) scan of all active Python files in the repository.

## 1. External Imports (Required in `requirements.txt`)
These packages must be installed for the pipeline to function correctly:
*   `chromadb`: Used in the vector databases (`vector_db`, `requirement_db`).
*   `fitz` (PyMuPDF): Used for parsing raw RBI PDFs in `extract_text.py`.
*   `networkx`: Used for generating the reference knowledge graph in `reference_graph_v2.py`.
*   `pandas`: Used for generating dataset inventory reports and Excel extractions.
*   `openpyxl`: Required by Pandas for Excel (.xlsx) read/write operations.
*   `sentence_transformers`: Used by ChromaDB / `score_documents.py` for text embedding generation.

## 2. Standard Library Imports
These are built-in Python modules and do NOT need to be installed. They represent the core NLP engine logic:
`os`, `sys`, `json`, `re`, `datetime`, `collections`, `typing`, `unittest`, `time`, `glob`, `shutil`, `ast`, `uuid`, `random`, `sqlite3`, `math`, `difflib`, `traceback`, `subprocess`, `tempfile`, `hashlib`, `copy`, `io`

## 3. Unused Dependencies
*   No external dependencies were found that are imported but entirely unused across the project, as the pipeline relies heavily on regex and standard data structures. The current `requirements.txt` is minimal and accurate.
