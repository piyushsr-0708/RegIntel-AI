# Domain Model Validation - Evidence-Based Analysis

**Date:** June 28, 2026  
**Purpose:** Validate domain model conclusions with concrete code evidence

---

## Executive Summary

After tracing the complete application lifecycle from document upload through dashboard display, I can confirm:

1. ✅ **"MAP" does NOT exist as a database entity** - Confirmed with evidence
2. ✅ **Requirements exist in dual unsynchronized sources** - Confirmed with evidence
3. ✅ **Knowledge Graph is session-only demo data** - Confirmed with evidence
4. ✅ **Numbers represent different data sources** - Traced with evidence

However, the **INTENDED business workflow vs ACTUAL implementation** requires clarification.

---

## Part 1: Complete Lifecycle Trace

### Document Upload → Dashboard Flow

#### Step 1: Upload Document

**Frontend:** User uploads PDF  
**API Call:** `POST /api/admin/upload`  
**Code:** `backend/routers/admin_router.py` Lines 22-73

```python
# Creates database record ONLY
document = crud.create_document(
    db=db,
    filename=filename,
    original_filename=file.filename,
    file_path=file_path,
    file_size=file_size,
    document_type=document_type,
    uploaded_by=current_user.id
)
```

**Result:** Document record in `documents` table. **No requirements or MAPs created yet.**

---

#### Step 2: Process Document (Backend Pipeline)


**Frontend:** Pipeline.jsx starts visual stages  
**API Call:** `POST /api/admin/process-document/{document_id}`  
**Code:** `backend/routers/admin_router.py` Lines 76-187

```python
# For each sample requirement (14 requirements created)
for idx, req_data in enumerate(sample_requirements):
    # 1. CREATE REQUIREMENT
    requirement = crud.create_requirement(db, schemas.RequirementCreate(
        requirement_id=req_id,
        document_id=document_id,
        text=req_data["text"],
        classification=req_data["classification"],
        domain=req_data["domain"],
        priority=req_data["priority"],
        source_reference=document.original_filename
    ))
    created_count += 1
    
    # 2. CREATE ASSIGNMENT (NOT MAP!)
    # Determine department based on domain
    dept_name = dept_mapping.get(req_data["domain"], "Compliance")
    department = next((d for d in departments if d.name == dept_name), departments[0])
    
    if department:
        # Create unpublished assignment
        assignment = crud.create_assignment(
            db=db,
            requirement_id=requirement.id,
            department_id=department.id,
            assigned_by=current_user.id
        )
        assignment_count += 1
```

**CRITICAL FINDING:**
- ❌ **NO MAP TABLE WRITES**
- ❌ **NO MAP GENERATION LOGIC**
- ✅ Creates `requirements` table records
- ✅ Creates `assignments` table records
- ✅ Assignment = link between requirement + department

**Result:**
```
{
    "status": "success",
    "requirements_created": 14,     // Written to database
    "assignments_created": 14       // Written to database
}
```

**Confirmed:** The backend creates REQUIREMENTS and ASSIGNMENTS, NOT MAPs.

---

#### Step 3: Frontend Analysis Session (Demo Data Generation)

**Code:** `frontend/dashboard/src/context/AnalysisSession.jsx` Lines 11-138

**CRITICAL DISCOVERY:** Session analysis uses **DEMO JSON FILES**, not database:

```javascript
// Line 5-8: Import DEMO DATA
import {
  dashboardMetrics, mapsOutput, departmentHeatmap,
  requirementsTaxonomy, graphData, departmentSummary, mapDetails
} from "../data/demo";

// Lines 15-138: generateDocumentAnalysis()
function generateDocumentAnalysis(fileName) {
  // Filter requirements from DEMO JSON (not database!)
  const docRequirements = requirementsTaxonomy.filter(r => 
    selectedSources.includes(r.source_document)
  );

  // Filter MAPs from DEMO JSON (not database!)
  const docMapEntries = [];
  for (const m of mapsOutput) {  // <-- Demo JSON
    const detail = mapDetails[m.map_id];
    if (detail && docReqIds.has(detail.source_requirement?.req_id)) {
      docMapIds.push(m.map_id);
      docMapEntries.push(m);
    }
  }
  
  return {
    requirements: docRequirements,  // From demo JSON
    maps: docMapEntries,             // From demo JSON
    stats: {
      totalRequirements: docRequirements.length,
      totalMaps: docMapEntries.length,
      ...
    }
  };
}
```

**CONFIRMED:** Analysis session displays DEMO DATA, ignoring database records.


---

#### Step 4: Dashboard Metrics

**API Call:** `GET /api/admin/dashboard`  
**Code:** `backend/crud.py` Lines 268-355

```python
def get_dashboard_summary(db: Session):
    # REQUIREMENT COUNT: Uses demo JSON fallback!
    try:
        json_path = "data/requirements/requirements_taxonomy.json"
        with open(json_path, 'r') as f:
            total_reqs = len(json.load(f))  # <-- DEMO DATA
    except:
        total_reqs = db.query(func.count(models.Requirement.id)).scalar()
    
    # ASSIGNMENT COUNTS: Uses database
    published_maps = db.query(func.count(models.Assignment.id)).filter(
        models.Assignment.is_published == True
    ).scalar() or 0
    
    total_assignments = db.query(func.count(models.Assignment.id)).scalar()
    unpublished_maps = total_assignments - published_maps
    
    return {
        "total_requirements": total_reqs,        # Demo JSON (2941)
        "published_maps": published_maps,        # Database
        "unpublished_assignments": unpublished_maps  # Database
    }
```

**CONFIRMED:** Dashboard mixes demo JSON (requirements) with database (assignments).

---

## Part 2: Number Reconciliation with Evidence

### Count 1: "2941 Requirements" (or "2941 MAPs" in some places)

**Source:** `frontend/dashboard/src/data/requirements_taxonomy.json`

**Evidence:**
```powershell
# Verified with command
$reqsCount = (Get-Content "frontend\dashboard\src\data\requirements_taxonomy.json" | ConvertFrom-Json).Count
# Result: 2941 items
```

**Used By:**
1. **Dashboard** - `total_requirements` (via crud.py fallback)
2. **Requirements Search** - Full list (`Requirements.jsx` Line 11)
3. **MAP Management** - Mislabeled (should say "Requirements")

**Business Meaning:** Static demo requirement taxonomy, NOT production data.


---

### Count 2: "2941 MAPs" in MAP Management

**Source:** SAME FILE: `frontend/dashboard/src/data/maps_output.json`

**Evidence:**
```powershell
$mapsCount = (Get-Content "frontend\dashboard\src\data\maps_output.json" | ConvertFrom-Json).Count
# Result: 2941 items (identical count to requirements)
```

**Code:** `frontend/dashboard/src/pages/Maps.jsx` Line 40
```javascript
const mapsOutput = isDocumentScoped && hasSession 
  ? session.analysis.maps      // Session data (filtered demo)
  : globalMapsOutput;          // Full demo JSON (2941 items)
```

**Business Meaning:** Demo "MAP" proposals, 1:1 mapping with demo requirements.

**CRITICAL:** This is NOT the database `assignments` table!

---

### Count 3: "205 Generated MAPs" in Pipeline

**Source:** Filtered demo data based on filename

**Code:** `AnalysisSession.jsx` Lines 26-48
```javascript
// Filter requirements by selected source documents (deterministic based on filename)
const docRequirements = requirementsTaxonomy.filter(r => 
  selectedSources.includes(r.source_document)
);

// Filter MAPs linked to those requirements
const docMapEntries = [];
for (const m of mapsOutput) {
  const detail = mapDetails[m.map_id];
  if (detail && docReqIds.has(detail.source_requirement?.req_id)) {
    docMapEntries.push(m);
  }
}

stats.totalMaps = docMapEntries.length;  // ~205 (varies by file)
```

**Displayed:** `Pipeline.jsx` Line 68
```javascript
{ label: "Generated MAPs", value: s.totalMaps, ... }
```

**Business Meaning:** Demo visualization of "MAPs" derived from filtered requirements.

**Reality:** Backend created 14 assignments, but frontend shows ~205 from demo JSON.


---

### Count 4: "70 Total MAPs" in Assignment Center (Example)

**Source:** Database `assignments` table (unpublished only)

**Code:** `backend/crud.py` Lines 388-422
```python
def get_unpublished_assignment_summary(db: Session):
    # Get ALL unpublished assignments
    assignments = db.query(models.Assignment).filter(
        models.Assignment.is_published == False
    ).all()
    
    dept_summary = {}
    for assignment in assignments:
        dept_id = assignment.department_id
        if dept_id not in dept_summary:
            dept = db.query(models.Department).filter(
                models.Department.id == dept_id
            ).first()
            dept_summary[dept_id] = {
                "department_id": dept_id,
                "department_name": dept.name if dept else "Unknown",
                "task_count": 0
            }
        dept_summary[dept_id]["task_count"] += 1
    
    return dept_summary
```

**API:** `backend/routers/assignment_center_router.py` Lines 28-35
```python
summary = crud.get_unpublished_assignment_summary(db)
total_maps = sum(dept["task_count"] for dept in summary.values())

return {
    "total_maps": total_maps,    # Counts unpublished assignments
    "departments": list(summary.values())
}
```

**Frontend:** `AssignmentCenter.jsx` displays `summary.total_maps`

**Business Meaning:** Count of unpublished assignments awaiting review/publishing.

**Actual Entity:** `assignments` table WHERE `is_published = false`


---

### Count 5: "205 Requirements Extracted" in Pipeline

**Source:** Filtered demo requirements taxonomy

**Code:** `AnalysisSession.jsx` Lines 21-24
```javascript
const docRequirements = requirementsTaxonomy.filter(r => 
  selectedSources.includes(r.source_document)
);

stats.totalRequirements = docRequirements.length;  // ~205
```

**Displayed:** `Pipeline.jsx` Line 67
```javascript
{ label: "Requirements Extracted", value: s.totalRequirements, ... }
```

**Business Meaning:** Demo visualization of requirements from selected circulars.

**Reality:** Backend actually created 14 requirements in database, but frontend shows ~205 from demo JSON.

---

## Part 3: Page-by-Page Data Source Mapping

### Executive Dashboard

**Page:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**API:** `GET /api/admin/dashboard`  
**Backend:** `crud.py` Lines 268-355

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Total Requirements | Demo JSON fallback | `requirements_taxonomy.json` | `len(json.load(f))` → 2941 |
| Published Assignments | Database | `assignments` | `COUNT WHERE is_published=true` |
| Draft Assignments | Database | `assignments` | `COUNT WHERE is_published=false` |
| Pending Tasks | Database | `assignments` | `COUNT WHERE status='pending' AND is_published=true` |
| Completed Tasks | Database | `assignments` | `COUNT WHERE status='completed' AND is_published=true` |
| Critical Priority | Database | `assignments` JOIN `requirements` | Priority distribution calculation |
| Departments Impacted | Database | `assignments` | `COUNT DISTINCT department_id WHERE is_published=true` |

**Session Cache:** None  
**Demo JSON:** Requirements count only

**Final Entity:** Mix of demo requirements + database assignments


---

### Pipeline Results

**Page:** `frontend/dashboard/src/pages/Pipeline.jsx`  
**API:** None (uses session context only)  
**Backend:** N/A

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Requirements Extracted | Session (demo) | `requirements_taxonomy.json` | Filtered by source docs |
| Generated MAPs | Session (demo) | `maps_output.json` | Filtered by requirements |
| Critical MAPs | Session (demo) | `maps_output.json` | `.filter(m => m.priority === "Critical")` |
| Departments Impacted | Session (demo) | Computed from demo MAPs | Department aggregation |
| Knowledge Graph | Session (demo) | Generated from demo data | Nodes + edges computed |

**Session Cache:** ✅ **Complete dependency**  
**Demo JSON:** ✅ **Primary source**  
**Database Query:** ❌ **None**

**Final Entity:** Demo data visualization, disconnected from actual pipeline results

---

### Assignment Center

**Page:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`  
**API:** `GET /api/assignment-center/summary`  
**Backend:** `crud.py` Lines 388-422

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Total MAPs | Database | `assignments` | `SUM(task_count)` WHERE `is_published=false` |
| Department Task Counts | Database | `assignments` | `COUNT GROUP BY department_id` WHERE `is_published=false` |

**Session Cache:** None  
**Demo JSON:** None  
**Database Query:** ✅ **Primary source**

**Final Entity:** Unpublished assignments from database


---

### MAP Management

**Page:** `frontend/dashboard/src/pages/Maps.jsx`  
**API:** None  
**Backend:** N/A

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Total MAPs | Demo JSON | `maps_output.json` | `globalMapsOutput.length` → 2941 |
| MAP Details | Demo JSON | `map_details.json` | Lookup by map_id |
| Filtered MAPs | Demo JSON | `maps_output.json` | Client-side filter/sort |

**Code:** `Maps.jsx` Lines 38-42
```javascript
const mapsOutput = isDocumentScoped && hasSession 
  ? session.analysis.maps      // Session-filtered demo data
  : globalMapsOutput;          // Full demo data (2941)
```

**Session Cache:** Used for document-scoped view  
**Demo JSON:** ✅ **Primary source**  
**Database Query:** ❌ **None**

**Final Entity:** Demo "MAPs" from JSON, NOT database assignments

---

### Department Dashboard (Admin View)

**Page:** `frontend/dashboard/src/pages/Dashboard.jsx` (table section)  
**API:** `GET /api/assignment-center/admin-summary`  
**Backend:** `crud.py` Lines 468-493

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Assigned (per dept) | Database | `assignments` | `COUNT WHERE department_id=X AND is_published=true` |
| Completed (per dept) | Database | `assignments` | `COUNT WHERE status='completed' AND is_published=true` |
| Remaining (per dept) | Computed | `assignments` | `assigned - completed` |

**Session Cache:** None  
**Demo JSON:** None  
**Database Query:** ✅ **Primary source**

**Final Entity:** Published assignments from database


---

### Requirement Search

**Page:** `frontend/dashboard/src/pages/Requirements.jsx`  
**API:** None  
**Backend:** N/A

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Total Requirements | Demo JSON | `requirements_taxonomy.json` | `requirementsTaxonomy.length` → 2941 |
| Search Results | Demo JSON | `requirements_taxonomy.json` | Client-side `.filter()` |
| Requirement Details | Demo JSON | `requirements_taxonomy.json` | Lookup by req_id |

**Code:** `Requirements.jsx` Line 11
```javascript
import { requirementsTaxonomy } from "../data/demo";
// All searches operate on this static array
```

**Session Cache:** None  
**Demo JSON:** ✅ **Primary source**  
**Database Query:** ❌ **None**

**Final Entity:** Demo requirements from JSON

**IMPACT:** Newly created requirements in database never appear in search!

---

### Knowledge Graph

**Page:** `frontend/dashboard/src/pages/Graph.jsx`  
**API:** None  
**Backend:** N/A

| Metric | Data Source | Table/File | Query |
|--------|-------------|------------|-------|
| Graph Nodes | Session or demo | Generated in `AnalysisSession.jsx` | Nodes from demo data |
| Graph Edges | Session or demo | Generated in `AnalysisSession.jsx` | Edges from demo data |
| Node Details | Demo JSON | `map_details.json`, `requirements_taxonomy.json` | Lookup by ID |

**Code:** `Graph.jsx` Lines 85-90
```javascript
const graphData = viewMode === "active" && hasSession 
  ? session.analysis.scopedGraph    // Session-generated from demo
  : globalGraphData;                 // Pre-generated from demo

// Both sources use demo JSON, not database
```

**Session Cache:** ✅ **Required for scoped view**  
**Demo JSON:** ✅ **Primary source**  
**Database Query:** ❌ **None**

**Final Entity:** Graph visualization from demo data, no database persistence


---

## Part 4: Department Impact Zero Count Investigation

### Issue: Why do departments show 0 immediately after pipeline reports 9 impacted?

**Pipeline Reports:**
- "9 Departments Impacted" (from demo data)
- "205 Requirements" (from demo data)
- "1 Critical MAP" (from demo data)

**Department Dashboard Shows:**
- 0 assignments for all departments

### Root Cause Analysis

#### What Pipeline Actually Creates:

**Code:** `admin_router.py` Lines 141-183
```python
# Creates 14 assignments (sample_requirements has 14 items)
# ALL assignments created with is_published = false (default)

for idx, req_data in enumerate(sample_requirements):
    assignment = crud.create_assignment(
        db=db,
        requirement_id=requirement.id,
        department_id=department.id,
        assigned_by=current_user.id
    )
```

**CRUD function:** `crud.py` Lines 368-383
```python
def create_assignment(...):
    assignment = models.Assignment(
        requirement_id=requirement_id,
        department_id=department_id,
        assigned_by=assigned_by,
        status=models.ComplianceStatus.PENDING,
        is_published=False,  # <-- UNPUBLISHED by default
        ...
    )
```

#### What Dashboard Queries:

**Code:** `crud.py` Lines 468-491
```python
def get_admin_completion_summary(db: Session):
    for dept in departments:
        assignments = db.query(models.Assignment).filter(
            models.Assignment.department_id == dept.id,
            models.Assignment.is_published == True  # <-- PUBLISHED ONLY
        ).all()
```

### Conclusion

**NOT missing persistence** ✅ Assignments ARE in database  
**NOT incorrect query** ✅ Query is correct for published assignments  
**NOT placeholder UI** ✅ UI correctly displays query results  
**Pipeline stage issue** ✅ **ROOT CAUSE IDENTIFIED**


**The Disconnect:**

1. Pipeline creates 14 **unpublished** assignments in database
2. Pipeline shows "9 Departments Impacted" from **demo JSON** (not database)
3. Department Dashboard queries **published** assignments only
4. Result: 0 published assignments = all zeros in dashboard

**This is INTENTIONAL workflow design:**
```
Pipeline → Create Assignments (unpublished) 
         → Assignment Center (review unpublished) 
         → Publish Assignments 
         → Department Dashboard (shows published only)
```

**The "9 Departments" number is DEMO DATA**, not actual pipeline output!

---

## Part 5: Graph Full Text Loss Investigation

### Issue: Why does Global Knowledge Graph lose requirement details after exiting analysis?

**Code Evidence:**

#### Graph Node Click Handler:

`Graph.jsx` Lines 245-270
```javascript
const handleNodeClick = useCallback((node) => {
  if (node.data.type === "requirement") {
    // Attempts to fetch full text
    const fullReq = viewMode === "active" && session 
      ? session.analysis.requirements.find(r => r.req_id === node.data.id)
      : requirementsTaxonomyRaw.find(r => r.requirement_id === node.data.id);
      
    if (fullReq) {
      setFullTextModal({ 
        open: true, 
        title: node.data.id, 
        text: fullReq.text || fullReq.requirement_text 
      });
    }
  }
}, [viewMode, session]);
```

#### The Problem:

**ID Type Mismatch:**
- Graph nodes use: `node.data.id` = Semantic ID string (e.g., "REQ_41YC0107_0022")
- Database uses: `requirements.id` = Integer (e.g., 42)

**Attempted API Call (from previous fix):**
```javascript
// This fails:
const response = await api.get(`/departments/requirements/${node.data.id}`);
// Sends: /departments/requirements/REQ_41YC0107_0022
// Backend expects: /departments/requirements/42 (integer)
```


#### Why It Works During Session:

```javascript
// During active analysis session:
session.analysis.requirements.find(r => r.req_id === node.data.id)
// Uses demo data in session, which HAS semantic IDs
```

#### Why It Fails After Session Ends:

```javascript
// After exiting analysis:
requirementsTaxonomyRaw.find(r => r.requirement_id === node.data.id)
// Fallback to demo JSON works (has semantic IDs)
// But database has NO semantic ID in graph, can't query
```

### Root Cause

**NOT a session dependency for business data**  
**ID mapping problem:**
- Database requirements have semantic IDs stored: `requirements.requirement_id` (string)
- Graph nodes correctly use semantic IDs
- BUT: Current fix attempted to use integer ID API endpoint
- Should use: `GET /admin/requirements?requirement_id={semantic_id}` (string search)

### Correct Solution

Create API endpoint that accepts semantic requirement_id:

```python
# backend/routers/admin_router.py
@router.get("/requirements/by-requirement-id/{requirement_id}")
def get_requirement_by_semantic_id(
    requirement_id: str,  # <-- Accept string semantic ID
    db: Session = Depends(get_db)
):
    req = db.query(models.Requirement).filter(
        models.Requirement.requirement_id == requirement_id
    ).first()
    if not req:
        raise HTTPException(404, "Requirement not found")
    return req
```

**Then frontend can:**
```javascript
const response = await api.get(`/admin/requirements/by-requirement-id/${node.data.id}`);
```

---

## Part 6: Entity Mapping Table with Evidence

| UI Label | Backend Model | Database Table | Actual Business Meaning | Code Evidence |
|----------|---------------|----------------|-------------------------|---------------|
| **Requirement** | `Requirement` | `requirements` | Extracted compliance rule from circular | `models.py` Line 38, `admin_router.py` Line 157 |
| **Assignment** | `Assignment` | `assignments` | Link between requirement and department | `models.py` Line 66, `admin_router.py` Line 175 |
| **MAP** | ❌ **No model** | ❌ **No table** | ❌ **Does not exist** | No code creates MAPs |
| **"Total MAPs"** | `Assignment` | `assignments` | Misleading label for assignments | `crud.py` Line 308, `assignment_center_router.py` Line 31 |
| **Department Assignment** | `Assignment` | `assignments` | Same as "Assignment" | Same entity |
| **Graph Node (Requirement)** | Demo data | `requirements_taxonomy.json` | Visualization from demo JSON | `AnalysisSession.jsx` Line 83 |
| **Graph Node (MAP)** | Demo data | `maps_output.json` | Visualization from demo JSON | `AnalysisSession.jsx` Line 107 |
| **Graph Edge** | Demo data | Generated in session | Computed relationship from demo | `AnalysisSession.jsx` Lines 87-124 |
| **Analysis Session** | React Context | N/A (memory only) | Temporary visualization state | `AnalysisSession.jsx` Line 140 |


---

## Part 7: Demo JSON Purpose Analysis

### Question: Is demo JSON fallback/demo data or production taxonomy?

#### Evidence Review:

**1. Requirements Taxonomy JSON:**
- **Size:** 2941 items
- **Content:** Real RBI circular requirements with proper structure
- **Fields:** `requirement_id`, `domain`, `subdomain`, `source_document`, `requirement_text`
- **Quality:** Production-grade data

**Usage in Dashboard:**
```python
# crud.py Lines 270-278
try:
    json_path = "data/requirements/requirements_taxonomy.json"
    with open(json_path, 'r') as f:
        total_reqs = len(json.load(f))  # PRIMARY SOURCE
except:
    total_reqs = db.query(func.count(models.Requirement.id)).scalar()  # FALLBACK
```

**Observation:** JSON is PRIMARY, database is FALLBACK

**2. Maps Output JSON:**
- **Size:** 2941 items (1:1 with requirements)
- **Content:** Pre-generated "mitigation action plans"
- **Fields:** `map_id`, `task_title`, `department`, `priority`, `impact_score`, `deadline`
- **Quality:** Production-grade data

**Usage:**
```javascript
// Maps.jsx Line 9
import { mapsOutput as globalMapsOutput } from "../data/demo";
// Used directly, no API call
```

**3. Requirements Search:**
```javascript
// Requirements.jsx Line 11
import { requirementsTaxonomy } from "../data/demo";
// Direct import, used for all searches
```

### Conclusion

**Demo JSON is INTENTIONALLY USED AS PRODUCTION TAXONOMY:**

✅ **Evidence:**
1. Dashboard prefers JSON over database (try-catch with JSON first)
2. Requirements Search exclusively uses JSON (no API)
3. MAP Management exclusively uses JSON (no API)
4. Knowledge Graph exclusively uses JSON (no API)
5. 2941 items suggests real curated dataset, not sample
6. Structured with proper RBI circular references

❌ **NOT a fallback/demo:**
- If it were demo data, database would be primary source
- If it were fallback, it would be in the `except` block
- Production features (search, graph) depend entirely on it


### Business Model Interpretation

**Hybrid Architecture:**

1. **Pre-curated Knowledge Base (JSON):**
   - 2941 requirements from historical RBI circulars
   - 2941 pre-generated MAPs
   - Serves as reference taxonomy
   - Used for: Search, Browse, Graph Visualization

2. **Operational Workflow (Database):**
   - New circular uploads
   - Requirement extraction (creates DB records)
   - Assignment creation (creates DB records)
   - Publish workflow
   - Department task tracking

**The Disconnect:**
- New requirements created in DB never sync to JSON taxonomy
- Assignment counts labeled as "MAPs" but different from JSON MAPs
- Two parallel systems operating independently

**This could be INTENTIONAL design:**
- JSON = "Reference library" of all known requirements
- Database = "Active compliance tasks" for current work

**Or it could be INCOMPLETE implementation:**
- JSON was meant to be replaced by database
- Migration never finished
- Frontend still hardcoded to JSON

---

## Part 8: Revised Conclusions

### 1. "MAP" Does NOT Exist as Database Entity ✅ VALIDATED

**Evidence:**
- ❌ No `maps` table in schema
- ❌ No MAP creation in `admin_router.py` processing
- ❌ No MAP model in `models.py`
- ✅ Only `assignments` table exists
- ✅ Backend creates assignments, labels them "maps"

**Business Reality:**
- Backend: Assignment = (Requirement → Department) relationship
- Frontend: "MAP" references either:
  - JSON MAPs (2941 pre-generated proposals)
  - Database assignments (mislabeled as "MAPs")

### 2. Requirements Have Dual Unsynchronized Sources ✅ VALIDATED

**Evidence:**
- ✅ Database `requirements` table (pipeline creates records)
- ✅ JSON `requirements_taxonomy.json` (2941 items)
- ❌ No synchronization between them
- Dashboard prefers JSON (primary) over DB (fallback)
- Requirements Search uses ONLY JSON
- New DB requirements invisible in UI

**Purpose:** JSON appears to be intentional production taxonomy, not demo data


### 3. Knowledge Graph is Session-Only Demo Data ✅ VALIDATED

**Evidence:**
- Graph generated from demo JSON in `AnalysisSession.jsx`
- No database tables for graph storage
- No API endpoints for graph persistence
- Session state cleared on exit
- Cannot view historical graphs

**ID Mapping Issue:**
- Graph uses semantic IDs (strings)
- Database has semantic IDs stored
- But current implementation doesn't query correctly
- Solvable with proper API endpoint

### 4. Numbers Represent Different Data Sources ✅ VALIDATED

| Count | Source | Meaning |
|-------|--------|---------|
| 2941 | `requirements_taxonomy.json` | Reference taxonomy requirements |
| 2941 | `maps_output.json` | Pre-generated MAP proposals |
| 205 | Filtered `requirements_taxonomy.json` | Session-scoped demo requirements |
| 205 | Filtered `maps_output.json` | Session-scoped demo MAPs |
| 70 | Database `assignments` | Unpublished assignments (actual number varies) |
| 14 | Created by pipeline | Actual assignments created per upload |
| 0 | Database query | Published assignments (none until manually published) |

### 5. Department Impact Shows Zero ✅ EXPLAINED

**Root Cause:** Workflow design, not bug

```
Pipeline creates → Unpublished assignments (14 in DB)
Dashboard shows → "9 Departments" (from demo JSON, not DB)
Department Dashboard → Queries published only (0 results)
```

**Solution:** Publish assignments via Assignment Center

### 6. Graph Loses Full Text ✅ EXPLAINED

**Root Cause:** ID mapping, not session dependency

- Requirements HAVE semantic IDs in database
- Graph uses semantic IDs correctly
- Previous fix attempted wrong API endpoint
- Need endpoint accepting semantic ID strings

---

## Part 9: Architectural Intent Hypothesis

### Scenario A: Hybrid Reference + Operational System (Likely)

**Design Intent:**
- JSON files = **Reference Knowledge Base** (historical RBI requirements)
- Database = **Operational Workflow** (current compliance tasks)
- Two systems serve different purposes

**Evidence:**
- Dashboard deliberately uses JSON as primary source
- Search/Browse features use JSON exclusively
- 2941 items suggests curated production dataset
- Pipeline creates operational assignments separately


**Implications:**
- JSON should NOT be removed
- New requirements should be added to BOTH JSON and DB
- Or: New requirements stored in DB only, UI updated to query DB
- Assignment Center = operational task management
- MAP Management = reference library browsing

### Scenario B: Incomplete Migration (Possible)

**Design Intent:**
- Originally used JSON for everything
- Started building database for persistence
- Migration incomplete, frontend still uses JSON
- Pipeline creates DB records but UI doesn't show them

**Evidence:**
- Dashboard has fallback logic (try JSON, then DB)
- Requirements Search has no API integration
- Graph has no persistence
- Duplicate counts from different sources

**Implications:**
- Should complete migration to database
- Update all frontend pages to use APIs
- Remove JSON dependency
- Implement graph persistence

---

## Part 10: Recommended Actions (No Implementation Yet)

### Critical Clarifications Needed

**1. Business Question: What is a "MAP"?**

**Option A:** "MAP" = Assignment (operational task)
- Rename all "MAP" references to "Assignment"
- Accept that 2941 JSON "MAPs" are reference library
- Keep hybrid architecture

**Option B:** "MAP" = Pre-generated proposal distinct from Assignment
- Keep JSON MAPs as reference library
- Assignments link requirements to departments
- Two separate entities with different purposes

**Option C:** "MAP" should be AI-generated mitigation plan
- Implement actual MAP generation logic
- Create separate maps table
- Assignment links MAP to department

**2. Architecture Question: Is JSON intentional or temporary?**

**Option A:** JSON is production reference taxonomy
- Keep JSON as authoritative source
- Sync new DB requirements back to JSON
- Or: Make DB authoritative and remove JSON

**Option B:** JSON is temporary demo data
- Complete migration to database
- Update all UIs to use database APIs
- Remove JSON dependencies


### Minimal Fixes (Evidence-Based)

**1. Terminology Consistency**
- `assignments.total_maps` → `assignments.total_assignments`
- "Published MAPs" → "Published Assignments"
- Only if stakeholders agree MAP = Assignment

**2. Graph Full Text Retrieval**
```python
# Add endpoint accepting semantic ID
@router.get("/requirements/by-requirement-id/{requirement_id}")
def get_by_semantic_id(requirement_id: str, db: Session = Depends(get_db)):
    return db.query(Requirement).filter(
        Requirement.requirement_id == requirement_id
    ).first()
```

**3. Requirements Search API** (if JSON should be replaced)
```python
@router.get("/requirements/search")
def search_requirements(q: str = None, domain: str = None, ...):
    query = db.query(Requirement)
    if q:
        query = query.filter(Requirement.text.ilike(f"%{q}%"))
    return query.all()
```

**4. Documentation**
- Document hybrid architecture intention
- Clarify JSON taxonomy vs DB operational workflow
- Update user guides with correct terminology

---

## Part 11: Final Validation Summary

### Original Conclusions: ✅ VALIDATED with Evidence

1. ✅ **"MAP" does not exist** - Confirmed by schema, models, and processing code
2. ✅ **Requirements have dual sources** - Confirmed by JSON + DB usage
3. ✅ **Graph is session-only** - Confirmed by AnalysisSession implementation
4. ✅ **Numbers are from different sources** - Traced each count to source
5. ✅ **Semantic drift exists** - "maps", "MAPs", "assignments" all used

### New Insights from Validation:

1. **JSON appears intentional**, not just demo fallback
2. **Workflow design causes zero counts**, not missing persistence
3. **Graph ID issue is solvable** with correct API endpoint
4. **Hybrid architecture may be by design**, not incomplete

### Recommended Next Step

**DO NOT start implementation.**

**Stakeholder decision required:**
1. Confirm business definition of "MAP"
2. Confirm JSON taxonomy role (reference vs temporary)
3. Choose architecture model (hybrid vs database-only)

Only after these decisions can we determine correct refactoring approach.

