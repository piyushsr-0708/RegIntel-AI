# SuRaksha Backend Dependency Map

The SuRaksha backend pipeline is architected as a series of decoupled scripts that communicate entirely via JSON artifacts. Direct Python imports are minimized to enforce modularity.

## Active Pipeline Imports
The following Python files import each other:

*   `department_mapper.py` imports `taxonomy_builder.py` (To load Domain Rules).
*   `golden_set_evaluator.py` imports `effective_requirement_resolver.py` (To test resolver logic).
*   `map_dashboard_feed.py` imports `deadline_tracker.py` (To calculate urgency logic).
*   `map_generator.py` imports `department_mapper.py` and `deadline_tracker.py`.
*   All `tests/test_*.py` files import their respective target modules.

## Data Flow Dependencies (JSON Architecture)
Because the modules are uncoupled, they must be executed in a specific sequence to pass data down the chain:

1.  `extract_text.py` → **[Extracted Text]**
2.  `chunk_documents.py` → **[Chunks]**
3.  `extract_requirements_v2.py` → `requirements.json`
4.  `taxonomy_builder.py` → `requirements_taxonomy.json`
5.  `cross_reference_parser.py` → `cross_references.json`
6.  `effective_requirement_resolver.py` → (Evaluates supersessions dynamically)
7.  `reference_graph_v2.py` → `reference_graph_v2.json`
8.  `map_generator.py` → `maps/maps_output.json`
9.  `map_dashboard_feed.py` → `maps/dashboard_metrics.json`

## Dead Code & Archived Modules Verification
I have used AST and regex to scan all repository imports. I can confirm that **no active module** imports or references the following deprecated files:

*   `compliance_answer_engine_v1-v4.py`
*   `gap_analysis_engine_v1-v2.py`
*   `change_detector_v1.py`
*   `change_diff_summary.py`
*   `reference_graph.py`
*   `extract_requirements.py`

These are genuinely dead code paths. They are safe to archive and omit from the final build.
