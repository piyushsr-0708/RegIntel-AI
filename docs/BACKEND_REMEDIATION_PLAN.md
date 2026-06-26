# Backend Remediation Plan

## Overview
This document outlines the remediation strategy for the 5 fake JSON deliverables. Because the core NLP extraction and taxonomy logic is already functioning correctly, all missing files are simply data-projection tasks. 

---

## Deliverable Analysis

### 1. `department_heatmap.json`
*   **Can it be generated from existing data?** YES.
*   **Source File:** `maps/maps_output.json` (Iterate through MAPs, grouping by `department` and counting `priority` levels).
*   **Generating Module:** `map_dashboard_feed.py`
*   **Estimated Effort:** 10–15 minutes.
*   **Risk Level:** **LOW**. Requires only standard library `collections.defaultdict` and basic counters.

### 2. `map_details.json`
*   **Can it be generated from existing data?** YES.
*   **Source File:** `maps/maps_output.json` joined with `requirements_taxonomy.json` (for source text) and `cross_references.json` (for related MAPs).
*   **Generating Module:** `map_generator.py`
*   **Estimated Effort:** 30–45 minutes.
*   **Risk Level:** **MEDIUM**. Requires joining three datasets correctly in memory before dumping to JSON to ensure `related_maps` and `source_document` fields are populated accurately.

### 3. `graph_ui.json`
*   **Can it be generated from existing data?** YES.
*   **Source File:** `reference_graph_v2.json`
*   **Generating Module:** `reference_graph_v2.py`
*   **Estimated Effort:** 20–30 minutes.
*   **Risk Level:** **LOW**. This is merely a schema transformation task, restructuring the existing NetworkX graph nodes/edges into the exact Cytoscape/D3 format the UI expects.

### 4. `top_risk_departments.json`
*   **Can it be generated from existing data?** YES.
*   **Source File:** `maps/maps_output.json` (Summing `impact_score` per department and sorting descending).
*   **Generating Module:** `map_dashboard_feed.py`
*   **Estimated Effort:** 10 minutes.
*   **Risk Level:** **LOW**. Extremely straightforward dictionary sorting.

### 5. `executive_summary.json`
*   **Can it be generated from existing data?** YES.
*   **Source File:** `maps/maps_output.json` (Aggregating critical task counts, deadlines, and global risk metrics).
*   **Generating Module:** `map_dashboard_feed.py`
*   **Estimated Effort:** 15–20 minutes.
*   **Risk Level:** **LOW**. 

---

## Priority Ranking
1.  **CRITICAL PRIORITY: `map_details.json`**. The MAP detail view is the core of the application; without it, users cannot drill down into compliance tasks to read the actual regulations.
2.  **HIGH PRIORITY: `department_heatmap.json`**. Crucial for the Department View page, which is a major judging milestone for visualizing risk distribution.
3.  **HIGH PRIORITY: `graph_ui.json`**. The Knowledge Graph is the main "AI Wow-Factor" for the demo; it must load dynamically.
4.  **MEDIUM PRIORITY: `top_risk_departments.json`**. Important for the dashboard, but the UI might be able to fallback to `department_risk_scores` in `dashboard_metrics.json` if necessary.
5.  **LOW PRIORITY: `executive_summary.json`**. Can be handled last. Much of its proposed data overlaps with the existing `dashboard_metrics.json`.

---

## Final Assessment

**Can a single developer complete all missing backend work within 4–6 hours?**

**YES. Absolutely.** 

Because the heavy lifting (the deterministic NLP rules, text extraction, cross-referencing, and vector databases) was already perfected in the frozen Phase 7 pipeline, the remaining work is entirely standard data wrangling (reshaping Python dictionaries into JSON). An experienced Python developer can easily write these 5 aggregation scripts in **under 2 hours**. 

There is zero architectural risk, zero model hallucination risk, and no external dependencies required. The project is highly salvageable before the June 26 evaluation.
