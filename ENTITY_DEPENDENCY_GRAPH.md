# ENTITY DEPENDENCY GRAPH

## REQUIREMENTS

**Created by:**
- Backend: `POST /admin/process-document` (crud.create_requirement)
- Demo: Static JSON file `requirements_taxonomy.json` (2941 records)

**Stored in:**
- Backend: `requirements` table (PostgreSQL/SQLite)
- Demo: `data/requirements_taxonomy.json`
- Frontend: `demo.js` → `requirementsTaxonomy` array
- Session: `session.analysis.requirements` (filtered demo subset)

**Modified by:**
- Backend: None (immutable after creation)
- Frontend: None

**Read by:**
- Backend: `GET /admin/requirements`, `GET /admin/requirements/by-semantic-id/{id}`
- Frontend: Requirements.jsx (demo only), AnalysisSession.generateDocumentAnalysis()

**Deleted by:**
- Backend: None (no delete endpoint)
- Frontend: None

**API endpoints:**
- `POST /admin/process-document` (creates)
- `GET /admin/requirements` (lists)
- `GET /admin/requirements/by-semantic-id/{id}` (detail)
- `GET /admin/requirements/unassigned` (filter)

**React Context:**
- AnalysisSession: `session.analysis.requirements` (demo-derived)

**Pages using it:**
- Requirements.jsx (demo data only - 2941 records)
- Pipeline results (via session - ~180 filtered demo records)
- Dashboard session mode (via session.analysis.stats)
- Knowledge Graph (via session for requirement text lookup)

---

## MAPs (Mitigation Action Plans)

**Created by:**
- Demo ONLY: Static JSON file `maps_output.json` (2941 records)
- Backend: NONE (no MAP table exists!)

**Stored in:**
- Demo: `data/maps_output.json`, `data/map_details.json`
- Frontend: `demo.js` → `mapsOutput`, `mapDetails` objects
- Session: `session.analysis.maps` (filtered demo subset)
- Backend: N/A (concept doesn't exist in backend!)

**Modified by:**
- None (demo data is static)

**Read by:**
- Frontend: Maps.jsx, MapDetail.jsx, AnalysisSession.generateDocumentAnalysis()

**Deleted by:**
- None

**API endpoints:**
- NONE! No backend support for MAPs

**React Context:**
- AnalysisSession: `session.analysis.maps` (demo-derived)

**Pages using it:**
- Maps.jsx (global: 2941 demo, document scoped: ~85 filtered demo)
- MapDetail.jsx (demo mapDetails only)
- Pipeline results (via session)
- Dashboard session mode (via session.analysis.stats)

**🚨 CRITICAL:** MAPs exist ONLY in frontend demo data, not in backend!

---

## ASSIGNMENTS

**Created by:**
- Backend: `POST /admin/process-document` (crud.create_assignment)
- Backend: `POST /admin/assignments` (crud.create_assignment)

**Stored in:**
- Backend: `assignments` table (PostgreSQL/SQLite)
- Frontend: None (only temporary API response cache)

**Modified by:**
- Backend: `POST /assignment-center/publish` (sets is_published=true)
- Backend: `POST /workspace/complete/{id}` (sets status=completed)

**Read by:**
- Backend: All assignment APIs
- Frontend: AssignmentCenter.jsx, DepartmentWorkspace.jsx (via API)

**Deleted by:**
- Backend: None (no delete endpoint)

**API endpoints:**
- `POST /admin/process-document` (creates batch)
- `POST /admin/assignments` (creates single)
- `GET /admin/assignments` (lists all)
- `GET /admin/assignments/{id}` (detail)
- `GET /assignment-center/summary` (unpublished by department)
- `POST /assignment-center/publish` (publishes by department)
- `GET /workspace/tasks` (department user view)
- `POST /workspace/complete/{id}` (marks complete)

**React Context:**
- None (always fetched fresh from API)

**Pages using it:**
- AssignmentCenter.jsx (unpublished)
- DepartmentWorkspace.jsx (published, by department)
- Dashboard operational mode (aggregated stats)

---

## DEPARTMENTS

**Created by:**
- Backend: Seed script only (crud.seed_database)
- Demo: Static JSON files (department_summary.json, department_heatmap.json)

**Stored in:**
- Backend: `departments` table (9 records)
- Demo: `data/department_*.json`
- Frontend: `demo.js` → `departmentSummary`, `departmentHeatmap`
- Session: `session.analysis.departments` (computed from demo maps)

**Modified by:**
- Backend: None (static reference data)

**Read by:**
- Backend: All routers (for department_id lookups)
- Frontend: All pages (via API or demo)

**Deleted by:**
- None

**API endpoints:**
- `GET /admin/departments` (lists all)
- Embedded in other responses (assignment summary, dashboard stats)

**React Context:**
- AnalysisSession: `session.analysis.departments` (computed from session.analysis.maps)

**Pages using it:**
- All pages (for department names)
- Dashboard (department risk scores)
- Departments.jsx (risk analysis)
- Pipeline results (department breakdown)

---

## DASHBOARD STATS

**Created by:**
- Backend: Computed on-demand (crud.get_dashboard_summary)
- Demo: Static JSON `dashboard_metrics.json`
- Session: Computed from session.analysis.stats

**Stored in:**
- Backend: NONE (computed from assignments/requirements tables)
- Demo: `data/dashboard_metrics.json`
- Frontend: `dashboardStats` local state (temporary API cache)
- Session: `session.analysis.stats` (computed from demo)

**Modified by:**
- Backend: Recomputed on each API call
- Session: Recomputed on session creation

**Read by:**
- Dashboard.jsx (3-way switch: session → API → demo)

**Deleted by:**
- None (ephemeral)

**API endpoints:**
- `GET /admin/dashboard` (computes and returns)
- `GET /assignment-center/admin-summary` (completion stats)

**React Context:**
- AnalysisSession: `session.analysis.stats`

**Pages using it:**
- Dashboard.jsx (primary consumer)

---

## SESSION

**Created by:**
- Frontend: `createSession()` in AnalysisSession.jsx
- Triggered by: Pipeline.jsx after document processing

**Stored in:**
- Frontend: AnalysisSession context state
- NOT in localStorage, NOT in backend

**Modified by:**
- Frontend: `resetSession()` (clears)

**Read by:**
- All pages via `useAnalysisSession()` hook

**Deleted by:**
- Frontend: `resetSession()` or page refresh

**API endpoints:**
- None (session is frontend-only concept)

**React Context:**
- AnalysisSession (owns it)

**Pages using it:**
- Pipeline.jsx (creates and displays)
- Dashboard.jsx (session mode)
- Maps.jsx (document scoped mode)
- Graph.jsx (active mode)
- All pages (check hasSession)

---

## KNOWLEDGE GRAPH

**Created by:**
- Demo: Static JSON `reference_graph_v2.json` (global graph)
- Session: Computed by generateDocumentAnalysis() (document graph)

**Stored in:**
- Demo: `data/reference_graph_v2.json`
- Frontend: `demo.js` → `graphData`
- Session: `session.analysis.scopedGraph`
- Backend: NONE (no graph storage)

**Modified by:**
- None (demo is static, session is computed once)

**Read by:**
- Graph.jsx (switches between global demo and session scoped)

**Deleted by:**
- Session graph: cleared with resetSession()

**API endpoints:**
- `GET /admin/requirements/by-semantic-id/{id}` (fetches requirement text for nodes)
- No endpoints for graph structure itself

**React Context:**
- AnalysisSession: `session.analysis.scopedGraph`

**Pages using it:**
- Graph.jsx (only consumer)

---

## FINAL ANALYSIS

### 1. Which entity is canonical?

**ASSIGNMENTS** - Only entity with single source of truth (backend database)
- No demo data
- No session copy
- No frontend duplication
- Always fetched from API

### 2. Which entities are derived?

- **Dashboard Stats** - Computed from Requirements + Assignments
- **Knowledge Graph** - Constructed from Requirements + MAPs/Assignments
- **Session** - Aggregates multiple entities for temporary display

### 3. Which entities should never be persisted?

- **Dashboard Stats** - Always compute on-demand
- **Session** - Ephemeral UI state only
- **Knowledge Graph** - Frontend visualization only (until backend graph service exists)

### 4. Which entities are duplicated?

**Requirements:** 4 copies
- Backend DB (14) ✅ Canonical
- Demo JSON (2941) ❌ Delete
- Demo aggregator ❌ Delete
- Session (180) ❌ Fetch from backend

**MAPs:** 2 copies
- Demo JSON (2941) ❌ Delete (not real MAPs!)
- Session (85) ❌ Should use Assignments

**Departments:** 3 copies
- Backend DB (9) ✅ Canonical
- Demo JSON ❌ Delete
- Session computed ❌ Fetch from backend

**Dashboard Stats:** 3 copies
- Backend computed ✅ Canonical
- Demo JSON ❌ Delete
- Session computed ❌ Fetch from backend

**Knowledge Graph:** 2 copies
- Demo JSON ❌ Delete or mark as example
- Session computed ⚠️ Acceptable until backend implements

**ROOT PROBLEM:** Requirements, MAPs, Departments, Dashboard Stats all duplicated with conflicting values!
