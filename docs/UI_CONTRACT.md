# UI JSON Contract

The Frontend UI should be built exclusively by reading the static JSON files listed below. No API server is required.

## 1. `maps/dashboard_metrics.json`
**Purpose:** Top-level metrics for the main executive dashboard.
**Schema Snippet:**
```json
{
  "total_maps": 2941,
  "critical_maps": 69,
  "high_maps": 1103,
  "departments_impacted": 9,
  "upcoming_deadlines": 74,
  "top_risk_department": "Compliance Department",
  "department_risk_scores": {
    "AML Compliance Cell": 17622,
    "Compliance Department": 48708
  },
  "compliance_summary": {
    "pending_tasks": 2941
  }
}
```

## 2. `maps/maps_output.json`
**Purpose:** The core data table backing the "Action Plan" or "MAP List" views.
**Schema Snippet:**
```json
[
  {
    "map_id": "MAP_MD18KYCF_0184_F36A90",
    "requirement_id": "REQ_MD18KYCF_0184_F36A90",
    "task_title": "Implement Wire Transfer Controls",
    "task_description": "REs shall ensure that they do not process cross-border transactions...",
    "department": "AML Compliance Cell",
    "department_confidence": 55,
    "matched_keywords": ["screening"],
    "priority": "Critical",
    "impact_score": 70,
    "impact_reasoning": {
      "priority": 50,
      "department": 20,
      "deadline": 0,
      "cross_reference": 0
    },
    "deadline": null,
    "status": "Pending"
  }
]
```

## 3. `maps/department_summary.json` & `maps/priority_summary.json`
**Purpose:** Simple key-value mappings for generating Pie/Bar charts in the UI.
**Schema Snippet:**
```json
{
  "Compliance Department": 1445,
  "KYC Operations": 461,
  "AML Compliance Cell": 395
}
```

## 4. `requirements/requirements_taxonomy.json`
**Purpose:** Backs the "Requirement Search" page for exploring raw regulatory classifications.
**Schema Snippet:**
```json
[
  {
    "requirement_id": "REQ_MD18KYCF_0184_F36A90",
    "domain": "AML",
    "subdomain": "Cross Border Wire Transfers",
    "obligation_type": "Prohibited",
    "source_document": "MD18KYCF6E92C82E1E1419D87323E3869BC9F13.pdf",
    "effective_status": "Active"
  }
]
```

## 5. `reference_graph_v2.json`
**Purpose:** Backs the "Knowledge Graph" visualizer (e.g., Cytoscape.js or D3).
**Schema Snippet:**
```json
{
  "nodes": [{"id": "REQ_123", "label": "AML", "type": "requirement"}],
  "edges": [{"source": "REQ_123", "target": "REQ_456", "label": "supersedes"}]
}
```
