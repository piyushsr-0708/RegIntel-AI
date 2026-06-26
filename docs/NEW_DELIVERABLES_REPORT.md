# New Deliverables Report

## 1. Python Modules
*   **File**: `search_requirements.py`
*   **Purpose**: Provides a lightweight, fully-offline keyword search over the taxonomy.
*   **Inputs**: `data/requirements/requirements_taxonomy.json` and a user query string.
*   **Outputs**: JSON array printed to `stdout` containing matched requirements sorted by relevance.
*   **Dependencies**: Standard library only (`argparse`, `json`, `re`, `sys`, `pathlib`).
*   **Implementation Status**: Appears complete and functional as a standalone CLI tool.

## 2. JSON Data Payloads
*   **Files**: `maps/department_heatmap.json`, `maps/executive_summary.json`, `maps/graph_ui.json`, `maps/map_details.json`, `maps/top_risk_departments.json`
*   **Purpose**: Static JSON blobs intended to feed the UI.
*   **Inputs**: Unknown.
*   **Outputs**: Static JSON files.
*   **Dependencies**: None.
*   **Implementation Status**: **INCOMPLETE / FAKED**. There is absolutely no Python code in the repository that dynamically generates these files from the pipeline outputs. These are manually uploaded mock/static files.
