# TEAM_HANDOVER: SuRaksha Backend Engine

## 1. Project Overview
SuRaksha is an RBI Regulatory Intelligence Platform built for the Cyber SuRaksha 2.0 Hackathon. The platform ingests RBI PDFs, extracts compliance requirements, builds a dynamic knowledge graph, and automatically generates prioritized, department-assigned Measurable Action Points (MAPs) for banking teams.

## 2. Current Architecture (Backend)
The backend pipeline operates entirely offline (zero external LLM calls) using deterministic NLP heuristics, regex, and vector embeddings (ChromaDB).

**Core Pipeline Modules:**
*   `extract_requirements_v2.py`: Chunks and extracts regulatory text.
*   `taxonomy_builder.py`: Classifies text into Domain/Subdomain/Obligation.
*   `effective_requirement_resolver.py`: Evaluates applicability and active status.
*   `cross_reference_parser.py`: Links related requirements and maps dependencies.
*   `reference_graph_v2.py`: Builds a queryable Knowledge Graph.
*   `department_mapper.py`: Strictly assigns specific Canara Bank departments using confidence scoring.
*   `map_generator.py`: Generates the final intelligent MAP tasks and risk scores.
*   `map_dashboard_feed.py`: Aggregates the data into UI-ready metrics.

## 3. How to Run
The backend is completely functional and outputs directly to JSON for UI consumption.

To regenerate the intelligence MAPs and dashboard feeds:
```bash
python map_generator.py
python map_dashboard_feed.py
```
This will overwrite the contents of the `maps/` directory.

## 4. Known Limitations
1.  **Resolver Accuracy:**
    Golden-set evaluation shows approximately:
    - Top-1 Accuracy: 24%
    - Top-3 Accuracy: 36%
    - Top-5 Accuracy: 36%
    
    The resolver is suitable as a regulatory search assistant and evidence retrieval tool but should not be presented as a fully autonomous compliance decision engine. (See `GOLDEN_SET_FINDINGS.md` for details).
2.  **No Automated Crawling:** The system processes PDFs present in the `dataset/` directory. Automated web scraping of the RBI site is not implemented.
3.  **Static UI Integration:** Currently, UI components must poll or read the JSON files in the `maps/` directory. There is no active API server (e.g., FastAPI) hosting the endpoints.

## 5. Handover Assignments (June 21 - June 25)
With the backend largely finalized, the project is officially in UI/Demo focus mode. The backend is frozen; no new features, taxonomy rebuilds, or validation frameworks should be added.

**Teammate 1 (Backend/UI Support Only):**
Priority order:
1. MAP Detail View JSON endpoint/file
2. Department Risk Dashboard JSON
3. Knowledge Graph JSON cleanup
4. Demo data generation
*(Nothing else).*

**Teammate 2 (100% UI Focus):**
Build these 5 pages to maximize hackathon points:
1. Dashboard
2. MAPs Table
3. Department View
4. Knowledge Graph
5. Requirement Search

**Demo Preparation:**
1. Finalize cleanup (build the Handover ZIP).
2. Prepare a scripted demo walkthrough that highlights the offline accuracy.

## 6. UI Integration Points
The Frontend/UI team does NOT need to interact with the Python backend. They simply need to read the JSON outputs generated in the `maps/` directory.

**Integration Files:**
*   `maps/maps_output.json`: The core list of all MAPs, containing task titles, department assignments, deadlines, and impact scores. Use this for the main data table.
*   `maps/dashboard_metrics.json`: Pre-calculated KPI aggregates (Total MAPs, Critical MAPs, Department Risk Scores, Upcoming Deadlines). Use this for top-level dashboard widgets.
*   `maps/department_summary.json`: A simple map of department to task count. Useful for pie charts.
*   `maps/priority_summary.json`: A simple map of priority level to task count. Useful for bar charts.

## 7. JSON Outputs Available
In addition to the `maps/` directory, the following data sets are available for the UI/graphing features:
*   `requirements/requirements_taxonomy.json`: The fully classified raw dataset.
*   `cross_references.json`: The parsed dependencies between different requirements.
*   `reference_graph_v2.json`: The structured knowledge graph (suitable for visual rendering tools like D3.js or Cytoscape).
