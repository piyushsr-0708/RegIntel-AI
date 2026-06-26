# Demo Simulation Report

## Judge Walkthrough Simulation

1.  **Dashboard**: The initial view works. The metrics look real.
2.  **MAPs**: The Action Plan list loads correctly from `maps_output.json`.
3.  **MAP Detail**: 
    *   *Judge Action*: The judge clicks on a specific MAP to view details. 
    *   *System Response*: The frontend loads data from the static `map_details.json`. 
    *   *Demo Risk*: If the judge asks to regenerate the MAPs from a fresh PDF upload, the MAP details will not update because the JSON is hardcoded.
4.  **Department Risk**:
    *   *Judge Action*: The judge views the heatmap.
    *   *Demo Risk*: The heatmap data (`department_heatmap.json`) is entirely fake. It does not accurately reflect the current state of `maps_output.json`.
5.  **Search**:
    *   *Judge Action*: The judge runs a keyword search for "AML".
    *   *System Response*: The search executes successfully using `search_requirements.py`. This is a strong demo point.
6.  **Graph**:
    *   *Judge Action*: The judge navigates to the Knowledge Graph.
    *   *Demo Risk*: The `graph_ui.json` is static. It does not update when new cross-references are found.

## Conclusion
The demo is highly fragile. Any judge who asks to see the backend "generate" the heatmap, graph, or executive summaries will instantly uncover that the system is faked.
