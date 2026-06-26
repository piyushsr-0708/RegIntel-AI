# JSON Contract Validation

## UI Contract Drift
`UI_CONTRACT.md` contains NO schemas for `map_details.json`, `department_heatmap.json`, `top_risk_departments.json`, `executive_summary.json`, or `graph_ui.json`. 
Teammate 1 failed to update the contract, meaning the frontend developer will have to blindly guess the schemas by inspecting the mock files.

## Static File Validation
While the static JSON files provided parse correctly and contain required fields that match what a frontend might expect:
*   The data is entirely decoupled from the actual backend pipeline.
*   Because the contract isn't updated, any schema is technically "unvalidated."
