# Demo Risk Report

## Demo Breaking Bugs & Risks
As a hackathon judge evaluating this platform on June 26, the following risks are immediately apparent:

### CRITICAL Risks
*   **Missing Features**: The pitch (based on the "new backend features") promises Executive Summaries, Department Heatmaps, and interactive Graph UIs. Because the JSON files for these features do not exist in the repository, any attempt to click into these tabs during the demo will result in a blank screen or a 404 error. The judges will immediately notice that half the platform is fake/non-functional.

### HIGH Risks
*   **Accuracy Bottleneck**: The backend has a rigid 24% Top-1 accuracy constraint. While this is acceptable if framed correctly as a "human-in-the-loop search assistant," any judge trying to input a novel query and expecting a perfect automated answer will expose the system's failure rate instantly.

### MEDIUM Risks
*   **No API Server**: The entire UI relies on static JSON files. Judges checking the network tab will see no real-time processing, exposing that the pipeline must be run manually via CLI before the UI can update.

## Conclusion
The demo is currently poised for catastrophic failure due to the missing JSON endpoints that the frontend expects.
