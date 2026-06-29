# UI Display to Code Source Mapping

Quick reference guide showing exactly where each displayed number comes from.

---

## Dashboard Page

### "Published MAPs" / "Published Assignments"
- **Display:** KPI card on Dashboard
- **Frontend:** `Dashboard.jsx` Line ~88
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Line 308
- **Query:** `COUNT(assignments WHERE is_published=true)`
- **Actual Entity:** Published assignments from database

### "Draft MAPs" / "Unpublished Assignments"  
- **Display:** KPI card on Dashboard
- **Frontend:** `Dashboard.jsx` Line ~94
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Line 309
- **Query:** `total_assignments - published_maps`
- **Actual Entity:** Unpublished assignments from database

### "Total Requirements" (2941)
- **Display:** Dashboard metrics (if shown)
- **Frontend:** `Dashboard.jsx`
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Lines 270-278
- **Source:** `requirements_taxonomy.json` (primary) or database (fallback)
- **Actual Entity:** Demo JSON count (2941 items)

### "Pending Tasks"
- **Display:** KPI card on Dashboard
- **Frontend:** `Dashboard.jsx`
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Lines 289-293
- **Query:** `COUNT(assignments WHERE status='pending' AND is_published=true)`
- **Actual Entity:** Published pending assignments

### "Completed Tasks"
- **Display:** KPI card on Dashboard
- **Frontend:** `Dashboard.jsx`
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Lines 301-305
- **Query:** `COUNT(assignments WHERE status='completed' AND is_published=true)`
- **Actual Entity:** Published completed assignments

### "Critical Priority" / "Critical MAPs"
- **Display:** KPI card on Dashboard
- **Frontend:** `Dashboard.jsx`
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Lines 314-326
- **Query:** Priority distribution calculation from assignments
- **Actual Entity:** Count of assignments with Critical priority

### "Departments Impacted"
- **Display:** KPI card on Dashboard
- **Frontend:** `Dashboard.jsx`
- **API:** `GET /api/admin/dashboard`
- **Backend:** `crud.py` Line 312
- **Query:** `COUNT DISTINCT(department_id WHERE is_published=true)`
- **Actual Entity:** Unique departments with published assignments


---

## Pipeline Results Page

### "205 Requirements Extracted" (varies by file)
- **Display:** Analysis results hero banner
- **Frontend:** `Pipeline.jsx` Line 67
- **Data Source:** `AnalysisSession.jsx` Lines 21-24
- **Source:** Filtered `requirements_taxonomy.json`
- **Calculation:** `docRequirements.length` (filtered by selected source documents)
- **Actual Entity:** Demo JSON filtered by filename hash

### "205 Generated MAPs" (varies by file)
- **Display:** Analysis results hero banner
- **Frontend:** `Pipeline.jsx` Line 68
- **Data Source:** `AnalysisSession.jsx` Lines 26-48
- **Source:** Filtered `maps_output.json`
- **Calculation:** `docMapEntries.length` (linked to filtered requirements)
- **Actual Entity:** Demo JSON filtered by requirement linkage

### "9 Departments Impacted" (varies)
- **Display:** Analysis results hero banner
- **Frontend:** `Pipeline.jsx` Line 68
- **Data Source:** `AnalysisSession.jsx` Lines 50-70
- **Source:** Computed from filtered demo MAPs
- **Calculation:** `docDepartments.length`
- **Actual Entity:** Unique departments from filtered demo MAPs

### "1 Critical MAP" (varies)
- **Display:** Analysis results hero banner
- **Frontend:** `Pipeline.jsx` Line 68
- **Data Source:** `AnalysisSession.jsx`
- **Source:** Filtered `maps_output.json`
- **Calculation:** `docMapEntries.filter(m => m.priority === "Critical").length`
- **Actual Entity:** Critical priority count from filtered demo MAPs

### Backend Reality Check:
- **Actual API Call:** `POST /api/admin/process-document/{id}`
- **Backend:** `admin_router.py` Lines 76-187
- **What's Created:** 14 requirements + 14 assignments in database
- **Disconnect:** Frontend shows demo data (~205), backend creates 14 records

---

## Assignment Center Page

### "70 Total MAPs" (example number, varies)
- **Display:** Summary card "Total MAPs Across X Departments"
- **Frontend:** `AssignmentCenter.jsx` Line ~127
- **API:** `GET /api/assignment-center/summary`
- **Backend:** `assignment_center_router.py` Lines 28-35
- **Query:** `crud.get_unpublished_assignment_summary(db)`
- **Source:** `crud.py` Lines 388-422
- **Calculation:** `SUM(dept["task_count"])` WHERE `is_published=false`
- **Actual Entity:** Unpublished assignments from database

### Department Task Counts
- **Display:** Department cards "{N} Tasks"
- **Frontend:** `AssignmentCenter.jsx`
- **API:** `GET /api/assignment-center/summary`
- **Backend:** `crud.py` Lines 388-422
- **Query:** `COUNT(assignments WHERE department_id=X AND is_published=false)`
- **Actual Entity:** Unpublished assignments per department


---

## MAP Management Page

### "2941 Mitigation Action Plans"
- **Display:** Page subtitle "Showing X of 2941"
- **Frontend:** `Maps.jsx` Lines 9, 40
- **Data Source:** `demo.js` import `mapsOutput`
- **Source File:** `maps_output.json`
- **Query:** None (direct JSON import)
- **Calculation:** `globalMapsOutput.length`
- **Actual Entity:** Demo JSON MAPs (2941 items)

### MAP List / Details
- **Display:** Full table of MAPs
- **Frontend:** `Maps.jsx` Line 40
- **Data Source:** `globalMapsOutput` from demo.js
- **Source File:** `maps_output.json`
- **Query:** None (client-side filter/sort)
- **Actual Entity:** Demo JSON MAPs, NOT database assignments

### When Viewing "Document MAPs" (scoped)
- **Display:** Filtered MAP list during analysis session
- **Frontend:** `Maps.jsx` Lines 38-42
- **Data Source:** `session.analysis.maps`
- **Source:** `AnalysisSession.jsx` filtered demo data
- **Calculation:** Filtered `maps_output.json` by document
- **Actual Entity:** Session-filtered demo MAPs

---

## Requirements Search Page

### "2941 Requirements"
- **Display:** Page subtitle
- **Frontend:** `Requirements.jsx` Line 11
- **Data Source:** `import { requirementsTaxonomy } from "../data/demo"`
- **Source File:** `requirements_taxonomy.json`
- **Query:** None (direct JSON import)
- **Calculation:** `requirementsTaxonomy.length`
- **Actual Entity:** Demo JSON requirements (2941 items)

### Search Results
- **Display:** Filtered requirement list
- **Frontend:** `Requirements.jsx`
- **Data Source:** `requirementsTaxonomy`
- **Source File:** `requirements_taxonomy.json`
- **Query:** None (client-side `.filter()`)
- **Actual Entity:** Demo JSON requirements, NOT database

### Consequence:
- **New requirements created in database:** NOT searchable in UI
- **Only demo JSON requirements:** Appear in search

---

## Department Dashboard (Admin View)

### Assignment Counts per Department
- **Display:** Table with "Assigned | Completed | Remaining"
- **Frontend:** `Dashboard.jsx` (table section)
- **API:** `GET /api/assignment-center/admin-summary`
- **Backend:** `crud.py` Lines 468-493
- **Query:** 
  ```python
  assignments = db.query(Assignment).filter(
      Assignment.department_id == dept.id,
      Assignment.is_published == True
  ).all()
  ```
- **Calculation:**
  - Assigned: `len(assignments)`
  - Completed: `sum(1 for a in assignments if a.status == 'completed')`
  - Remaining: `assigned - completed`
- **Actual Entity:** Published assignments from database

### Why Shows Zero After Pipeline:
- Pipeline creates **unpublished** assignments
- Dashboard queries **published** assignments only
- Must manually publish via Assignment Center first


---

## Knowledge Graph Page

### Graph Visualization
- **Display:** Interactive node-edge graph
- **Frontend:** `Graph.jsx` Lines 85-90
- **Data Source:** 
  ```javascript
  const graphData = viewMode === "active" && hasSession 
    ? session.analysis.scopedGraph    // Session data
    : globalGraphData;                 // Global demo data
  ```
- **Source:** `AnalysisSession.jsx` Lines 72-124 (generates from demo JSON)
- **Base Files:** `requirements_taxonomy.json`, `maps_output.json`, `map_details.json`
- **Query:** None (generated in frontend)
- **Actual Entity:** Demo data, no database persistence

### Node Details (Full Text)
- **Display:** Modal showing requirement/MAP full text
- **Frontend:** `Graph.jsx` Lines 245-270
- **Data Source (Active Session):** `session.analysis.requirements`
- **Data Source (Global):** `requirementsTaxonomyRaw`
- **Fallback Attempt:** API call (currently fails due to ID mismatch)
- **Source:** Demo JSON, NOT database
- **Issue:** Graph uses semantic IDs, API needs integer IDs

### Graph Statistics
- **Display:** Node/edge counts
- **Frontend:** `Graph.jsx`
- **Data Source:** Computed from `graphData.nodes` and `graphData.edges`
- **Source:** Demo JSON-derived graph
- **Actual Entity:** Counts from demo data graph structure

---

## Department Workspace (Department User View)

### "My Tasks"
- **Display:** Task list for department user
- **Frontend:** `DepartmentWorkspace.jsx`
- **API:** `GET /api/departments/workspace/my-tasks`
- **Backend:** `department_workspace_router.py`
- **Query:** 
  ```python
  assignments = db.query(Assignment).filter(
      Assignment.department_id == current_user.department_id,
      Assignment.is_published == True
  ).all()
  ```
- **Actual Entity:** Published assignments for user's department

### Task Counts
- **Display:** "X Completed, Y Pending"
- **Frontend:** `DepartmentWorkspace.jsx` (client-side calculation)
- **Data Source:** Tasks array from API
- **Calculation:** 
  ```javascript
  const completedCount = tasks.filter(t => t.status === 'completed').length;
  const pendingCount = tasks.length - completedCount;
  ```
- **Actual Entity:** Derived from published assignments

---

## Risk Analysis Page

### Department Risk Scores
- **Display:** Risk cards per department
- **Frontend:** `Departments.jsx`
- **API:** `GET /api/assignment-center/department-risk`
- **Backend:** `crud.py` Lines 497-555
- **Query:** All assignments per department (published + unpublished)
- **Calculation:**
  ```python
  PRIORITY_WEIGHTS = {"Critical": 40, "High": 20, "Medium": 5, "Low": 1}
  raw_score = sum(priority_counts[p] * PRIORITY_WEIGHTS[p])
  risk_score = (raw_score / max_raw_score) * 100  # Normalized 0-100
  ```
- **Actual Entity:** Computed from all database assignments


---

## Summary: Data Source Matrix

| UI Page | Metric | Database | Demo JSON | Session | Actual Entity |
|---------|--------|----------|-----------|---------|---------------|
| **Dashboard** | Published MAPs | ✅ | ❌ | ❌ | Assignments |
| **Dashboard** | Total Requirements | Fallback | ✅ Primary | ❌ | JSON (2941) |
| **Pipeline** | Requirements Extracted | ❌ | ✅ | ✅ | Filtered JSON |
| **Pipeline** | Generated MAPs | ❌ | ✅ | ✅ | Filtered JSON |
| **Pipeline** | Departments Impacted | ❌ | ✅ | ✅ | Computed from JSON |
| **Assignment Center** | Total MAPs | ✅ | ❌ | ❌ | Unpublished assignments |
| **MAP Management** | 2941 MAPs | ❌ | ✅ | ❌ | JSON MAPs |
| **Requirements Search** | 2941 Requirements | ❌ | ✅ | ❌ | JSON requirements |
| **Knowledge Graph** | Nodes/Edges | ❌ | ✅ | ✅ | Generated from JSON |
| **Dept Dashboard** | Assignment Counts | ✅ | ❌ | ❌ | Published assignments |
| **Dept Workspace** | My Tasks | ✅ | ❌ | ❌ | Published assignments |
| **Risk Analysis** | Risk Scores | ✅ | ❌ | ❌ | All assignments |

---

## Key Insights from Mapping

### Pages Using Database (Operational Workflow):
- ✅ Dashboard (KPIs except requirements count)
- ✅ Assignment Center (unpublished assignments)
- ✅ Department Dashboard (published assignments)
- ✅ Department Workspace (user tasks)
- ✅ Risk Analysis (all assignments)

### Pages Using Demo JSON (Reference/Visualization):
- ✅ Pipeline Results (analysis visualization)
- ✅ MAP Management (reference library)
- ✅ Requirements Search (knowledge base)
- ✅ Knowledge Graph (relationship visualization)

### Hybrid Pages (Mixed Sources):
- ⚠️ Dashboard (assignments from DB, requirements from JSON)

---

## Workflow Understanding

### Operational Flow (Database):
```
1. Upload Document
2. Process → Create 14 assignments (unpublished)
3. Assignment Center → Review 14 assignments
4. Publish → Assignments become visible
5. Department Workspace → Users see published tasks
6. Update Status → Track completion
7. Dashboard → Show metrics
```

### Reference Flow (Demo JSON):
```
1. Browse MAP Management → See 2941 reference MAPs
2. Search Requirements → Search 2941 taxonomy
3. View Knowledge Graph → Visualize relationships
4. Pipeline Analysis → Show demo data visualization
```

### The Disconnect:
- Pipeline creates 14 DB records
- Pipeline shows ~205 demo records
- Users see demo data, not actual pipeline output

---

## Terminology Mapping

| UI Label | Variable Name | Database Table | Actual Meaning |
|----------|---------------|----------------|----------------|
| "Published MAPs" | `published_maps` | `assignments` | Published assignments |
| "Draft MAPs" | `unpublished_maps` | `assignments` | Unpublished assignments |
| "Total MAPs" (Assignment Center) | `total_maps` | `assignments` | Sum of unpublished assignments |
| "2941 MAPs" (MAP Management) | `globalMapsOutput` | N/A | Demo JSON proposals |
| "Generated MAPs" (Pipeline) | `stats.totalMaps` | N/A | Filtered demo JSON |
| "Pending Tasks" | `pending_assignments` | `assignments` | Pending status assignments |
| "Requirements" (Dashboard) | `total_requirements` | `requirements` or JSON | Varies by source |
| "Requirements" (Search) | `requirementsTaxonomy` | N/A | Demo JSON taxonomy |

**Key Observation:** "MAP" label used for multiple different entities depending on context.

