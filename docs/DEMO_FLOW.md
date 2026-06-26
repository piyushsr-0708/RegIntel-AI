# Hackathon Demo Flow Script

This document details the exact sequence of events to present to the judges.

## Goal
Demonstrate that we have successfully bypassed the need for expensive, hallucinatory LLM agents to deliver high-quality, actionable compliance tasks (MAPs) strictly using an offline, deterministic NLP pipeline.

## 1. Input & Processing (The "Black Box")
*   **Show:** The `dataset/` directory containing the 103 raw RBI PDF circulars.
*   **Show:** Run `python map_generator.py` in the terminal.
*   **Say:** *"Our backend runs completely offline. No LLM tokens. It uses a custom deterministic heuristic engine that classifies the entire corpus in seconds."*

## 2. The Dashboard (The "Executive View")
*   **Show:** The main UI Dashboard (loading `dashboard_metrics.json`).
*   **Highlight:**
    *   **Department Risk Scores:** Show how *AML Compliance Cell* and *Compliance Department* are clearly separated.
    *   **Critical MAPs:** Point out the total count of high-priority prohibited actions.
*   **Say:** *"The UI aggregates our risk scores. We created a custom mathematical formula weighting RBI priorities, deadlines, and department vulnerability."*

## 3. Department View (The "Action View")
*   **Show:** The UI table filtering by department (loading `maps_output.json`).
*   **Highlight:**
    *   **MAP Titles:** Point out the semantic, human-readable task titles (e.g., *"Report Suspicious Transactions to FIU-IND"*, *"Maintain Customer Transaction Records"*).
    *   **Confidence Score:** Show the transparency of the assignment (e.g., *Confidence: 70%*).
*   **Say:** *"Our system doesn't just copy-paste text. It translates complex legal jargon into standard, actionable business tasks, assigning a confidence score so managers know precisely why it was routed to them."*

## 4. Knowledge Graph (The "Context View")
*   **Show:** The visual node graph (loading `reference_graph_v2.json`).
*   **Highlight:** Circular references and master directions superseding old notifications.
*   **Say:** *"To ensure no requirement is missed, our parser connects explicitly stated cross-references across documents, mapping the entire regulatory web."*
