# SuRaksha Run Order & Rebuild Instructions

This document provides the exact terminal commands required to rebuild the entire pipeline from raw PDFs to final Dashboard JSONs.

## Prerequisites
Ensure Python 3.10+ is installed and you are in the `d:\SuRaksha` root directory. All source data must be present in the `dataset/` directory.

## Phase 1: Data Extraction
Convert PDFs to text, chunk them, and extract regulatory requirements.

```bash
python extract_text.py
python chunk_documents.py
python extract_requirements_v2.py
```

## Phase 2: Intelligence & Structuring
Classify the requirements, find cross-references, and build the knowledge graph.

```bash
python taxonomy_builder.py
python cross_reference_parser.py
python reference_graph_v2.py
```

## Phase 3: MAP Generation & Dashboarding
Generate intelligent task titles, assign Canara Bank departments, calculate risk scores, and aggregate UI dashboard metrics.

```bash
python map_generator.py
python map_dashboard_feed.py
```

## Phase 4: Validation (Optional, for Judges)
To prove the deterministic accuracy of the pipeline without LLMs, you can run the validation suite:

```bash
python -m unittest tests/test_map_modules.py
python phase7_quality_gate.py
python golden_set_evaluator.py
```
