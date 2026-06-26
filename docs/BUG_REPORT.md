# Bug Report

## Discovered Issues

1.  **Mock Data Dependency (Medium Risk):** The frontend was delivered with a hardcoded `demo.js` file containing completely fake MAPs and requirements. (FIXED).
2.  **Schema Mismatches (Low Risk):** The mock data used `title` instead of the backend's `task_title`, and arrays instead of nested objects. (FIXED).
3.  **Missing Node Fetching Logic (Low Risk):** The UI expects synchronous data delivery. Standard API fetches would fail offline due to CORS without a static server. (FIXED by leveraging Vite's JSON bundler).

## Bug Metrics
*   **Critical Bugs**: 0
*   **High Bugs**: 0
*   **Medium Bugs**: 1 (Mock data disconnected from backend)
*   **Low Bugs**: 2

All discovered issues have been automatically remediated via the `demo.js` Adapter pattern.
