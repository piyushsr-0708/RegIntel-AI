# File Movement Log

The physical layout of the repository has been permanently restructured. Below is a high-level summary of the movements executed:

### Moved to `data/`
*   `dataset/` (Raw RBI PDFs)
*   `requirements/` (Clean JSON files and taxonomies)
*   `vector_db/`, `chroma_db/`, `requirement_db/` (Vector databases)
*   `extracted_text/`, `chunks/` (Preprocessing artifacts)

### Moved to `docs/`
*   `CLEANUP_PLAN.md`, `ZIP_READINESS_REPORT.md`, `DEPENDENCY_MAP.md`, `DEMO_FLOW.md`, `RUN_ORDER.md`, `UI_CONTRACT.md`
*   All `*REPORT.md` files generated during Phase 8 and final audits.
*   All `.xlsx` inventories and `.txt` readmes.

### Moved to `archive/`
*   `gap_analysis_engine.py`, `v2`, `v3`
*   `compliance_answer_engine.py`, `v2`, `v3`, `v4`
*   `extract_requirements.py`, `change_detector_v1.py`, `change_detector_v2.py`
*   And 20+ other deprecated logic scripts.

### Moved to `archive/delete_candidates/`
*   `dummy_dir/`, `__pycache__`
*   `print_titles.py`, `check_collections.py`, `remove_duplicate_files.py`
