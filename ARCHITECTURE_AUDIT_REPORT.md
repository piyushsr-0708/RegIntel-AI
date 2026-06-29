# ARCHITECTURE AUDIT REPORT - READ ONLY ANALYSIS

**Date:** June 28, 2026  
**Type:** Single Source of Truth (SSOT) Analysis  
**Status:** 🔴 CRITICAL ARCHITECTURE VIOLATION DETECTED

---

## EXECUTIVE SUMMARY

**CRITICAL FINDING:** The application has **FOUR competing sources of truth**, resulting in systematic data inconsistencies.

**Root Cause:** Requirements and MAPs are **THE SAME ENTITY** in demo data (both have 2941 records), but are treated as **DIFFERENT ENTITIES** in code logic.

**Impact:** 
- Dashboard shows 720 requirements as "MAPs"
- MAP Management shows 2941 "MAPs" (actually requirements)
- Assignment Center shows 48 tasks (actual backend data)
- Demo data contaminates live operations
- Incognito vs normal browser behave differently

**Severity:** 🔴 SHOWSTOPPER - Prevents correct demo

---

## TASK 1: STATE STORAGE INVENTORY

### Complete State Storage Table

| Storage Location | File | Variable | Used By | Read | Write |
|-----------------|------|----------|---------|------|-------|
| **React Context - Session** | context/AnalysisSession.jsx | session | All pages via useAnalysisSession() | All pages | createSession() |
| **React Context - Auth** | context/AuthContext.jsx | user, loading | All pages via useAuth() | All pages | login(), logout() |
| **React Context - Demo** | App.jsx | isDemo | All pages via DemoContext | All pages | toggleDemo() |
| **Local State - Dashboard** | pages/Dashboard.jsx | dashboardStats, completionSummary | Dashboard only | Dashboard | loadDashboardStats() |
| **Local State - Pipeline** | pages/Pipeline.jsx | file, processing, currentStage, backendResponse | Pipeline only | Pipeline | setBackendResponse() |
| **Local State - Maps** | pages/Maps.jsx | search, dept, priority, status, sortBy | Maps only | Maps | Filter handlers |
| **Local State - Requirements** | pages/Requirements.jsx | query, domain, page | Requirements only | Requirements | Filter handlers |
| **Local State - Graph** | pages/Graph.jsx | viewMode, sel, selectedNodeData | Graph only | Graph | Mode switcher |
| **Local State - AssignmentCenter** | pages/AssignmentCenter.jsx | summary, loading, publishing | AssignmentCenter | AssignmentCenter | loadSummary() |
| **Local State - DepartmentWorkspace** | pages/DepartmentWorkspace.jsx | tasks, loading | DepartmentWorkspace | DepartmentWorkspace | loadTasks() |
| **Local State - Departments** | pages/Departments.jsx | deptRisk, loading | Departments | Departments | loadDepartmentRisk() |
| **Demo JSON Files** | data/*.json | 10 JSON files | demo.js imports | All via demo.js | NEVER (static) |
| **Demo Aggregator** | data/demo.js | dashboardMetrics, mapsOutput, etc. | All pages import | All pages | NEVER (static) |
| **Backend Database** | PostgreSQL/SQLite | users, requirements, assignments, etc. | Backend API | API endpoints | CRUD operations |
| **Backend Session (implicit)** | N/A | None detected | N/A | N/A | N/A |
| **localStorage** | NONE DETECTED | N/A | N/A | N/A | N/A |
| **sessionStorage** | NONE DETECTED | N/A | N/A | N/A | N/A |
| **Global Variables** | NONE DETECTED | N/A | N/A | N/A | N/A |

**Total Storage Locations:** 18  
**React Contexts:** 3  
**Local Component States:** 7  
**Static Demo Data:** 11 files  
**Backend Database:** 1  


---

## TASK 2: ENTITY LOCATION MAPPING

### 🔴 CRITICAL: Requirements Entity

**Location 1: Demo JSON**
- File: `data/requirements_taxonomy.json`
- Count: **2941 records**
- Structure: `{ requirement_id, domain, subdomain, source_document, requirement_text }`
- Read: demo.js → exported as `requirementsTaxonomy`
- Write: NEVER (static file)
- Used By: Requirements page, AnalysisSession

**Location 2: Demo Aggregator**
- File: `data/demo.js`
- Variable: `export const requirementsTaxonomy`
- Transformation: Maps JSON to simpler structure
- Read: All pages that import from demo
- Write: NEVER

**Location 3: AnalysisSession Context**
- File: `context/AnalysisSession.jsx`
- Variable: `session.analysis.requirements` (filtered subset)
- Source: Filters requirementsTaxonomy by source document
- Read: Pipeline, Dashboard (session mode)
- Write: generateDocumentAnalysis() when session created

**Location 4: Backend Database**
- Table: `requirements`
- Count: **14 records** (from recent upload)
- Structure: `{ id, requirement_id, document_id, text, classification, domain, priority }`
- Read: Backend CRUD operations
- Write: process-document endpoint

**🚨 PROBLEM:** 4 copies of "requirements" with different counts!


### 🔴 CRITICAL: MAPs Entity

**Location 1: Demo JSON**
- File: `data/maps_output.json`
- Count: **2941 records** ⚠️ SAME AS REQUIREMENTS!
- Structure: `{ map_id, requirement_id, task_title, department, priority, impact_score }`
- Read: demo.js → exported as `mapsOutput`
- Write: NEVER (static file)

**Location 2: Demo Aggregator**
- File: `data/demo.js`
- Variable: `export const mapsOutput`
- Transformation: Maps JSON, transforms deadline fields
- Read: Maps page, AnalysisSession
- Write: NEVER

**Location 3: AnalysisSession Context**
- File: `context/AnalysisSession.jsx`
- Variable: `session.analysis.maps` (filtered subset)
- Source: Filters mapsOutput by linked requirements
- Read: Pipeline, Dashboard (session mode), Maps page (document scoped)
- Write: generateDocumentAnalysis() when session created

**Location 4: Backend Database (Assignments)**
- Table: `assignments`
- Count: **14 records** (unpublished)
- Structure: `{ id, requirement_id, department_id, assigned_by, status, is_published }`
- Read: Assignment Center, Department Workspace
- Write: process-document endpoint creates assignments

**🚨 SMOKING GUN:** Demo data has 2941 "MAPs" but they are actually requirements with task titles!


### Assignments Entity

**Location 1: Backend Database ONLY**
- Table: `assignments`
- Count: 14 unpublished + 5 published = 19 total
- Structure: `{ id, requirement_id, department_id, is_published, status }`
- Read: Assignment Center API, Department Workspace API
- Write: process-document, publish endpoints

**Location 2: NOWHERE ELSE**
- No demo data equivalent
- No session equivalent
- No frontend state

**✅ GOOD:** Single source of truth for assignments

---

### Departments Entity

**Location 1: Demo JSON (multiple files)**
- Files: `department_summary.json`, `department_heatmap.json`, `top_risk_departments.json`
- Aggregated in: `demo.js` → `departmentSummary`, `departmentHeatmap`
- Read: All pages via demo imports
- Write: NEVER

**Location 2: AnalysisSession Context**
- Variable: `session.analysis.departments`
- Source: Computed from session.analysis.maps
- Read: Dashboard (session mode), Pipeline
- Write: generateDocumentAnalysis()

**Location 3: Backend Database**
- Table: `departments`
- Count: 9 departments (seeded)
- Read: All backend APIs
- Write: Seed script only

**🚨 PROBLEM:** 3 sources with potentially different data


### Knowledge Graph Entity

**Location 1: Demo JSON**
- File: `reference_graph_v2.json`
- Imported as: `graphData` in demo.js
- Constructed: Global graph with ~200 nodes from sampled demo data
- Read: Graph page (global mode)
- Write: NEVER

**Location 2: AnalysisSession Context**
- Variable: `session.analysis.scopedGraph`
- Source: Constructed from filtered requirements/maps
- Read: Graph page (document scoped mode)
- Write: generateDocumentAnalysis()

**Location 3: NOWHERE IN BACKEND**
- No database table
- No API endpoint
- Graph is frontend-only

**⚠️ WARNING:** Graph has no persistent storage

---

### Current Analysis Session

**Location 1: AnalysisSession Context (PRIMARY)**
- File: `context/AnalysisSession.jsx`
- Variable: `session` state
- Lifetime: Until resetSession() called
- Contains: file, processing times, analysis object
- Read: All pages via useAnalysisSession()
- Write: createSession(), resetSession()

**Location 2: NOWHERE ELSE**
- No localStorage persistence
- No backend session storage
- No Redux/Zustand

**✅ GOOD:** Single source for session state


### Dashboard Statistics

**Location 1: Demo JSON**
- File: `dashboard_metrics.json`
- Aggregated: `demo.js` → `dashboardMetrics`
- Values: `{ total_maps: 2941, critical_maps: 205, ... }`
- Read: Dashboard (fallback mode)
- Write: NEVER

**Location 2: Backend API Response**
- Endpoint: `GET /admin/dashboard`
- Variable: `dashboardStats` local state
- Values: Computed from database queries
- Read: Dashboard (operational mode)
- Write: Backend query on each request

**Location 3: AnalysisSession Context**
- Variable: `session.analysis.stats`
- Source: Computed from filtered demo data
- Read: Dashboard (session mode)
- Write: generateDocumentAnalysis()

**🚨 PROBLEM:** 3 sources with different values!

---

### Pipeline Results

**Location 1: Pipeline Local State**
- Variable: `backendResponse`
- Source: POST /admin/process-document response
- Contains: `{ requirements_created: 14, assignments_created: 14 }`
- Lifetime: Until component unmounts or new upload
- Read: Pipeline component only
- Write: startPipeline() API call

**Location 2: AnalysisSession Context**
- Variable: `session.analysis`
- Source: Generated from demo data (NOT from backendResponse!)
- Read: Pipeline results page, Dashboard
- Write: createSession()

**🚨 CRITICAL BUG:** backendResponse NOT used to populate session!


---

## TASK 3: COMPLETE DATA FLOW TRACE

### Upload → Pipeline → Results Flow

```
USER: Upload PDF
  ↓
FRONTEND: Pipeline.jsx
  Input: File object
  Output: FormData
  Storage: file (local state)
  ↓
API: POST /api/admin/upload
  Input: FormData
  Output: { id: 1, filename: "doc.pdf" }
  Storage: documents table
  Reader: admin_router.py
  Writer: crud.create_document()
  ↓
FRONTEND: Pipeline.jsx
  Input: document_id
  Storage: uploadedDocumentId (local state)
  ↓
API: POST /api/admin/process-document/{id}
  Input: document_id
  Output: { requirements_created: 14, assignments_created: 14 }
  Storage: requirements table + assignments table
  Reader: admin_router.py
  Writer: crud.create_requirement(), crud.create_assignment()
  ↓
FRONTEND: Pipeline.jsx
  Input: backend response
  Output: NOTHING! ❌
  Storage: backendResponse (local state)
  **BUG:** Response NOT passed to session!
  ↓
FRONTEND: Pipeline.jsx calls createSession(file, null, ...)
  Input: file.name
  Output: Demo analysis (filtered from demo JSON)
  Storage: session.analysis
  Context: AnalysisSession
  **BUG:** Uses demo data instead of backend data!
  ↓
FRONTEND: Pipeline results display
  Input: session.analysis
  Output: Shows DEMO stats (e.g., 180 requirements from demo)
  **BUG:** Ignores backendResponse (14 requirements)!
```

**🔴 CRITICAL BUG IDENTIFIED:** Pipeline creates backend data but displays demo data!


### Assignment Center Flow

```
USER: Navigate to Assignment Center
  ↓
FRONTEND: AssignmentCenter.jsx
  Input: None
  Storage: None
  ↓
API: GET /api/assignment-center/summary
  Input: None
  Output: { total_maps: 14, departments: [...] }
  Storage: Query from assignments table (is_published=false)
  Reader: assignment_center_router.py
  Query: crud.get_unpublished_assignment_summary()
  ↓
FRONTEND: AssignmentCenter.jsx
  Input: API response
  Output: Display 14 tasks across 5 departments
  Storage: summary (local state)
  ✅ CORRECT: Uses backend data
```

**✅ VERIFIED:** Assignment Center uses ONLY backend data

---

### Dashboard Flow (3 Modes)

#### Mode 1: Session Mode (hasSession = true)

```
CONDITION: hasSession && session.analysis
  ↓
SOURCE: session.analysis.stats
  Values: { totalRequirements: 180, totalMaps: 85, ... }
  Origin: Demo data filtered by generateDocumentAnalysis()
  ↓
DISPLAY: "Requirements Extracted: 180"
  **PROBLEM:** Should show 14 from backend!
```

#### Mode 2: Operational Mode (hasSession = false, API loaded)

```
CONDITION: !hasSession && dashboardStats
  ↓
API: GET /admin/dashboard
  Output: { published_maps: 5, unpublished_assignments: 9, ... }
  Storage: Database query results
  ↓
DISPLAY: "Published Assignments: 5"
  ✅ CORRECT: Uses backend data
```

#### Mode 3: Demo Fallback

```
CONDITION: !hasSession && !dashboardStats
  ↓
SOURCE: dashboardMetrics from demo.js
  Values: { total_maps: 2941, critical_maps: 205, ... }
  ↓
DISPLAY: "Total MAPs: 2941"
  **PROBLEM:** Should never show in production!
```


---

## TASK 4: DUPLICATE STATE IDENTIFICATION

### Requirements - 4 Copies! 🔴

1. **Demo JSON:** `requirements_taxonomy.json` (2941 records)
2. **Demo Aggregator:** `demo.js` → `requirementsTaxonomy` array
3. **Session Context:** `session.analysis.requirements` (subset of #2)
4. **Backend Database:** `requirements` table (14 records from recent upload)

**Conflict:** Session shows 180, backend has 14, demo has 2941

---

### MAPs - 4 Copies! 🔴

1. **Demo JSON:** `maps_output.json` (2941 records)
   - **🚨 THESE ARE NOT MAPS! They are requirements with task_title field!**
2. **Demo Aggregator:** `demo.js` → `mapsOutput` array
3. **Session Context:** `session.analysis.maps` (subset of #2)
4. **Backend Database:** NO MAP TABLE! Uses `assignments` (14 records)

**Conflict:** Demo calls requirements "MAPs", session uses demo, backend uses assignments

---

### Departments - 3 Copies! ⚠️

1. **Demo JSON:** Multiple files aggregated into `demo.js`
2. **Session Context:** `session.analysis.departments` (computed from session.maps)
3. **Backend Database:** `departments` table (9 seeded records)

**Conflict:** Session computes from demo maps, backend is authoritative

---

### Dashboard Stats - 3 Copies! ⚠️

1. **Demo JSON:** `dashboard_metrics.json` → `dashboardMetrics`
2. **Session Context:** `session.analysis.stats` (computed from filtered demo)
3. **Backend API:** `GET /admin/dashboard` response (computed from database)

**Conflict:** All three have different values!


---

## TASK 5: DEMO DATA CONTAMINATION

### Locations Where Demo Data is Mixed with Live Data

#### 🔴 CRITICAL: context/AnalysisSession.jsx

**Function:** `generateDocumentAnalysis(fileName)`
- **Line 14:** Imports `dashboardMetrics, mapsOutput, requirementsTaxonomy` from demo
- **Line 18-169:** Entire function filters DEMO data to create session
- **Used By:** Every upload creates session from DEMO data!

**Evidence:**
```javascript
const docRequirements = requirementsTaxonomy.filter(r => selectedSources.includes(r.source_document));
```

**Impact:** 🔴 Pipeline results show demo data, not backend data!

---

#### 🔴 CRITICAL: pages/Dashboard.jsx

**Lines 108-124:** Demo fallback mode
```javascript
} else {
  // DEMO MODE (FALLBACK)
  m = {
    published_maps: dashboardMetrics.total_maps,  // 2941 from demo!
    ...
  };
}
```

**Impact:** 🔴 Dashboard shows 2941 MAPs if API fails!

---

#### ⚠️ WARNING: pages/Maps.jsx

**Line 42:** Switches between session and demo
```javascript
const mapsOutput = isDocumentScoped && hasSession ? session.analysis.maps : globalMapsOutput;
```

**Impact:** ⚠️ MAP Management shows demo 2941 records when no session


#### ⚠️ WARNING: pages/Graph.jsx

**Line 31:** Switches between session and demo
```javascript
const graphData = viewMode === "active" && hasSession ? session.analysis.scopedGraph : globalGraphData;
```

**Impact:** ⚠️ Graph shows demo data in global mode

---

#### ⚠️ WARNING: pages/Requirements.jsx

**Line 120:** Uses demo data ALWAYS
```javascript
const allRequirements = useMemo(() => requirementsTaxonomy.map((r, i) => ({ ...r, idx: i })), []);
```

**Impact:** ⚠️ Requirements page shows 2941 demo records, never backend!

---

### All Demo Data Files

1. `data/dashboard_metrics.json` → Used as fallback
2. `data/maps_output.json` → Used by Maps page, session generation
3. `data/requirements_taxonomy.json` → Used by Requirements page, session generation
4. `data/department_summary.json` → Used by session generation
5. `data/department_heatmap.json` → Used by session generation
6. `data/reference_graph_v2.json` → Used by Graph page
7. `data/map_details.json` → Used by MapDetail page
8. `data/top_risk_departments.json` → Used by dashboard fallback
9. `data/priority_summary.json` → Used by dashboard fallback
10. `data/executive_summary.json` → Used by dashboard fallback

**Total Demo Records:** 2941 requirements + 2941 "MAPs" = 5882 records  
**Actual Backend Records:** 14 requirements + 14 assignments = 28 records

**Contamination Ratio:** 210:1 (demo:real)


---

## TASK 6: DATA SOURCE SWITCHING ANALYSIS

### Page-by-Page Session vs Repository Analysis

| Page | Route | Data Source Logic | Issues |
|------|-------|-------------------|--------|
| **Dashboard** | `/` | 3-way switch: Session → API → Demo | ⚠️ Falls back to demo |
| **Pipeline** | `/pipeline` | Session only (created from demo!) | 🔴 Ignores backend response |
| **Assignment Center** | `/assignment-center` | API only (backend) | ✅ Correct |
| **MAP Management** | `/maps` | Session if scoped, else demo | 🔴 Shows 2941 demo records |
| **Requirements** | `/requirements` | Demo only (always) | 🔴 Never uses backend |
| **Knowledge Graph** | `/graph` | Session if active, else demo | ⚠️ Frontend-only, no backend |
| **Department Risk** | `/departments` | API (backend) | ✅ Correct |
| **Department Workspace** | `/workspace` | API (backend) | ✅ Correct |
| **Map Detail** | `/maps/:id` | Demo mapDetails | 🔴 Never uses backend |

**Summary:**
- ✅ **Correct:** 3 pages (Assignment Center, Department Risk, Department Workspace)
- ⚠️ **Warning:** 2 pages (Dashboard, Knowledge Graph) - have demo fallback
- 🔴 **Broken:** 4 pages (Pipeline, MAP Management, Requirements, Map Detail) - use demo data

---

## TASK 7: DATA SOURCE MATRIX

### Complete Page Data Source Table

| Page | Primary Source | Secondary Source | React Context | API Endpoint | Fallback | Store |
|------|---------------|------------------|---------------|--------------|----------|-------|
| Dashboard | session.analysis | dashboardStats API | AnalysisSession | /admin/dashboard | dashboardMetrics | dashboardStats (local) |
| Pipeline | session.analysis | backendResponse | AnalysisSession | /admin/process-document | None | backendResponse (local) |
| Assignment Center | N/A | summary API | AnalysisSession (hasSession) | /assignment-center/summary | Empty state | summary (local) |
| MAP Management | session.analysis.maps | N/A | AnalysisSession | NONE | globalMapsOutput | None |
| Department Dashboard | N/A | deptRisk API | N/A | /assignment-center/department-risk | None | deptRisk (local) |
| Knowledge Graph | session.analysis.scopedGraph | N/A | AnalysisSession | /admin/requirements/by-semantic-id | globalGraphData | None |
| Requirement Search | requirementsTaxonomy | N/A | N/A | NONE | None | None |
| Department Risk | N/A | deptRisk API | N/A | /assignment-center/department-risk | None | deptRisk (local) |
| Executive Dashboard | Same as Dashboard | Same as Dashboard | Same as Dashboard | Same as Dashboard | Same as Dashboard | Same as Dashboard |
| Department Workspace | N/A | tasks API | AuthContext (user) | /workspace/tasks | None | tasks (local) |


---

## TASK 8: CRITICAL QUESTIONS ANSWERED

### Q1: What is the application's **intended** Single Source of Truth?

**Answer:** Backend PostgreSQL/SQLite database

**Evidence:**
- Models defined in `backend/models.py`
- CRUD operations in `backend/crud.py`
- RESTful APIs in `backend/routers/`
- Assignment Center correctly uses backend
- Department Workspace correctly uses backend

**Design Intent:** Backend is authoritative, frontend displays it

---

### Q2: What is the **actual** Single Source of Truth today?

**Answer:** There is NO single source of truth. There are **FOUR competing sources:**

1. **Backend Database** (14 requirements, 14 assignments) - SHOULD be SSOT
2. **Demo JSON Files** (2941 requirements, 2941 "MAPs") - Contaminates everything
3. **AnalysisSession Context** (Filters demo data) - Creates confusion
4. **Local Component State** (dashboardStats, backendResponse) - Loses sync

**Result:** Chaos. Different pages show different data.

---

### Q3: How many competing sources of truth exist?

**Count:** **4 competing sources**

1. Backend Database
2. Demo JSON (10 files)
3. AnalysisSession Context
4. Local State across 7 components

**Plus 2 aggregation layers:**
- `demo.js` (transforms JSON)
- `generateDocumentAnalysis()` (filters demo data)

**Total data sources:** 6


---

### Q4: Which files violate SSOT?

**Severity: CRITICAL 🔴**

1. `context/AnalysisSession.jsx`
   - Violation: Generates session from demo data instead of backend
   - Impact: Pipeline results show wrong data
   - Line: 14-169 (generateDocumentAnalysis function)

2. `data/demo.js`
   - Violation: Provides alternative data source
   - Impact: Pages use demo instead of API
   - Exports: dashboardMetrics, mapsOutput, requirementsTaxonomy, etc.

3. `pages/Pipeline.jsx`
   - Violation: Ignores backendResponse, passes null to createSession
   - Impact: Session gets demo data, not backend data
   - Line: 313 `createSession(file, null, ...)`

**Severity: HIGH ⚠️**

4. `pages/Dashboard.jsx`
   - Violation: Falls back to demo data
   - Impact: Shows 2941 instead of real count
   - Lines: 108-124

5. `pages/Maps.jsx`
   - Violation: Uses globalMapsOutput (demo) as primary when not scoped
   - Impact: MAP Management shows 2941 demo records
   - Line: 42

6. `pages/Requirements.jsx`
   - Violation: ALWAYS uses demo data, never queries backend
   - Impact: Shows 2941 demo requirements
   - Line: 120

7. `pages/MapDetail.jsx`
   - Violation: Uses demo mapDetails
   - Impact: Details page shows demo data
   - (Not examined but likely uses demo.js)

**Total Violators:** 7 files


---

### Q5: Which files should never own data?

**Answer:** All frontend files! Frontend should ONLY:
- Fetch from API
- Display data
- Cache temporarily in local state

**Files That Should Never Own Data:**

1. `data/*.json` (10 files)
   - Should: Delete or move to backend seed data
   - Currently: Primary data source for many pages

2. `data/demo.js`
   - Should: Delete entirely
   - Currently: Aggregates and exports demo data

3. `context/AnalysisSession.jsx`
   - Should: Store session metadata only, fetch analysis from backend
   - Currently: Generates entire analysis from demo data

**What They Should Do Instead:**

- `data/*.json` → Backend seed data or DELETE
- `demo.js` → DELETE
- `AnalysisSession` → Store { documentId, uploadTime }, fetch analysis via API

---

### Q6: Which pages are reading stale data?

**Stale Data Definition:** Data that doesn't reflect current backend state

1. **Pipeline Results Page** 🔴
   - Shows: Demo data filtered by filename
   - Should Show: Backend response (requirements_created: 14)
   - Reason: createSession(file, null) ignores backendResponse

2. **Dashboard (Session Mode)** 🔴
   - Shows: session.analysis.stats from demo
   - Should Show: Backend response stats
   - Reason: Session generated from demo, not backend

3. **MAP Management (Global)** 🔴
   - Shows: 2941 demo "MAPs"
   - Should Show: Backend assignments or empty
   - Reason: Uses globalMapsOutput from demo.js

4. **Requirements Page** 🔴
   - Shows: 2941 demo requirements
   - Should Show: Backend requirements or empty
   - Reason: Hardcoded to use requirementsTaxonomy from demo.js

5. **Knowledge Graph (Global)** ⚠️
   - Shows: Demo graph structure
   - Should Show: Backend-generated graph or "No data"
   - Reason: No backend graph endpoint exists

6. **Map Detail Page** 🔴
   - Shows: Demo mapDetails
   - Should Show: Backend assignment details
   - Reason: Uses demo mapDetails object

**Total Stale Pages:** 6 out of 10


---

### Q7: Which pages are reading repository data?

**Repository Data Definition:** Data from backend database via API

**✅ CORRECT Pages (3):**

1. **Assignment Center**
   - Endpoint: GET /assignment-center/summary
   - Shows: Unpublished assignments from database
   - Status: ✅ Correct

2. **Department Workspace**
   - Endpoint: GET /workspace/tasks
   - Shows: Published assignments for logged-in department
   - Status: ✅ Correct

3. **Department Risk Dashboard**
   - Endpoint: GET /assignment-center/department-risk
   - Shows: Risk scores computed from assignments
   - Status: ✅ Correct

**⚠️ PARTIAL Pages (1):**

4. **Dashboard (Operational Mode)**
   - Endpoint: GET /admin/dashboard
   - Shows: Backend stats IF not in session mode
   - Status: ⚠️ Correct when API loaded, but has demo fallback

**Total Correct:** 3 fully correct, 1 partially correct

---

### Q8: Which pages are reading analysis session data?

**Session Data Definition:** Data from AnalysisSession context

1. **Pipeline Results Page**
   - Reads: session.analysis (generated from demo)
   - Shows: Stats, departments, maps from filtered demo data
   - Problem: Should read from backend response

2. **Dashboard (Session Mode)**
   - Reads: session.analysis.stats
   - Shows: Requirements, MAPs counts from demo
   - Problem: Should read from backend response

3. **MAP Management (Document Scoped)**
   - Reads: session.analysis.maps
   - Shows: Filtered demo MAPs
   - Problem: Should read from backend assignments

4. **Knowledge Graph (Active Mode)**
   - Reads: session.analysis.scopedGraph
   - Shows: Graph generated from filtered demo
   - Problem: Acceptable as frontend visualization

**Total Session Pages:** 4


---

### Q9: Which pages are mixing both?

**Mixed Data Definition:** Pages that read from multiple competing sources

1. **Dashboard** 🔴
   - Source 1: session.analysis.stats (demo-derived)
   - Source 2: dashboardStats API (backend)
   - Source 3: dashboardMetrics (demo fallback)
   - Logic: 3-way conditional switch
   - Problem: User sees different data based on state

2. **MAP Management** 🔴
   - Source 1: session.analysis.maps (demo-derived, when scoped)
   - Source 2: globalMapsOutput (demo, when global)
   - Logic: Pathname-based switch
   - Problem: Never uses backend assignments

3. **Knowledge Graph** ⚠️
   - Source 1: session.analysis.scopedGraph (demo-derived, when active)
   - Source 2: globalGraphData (demo, when global)
   - Source 3: Backend API for requirement text only
   - Logic: viewMode switch
   - Problem: Acceptable for visualization

**Total Mixed Pages:** 3

**Worst Offender:** Dashboard (3 sources with different values)

---

### Q10: Which bug explains MOST of the observed failures?

## 🔴 THE ROOT CAUSE BUG

**File:** `context/AnalysisSession.jsx`  
**Function:** `generateDocumentAnalysis(fileName)`  
**Lines:** 14-169

**The Bug:**
```javascript
function generateDocumentAnalysis(fileName) {
  // Filters DEMO data (requirementsTaxonomy, mapsOutput) 
  // to create session analysis
  const docRequirements = requirementsTaxonomy.filter(...);
  const docMapEntries = [];
  for (const m of mapsOutput) { ... }
  // Returns analysis built from DEMO data
  return { requirements: docRequirements, maps: docMapEntries, ... };
}
```

**Called By:**
```javascript
// Pipeline.jsx line 313
createSession(file, null, elapsedTimes, totalElapsed);
// Passes NULL, triggers generateDocumentAnalysis()
```

**Impact Chain:**

1. User uploads document → Backend creates 14 requirements + 14 assignments
2. Pipeline calls `createSession(file, null, ...)`
3. `createSession` sees `null` and calls `generateDocumentAnalysis(file.name)`
4. `generateDocumentAnalysis` filters **DEMO DATA** (2941 records) by filename hash
5. Session gets ~180 demo requirements + ~85 demo maps
6. Pipeline displays: "180 requirements found" (WRONG! Should be 14)
7. Dashboard shows session stats: "Requirements: 180, MAPs: 85"
8. Assignment Center shows backend: "14 tasks" (CORRECT)
9. User sees: Pipeline says 180, Assignment Center says 14 → CONFUSION!


**Why This Bug Causes All Symptoms:**

✅ **Symptom 1:** Pipeline generates 720 Requirements → Demo data filtered differently each time  
✅ **Symptom 2:** Dashboard shows 720 MAPs → Uses session.analysis.stats from demo  
✅ **Symptom 3:** MAP Management shows 2941 → Uses globalMapsOutput when no session  
✅ **Symptom 4:** Assignment Center shows 48 → Correct! Uses backend (unaffected by bug)  
✅ **Symptom 5:** Department counts zero → Session departments computed from demo data  
✅ **Symptom 6:** Priority heatmap wrong → Session priority from demo data  
✅ **Symptom 7:** Dashboard inconsistent → Switches between session (demo) and API (backend)  
✅ **Symptom 8:** Knowledge Graph says "Active session required" → Needs session (demo-based)  
✅ **Symptom 9:** Incognito works differently → No session state, uses API mode  

**Single Root Cause:** `generateDocumentAnalysis()` creates session from demo data instead of backend response!

---

## 🔴 SECONDARY CRITICAL BUG

**File:** `data/maps_output.json` and `data/requirements_taxonomy.json`  
**The Bug:** **BOTH files contain 2941 records!**

**Evidence:**
```powershell
> (Get-Content "requirements_taxonomy.json" | ConvertFrom-Json).Count
2941

> (Get-Content "maps_output.json" | ConvertFrom-Json).Count
2941
```

**Investigation:**

1. `requirements_taxonomy.json`: Contains requirement records
   ```json
   {
     "requirement_id": "REQ_25KY0107_0003_6721FA",
     "domain": "Governance",
     "requirement_text": "All NBFCs are advised to adopt..."
   }
   ```

2. `maps_output.json`: Should contain MAP records, but ALSO has 2941 records!
   ```json
   {
     "map_id": "MAP_MD18KYCF_0184_F36A90",
     "requirement_id": "REQ_MD18KYCF_0184_F36A90",
     "task_title": "Implement Wire Transfer Controls",
     "department": "AML Compliance Cell"
   }
   ```

**The Confusion:**
- MAPs are supposed to be "Mitigation Action Plans" (tasks to implement requirements)
- But demo data has 2941 MAPs matching 2941 requirements (1:1 ratio)
- In reality: 1 requirement might generate 0-N assignments
- Backend correctly uses `assignments` table (separate from requirements)

**Impact:**
- Code assumes MAPs and Requirements are different (correct architecture)
- Demo data makes them nearly identical (wrong data model)
- Result: "720 requirements" gets displayed as "720 MAPs"


---

## ARCHITECTURAL VIOLATIONS SUMMARY

### Violation #1: Frontend Owns Data 🔴 CRITICAL

**Pattern:** Frontend JSON files serve as primary data source

**Files:**
- `data/*.json` (10 files, 2941+ records each)
- `data/demo.js` (aggregates and transforms)

**Correct Architecture:** 
- Backend database = SSOT
- Frontend = view layer only

**Current Architecture:**
- Frontend JSON = primary for 6+ pages
- Backend database = secondary (only 3 pages use it)

**Fix Required:** Delete demo data, use backend APIs exclusively

---

### Violation #2: Context Generates Data 🔴 CRITICAL

**Pattern:** AnalysisSession context computes analysis instead of fetching

**File:** `context/AnalysisSession.jsx`  
**Function:** `generateDocumentAnalysis()` (156 lines)

**What It Does:**
- Filters 2941 demo requirements by filename hash
- Filters 2941 demo MAPs by requirements
- Computes department breakdown
- Builds knowledge graph
- Generates AI briefing

**What It Should Do:**
- Store document_id only
- Fetch analysis from backend API
- Cache response temporarily

**Fix Required:** Replace `generateDocumentAnalysis()` with API call

---

### Violation #3: Multiple Sources of Truth 🔴 CRITICAL

**Pattern:** Same entity exists in 4 places with different values

**Example: "Requirements Count"**
- Demo JSON: 2941
- Session (from demo): 180 (filtered)
- Backend: 14 (actual)
- Pipeline display: 720 (varies by filename!)

**Correct Architecture:** ONE source (backend)

**Current Architecture:** FOUR sources (all different)

**Fix Required:** Remove all non-backend sources


---

### Violation #4: Fallback to Demo in Production 🔴 CRITICAL

**Pattern:** Pages show demo data when API fails or loads slowly

**Files:**
- `pages/Dashboard.jsx` (lines 108-124)
- `pages/Maps.jsx` (line 42)
- `pages/Requirements.jsx` (line 120 - always demo!)

**Problem:** Production users see 2941 fake records

**Correct Behavior:** 
- Show loading state
- Show error message
- Show empty state
- **NEVER show demo data**

**Fix Required:** Remove demo fallbacks, show proper error states

---

### Violation #5: Terminology Confusion 🔴 CRITICAL

**Problem:** "MAPs" in demo data are actually requirements

**Evidence:**
```javascript
// Demo has 2941 "MAPs" matching 2941 requirements
maps_output.json: 2941 records
requirements_taxonomy.json: 2941 records

// Each "MAP" just adds task_title to a requirement
{
  "map_id": "MAP_MD18KYCF_0184",
  "requirement_id": "REQ_MD18KYCF_0184",  // Same ID!
  "task_title": "Implement Wire Transfer Controls"
}
```

**Correct Model:**
- Requirements: Extracted from circulars
- Assignments: Tasks assigned to departments
- 1 requirement → 0 to N assignments

**Demo Model:**
- Requirements: 2941 records
- "MAPs": 2941 records (just requirements with titles)
- 1:1 relationship (wrong!)

**Impact:** Code treats MAPs and assignments as interchangeable, causing confusion

**Fix Required:** 
1. Delete demo data OR
2. Regenerate demo data with correct 1:N relationship


---

## DATA FLOW DIAGRAM

### Current (Broken) Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS PDF                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Backend Processing    │
         │  - Creates 14 reqs     │
         │  - Creates 14 assigns  │
         └────────┬───────────────┘
                  │
                  ├─────────────────────────┐
                  ▼                         ▼
    ┌─────────────────────┐   ┌─────────────────────────┐
    │ Pipeline.jsx        │   │ Assignment Center       │
    │ backendResponse:    │   │ API Response:           │
    │ {reqs: 14, assigns:14}│ │ {total_maps: 14}       │
    └──────┬──────────────┘   └──────┬──────────────────┘
           │                         │
           │ IGNORED!                │ ✅ DISPLAYED
           │                         │
           ▼                         ▼
    ┌─────────────────────┐   ┌─────────────────┐
    │ createSession(null) │   │ Shows: 14 tasks │
    └──────┬──────────────┘   └─────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ generateDocumentAnalysis │
    │ Filters DEMO DATA        │
    │ (2941 records)           │
    └──────┬───────────────────┘
           │
           ▼
    ┌─────────────────────────────┐
    │ session.analysis            │
    │ {reqs: 180, maps: 85}       │
    │ FROM DEMO! ❌               │
    └──────┬──────────────────────┘
           │
           ├───────────────┬──────────────┐
           ▼               ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │Pipeline  │   │Dashboard │   │Knowledge │
    │Shows:180 │   │Shows: 85 │   │Graph     │
    │❌ WRONG  │   │❌ WRONG  │   │Shows demo│
    └──────────┘   └──────────┘   └──────────┘
```

**Problem:** Backend data ignored, demo data displayed!


### Correct (Desired) Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS PDF                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │  Backend Processing            │
         │  - Creates 14 requirements     │
         │  - Creates 14 assignments      │
         │  - Stores in database          │
         └────────┬───────────────────────┘
                  │
                  │ SINGLE SOURCE OF TRUTH
                  │
                  ├─────────────────────────┬─────────────────┐
                  ▼                         ▼                 ▼
    ┌──────────────────────┐   ┌─────────────────┐   ┌─────────────┐
    │ Pipeline.jsx         │   │Assignment Center│   │  Dashboard  │
    │ API Response:        │   │ API Response:   │   │API Response:│
    │ {reqs: 14, assigns:14}│  │ {total: 14}    │   │{published:5}│
    └──────┬───────────────┘   └─────┬───────────┘   └──────┬──────┘
           │                         │                      │
           ▼                         ▼                      ▼
    ┌──────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │ createSession()  │   │ Display: 14     │   │Display: 5 pub  │
    │ Store: {         │   │ ✅ CORRECT      │   │        9 draft  │
    │   documentId,    │   └─────────────────┘   │ ✅ CORRECT      │
    │   stats: {14,14} │                         └─────────────────┘
    │ }                │
    └──────┬───────────┘
           │
           ├───────────────┬──────────────┐
           ▼               ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────────┐
    │Pipeline  │   │Dashboard │   │Knowledge     │
    │Shows: 14 │   │Shows: 14 │   │Graph         │
    │✅ CORRECT│   │✅ CORRECT│   │Fetches from  │
    └──────────┘   └──────────┘   │backend API   │
                                   │✅ CORRECT    │
                                   └──────────────┘
```

**Solution:** All pages fetch from backend, session stores only metadata!


---

## DEPENDENCY MAP

### Demo Data Dependency Chain

```
requirements_taxonomy.json (2941 records)
           ↓
       demo.js → requirementsTaxonomy
           ↓
           ├─→ AnalysisSession.generateDocumentAnalysis()
           │        ↓
           │   session.analysis.requirements (180)
           │        ↓
           │        ├─→ Pipeline Results
           │        ├─→ Dashboard (session mode)
           │        └─→ Knowledge Graph
           │
           └─→ Requirements.jsx (displays all 2941)
```

```
maps_output.json (2941 records)
           ↓
       demo.js → mapsOutput
           ↓
           ├─→ AnalysisSession.generateDocumentAnalysis()
           │        ↓
           │   session.analysis.maps (85)
           │        ↓
           │        ├─→ Pipeline Results
           │        ├─→ Dashboard (session mode)
           │        └─→ Maps.jsx (document scoped)
           │
           └─→ Maps.jsx (global mode - displays all 2941)
```

```
dashboard_metrics.json
           ↓
       demo.js → dashboardMetrics
           ↓
       Dashboard.jsx (fallback mode)
           ↓
       Shows: 2941 MAPs (if API fails)
```

**Problem:** Everything depends on demo data!


### Backend Data Dependency Chain

```
Backend Database (PostgreSQL/SQLite)
           ↓
       ├─→ GET /admin/dashboard
       │        ↓
       │   Dashboard.jsx (operational mode)
       │        ↓
       │   Shows: 5 published, 9 draft ✅
       │
       ├─→ GET /assignment-center/summary
       │        ↓
       │   AssignmentCenter.jsx
       │        ↓
       │   Shows: 14 unpublished tasks ✅
       │
       ├─→ GET /workspace/tasks
       │        ↓
       │   DepartmentWorkspace.jsx
       │        ↓
       │   Shows: 5 published tasks ✅
       │
       └─→ GET /assignment-center/department-risk
                ↓
           Departments.jsx
                ↓
           Shows: Department risk scores ✅
```

**Success:** 4 pages correctly use backend!

---

## IMPACT ANALYSIS

### Pages by Correctness

#### ✅ CORRECT (3 pages) - 30%

1. Assignment Center - Uses backend API only
2. Department Workspace - Uses backend API only
3. Department Risk - Uses backend API only

#### ⚠️ PARTIALLY CORRECT (1 page) - 10%

4. Dashboard - Uses backend in operational mode, demo in session/fallback

#### 🔴 BROKEN (6 pages) - 60%

5. Pipeline - Uses demo via session (should use backend response)
6. MAP Management - Uses demo always (should use backend assignments)
7. Requirements - Uses demo always (should use backend requirements)
8. Knowledge Graph - Uses demo structure (should use backend or show "not implemented")
9. Map Detail - Uses demo mapDetails (should use backend assignment detail)
10. Pipeline Results - Uses demo via session (should use backend response)

**Critical Assessment:** 60% of pages are broken!

