# Domain Model Reconciliation - Executive Summary

**Date:** June 28, 2026  
**Status:** ⚠️ CRITICAL SEMANTIC DRIFT DETECTED

---

## Critical Finding #1: "MAP" Does Not Exist

### The Problem

**Throughout the application, "MAP" (Mitigation Action Plan) is referenced extensively, but NO MAP ENTITY EXISTS.**

### Evidence

**Database Schema:**
```sql
-- NO maps table
-- NO map_id field
-- NO MAP generation logic

-- ONLY assignments table exists
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY,
    requirement_id INTEGER,  -- FK to requirements
    department_id INTEGER,   -- FK to departments
    status VARCHAR,
    is_published BOOLEAN,
    ...
);
```

**Backend Code:**
```python
# crud.py Line 308
published_maps = db.query(func.count(models.Assignment.id)).filter(...)

# schemas.py Line 196
total_maps: int  # Field in AssignmentBatch schema

# assignment_center_router.py Line 31
total_maps = sum(dept["task_count"] for dept in summary.values())
```

**Frontend Code:**
```javascript
// demo.js - mapsOutput.json
// AnalysisSession.jsx - maps: docMapEntries
// Dashboard.jsx - "Total MAPs"
// Pipeline.jsx - "Generated MAPs"
```

### What Actually Happens

**Expected (per terminology):**
```
Document → Extract Requirements → Generate MAPs → Assign to Departments
```

**Actual (per code):**
```
Document → Extract Requirements → Create Assignments to Departments
              ↑                          ↑
         requirements table        assignments table
```

### Impact

Every reference to "MAP" in the codebase is **SEMANTICALLY INCORRECT**. The term should be "Assignment".

| Count Location | Says "MAP" | Actually Counts |
|----------------|------------|-----------------|
| Dashboard | "Published MAPs" | Published Assignments |
| Dashboard | "Draft MAPs" | Unpublished Assignments |
| Dashboard | "Critical MAPs" | Assignments with Critical priority |
| Assignment Center | "Total MAPs" | Sum of department assignments |
| Pipeline | "Generated MAPs" | Created assignments |
| Batch Schema | `total_maps` | Count of assignments |

---

## Critical Finding #2: Requirements Have Dual Sources

### The Problem

Requirements exist in TWO PLACES with NO SYNCHRONIZATION:

**Source 1: Database (Persistent)**
- Table: `requirements`
- Created by: Pipeline processing
- Used by: Dashboard metrics, Assignment creation

**Source 2: Demo JSON (Static)**
- File: `data/requirements_taxonomy.json`
- Used by: Requirement Search page, Knowledge Graph
- Contains: 2941 pre-loaded requirements

### Evidence

```python
# crud.py - get_dashboard_summary()
try:
    json_path = "data/requirements/requirements_taxonomy.json"
    with open(json_path, 'r') as f:
        total_reqs = len(json.load(f))  # Uses demo JSON
except:
    total_reqs = db.query(func.count(models.Requirement.id)).scalar()  # Fallback to DB
```

```javascript
// Requirements.jsx
import { requirementsTaxonomy } from "../data/demo";
// Uses demo data, NOT backend API
```

### Impact

1. **Requirement Search shows demo data**, not actual database requirements
2. **Dashboard counts demo data** (2941 requirements), not database
3. **Pipeline creates requirements in database**, but UI doesn't show them
4. **No way to search newly created requirements** in the UI

---

## Critical Finding #3: Knowledge Graph is Session-Only

### The Problem

The Knowledge Graph is ONLY available during an active pipeline analysis session and uses DEMO DATA ONLY.

### Evidence

```javascript
// Graph.jsx
const graphData = viewMode === "active" && hasSession 
  ? session.analysis.scopedGraph    // Session data (demo)
  : globalGraphData;                 // Global demo data

// AnalysisSession.jsx - generateDocumentAnalysis()
// Builds graph from demo JSON files:
// - requirementsTaxonomyRaw
// - mapsOutputRaw
// - mapDetails
```

### Impact

1. **No persistent knowledge graph** - cleared when session ends
2. **Cannot view graph for historical circulars** - only during active session
3. **Graph nodes use semantic IDs** (REQ-XXX) but **database uses integers**
4. **Cannot retrieve full text** using graph node IDs (type mismatch)

---

## Critical Finding #4: Mixed Terminology Everywhere

### Semantic Drift Analysis

The same entity (Assignment) is referred to by FOUR different terms:

| Term | Usage Location | Correct? |
|------|---------------|----------|
| **Assignment** | Database table, ORM model | ✅ YES |
| **MAP** | Backend schemas, comments, variable names | ❌ NO |
| **Task** | Frontend UI labels, Assignment Center | ⚠️ Acceptable |
| **Requirement** | Sometimes conflated with assignment | ❌ NO |

### Examples

**Backend:**
```python
published_maps = count(Assignment)         # Should be published_assignments
total_maps = count(Assignment)             # Should be total_assignments
unpublished_maps = total - published       # Should be unpublished_assignments
```

**Frontend:**
```javascript
"Total MAPs" = summary.total_maps          # Should be "Total Assignments"
"Generated MAPs" = assignments created     # Should be "Created Assignments"
"Critical MAPs" = critical assignments     # Should be "Critical Assignments"
```

---

## Entity Cardinality (ACTUAL)

```
Document (1) ──────────────> Requirements (many)
                                    │
                                    │ (1)
                                    │
                                    ▼
                              Assignments (many)
                                    │
                                    │ (many)
                                    │
                                    ▼
                              Department (1)
```

**Reality:**
- 1 Document → Many Requirements
- 1 Requirement → Many Assignments (can be assigned to multiple departments)
- 1 Assignment → 1 Requirement (many-to-one)
- 1 Assignment → 1 Department (many-to-one)

**There is NO separate MAP entity.**

---

## Count Reconciliation

### Dashboard Metrics - Data Sources

| Metric | Backend Query | Frontend Display | Data Source |
|--------|---------------|------------------|-------------|
| Published Assignments | `COUNT(assignments WHERE is_published=true)` | "Published MAPs" | Database |
| Draft Assignments | `COUNT(assignments WHERE is_published=false)` | "Draft MAPs" | Database |
| Total Requirements | `len(json.load(requirements_taxonomy.json))` | 2941 | Demo JSON |
| Pending Tasks | `COUNT(assignments WHERE status='pending' AND is_published=true)` | "Pending Tasks" | Database |
| Completed Tasks | `COUNT(assignments WHERE status='completed' AND is_published=true)` | "Completed Tasks" | Database |
| Critical Priority | `COUNT(assignments WHERE priority='Critical' AND is_published=true)` | "Critical Priority" | Database |
| Departments Impacted | `COUNT(DISTINCT department_id WHERE is_published=true)` | "Depts Impacted" | Database |

### Assignment Center

| Metric | Backend Query | Frontend Display | Data Source |
|--------|---------------|------------------|-------------|
| Total MAPs | `SUM(task_count for all departments)` | "Total MAPs" | Database (unpublished assignments) |
| Department Task Count | `COUNT(assignments WHERE department_id=X AND is_published=false)` | "{N} Tasks" | Database |

### Pipeline Analysis Session

| Metric | Source | Frontend Display | Data Source |
|--------|--------|------------------|-------------|
| Total Requirements | `len(docRequirements)` | "{N} Requirements" | Demo JSON filtered |
| Total MAPs | `len(docMapEntries)` | "{N} MAPs" | Demo JSON filtered |
| Departments Impacted | `len(docDepartments)` | "{N} Departments" | Demo JSON derived |

---

## Semantic Drift Locations

### Backend Files

1. **crud.py**
   - Line 308: `published_maps` → should be `published_assignments`
   - Line 309: `unpublished_maps` → should be `unpublished_assignments`
   - Line 341: `"published_maps"` → should be `"published_assignments"`
   - Line 344: `"unpublished_assignments"` → correct term, inconsistent with others
   - Line 618: `total_maps` → should be `total_assignments`
   - Line 623: `completed_maps` → should be `completed_assignments`
   - Line 629: `verified_maps` → should be `verified_assignments`
   - Line 636: `batch.total_maps` → schema field should be `total_assignments`

2. **schemas.py**
   - Line 196: `published_maps: int` → should be `published_assignments`
   - Line 272: `total_maps: int` → should be `total_assignments`

3. **models.py**
   - Line 82: `total_maps = Column(...)` → should be `total_assignments`

4. **assignment_center_router.py**
   - Line 31: `total_maps` → should be `total_assignments`
   - Line 35: `"total_maps"` → should be `"total_assignments"`

### Frontend Files

1. **Dashboard.jsx**
   - "Published MAPs" → "Published Assignments"
   - "Draft MAPs" → "Draft Assignments"  
   - "Critical MAPs" → "Critical Assignments"
   - "Total MAPs" → "Total Assignments"

2. **AssignmentCenter.jsx**
   - "Total MAPs Across N Departments" → "Total Assignments"

3. **Pipeline.jsx**
   - "Generated MAPs" → "Created Assignments"
   - "Critical MAPs" → "Critical Assignments"

4. **Maps.jsx** (entire page)
   - Page title "MAP Management" is misleading
   - Should be "Assignment Management" or keep as "MAPs" if redesigning to make MAPs real entities

---

## Data Flow Issues

### Issue 1: Requirements Not Queryable

**Problem:** Pipeline creates requirements in database, but UI searches demo JSON

**Flow:**
```
Pipeline Upload
    ↓
process-document endpoint
    ↓
create_requirement(db, ...) → Stores in database
    ↓
BUT Requirements Search page
    ↓
Uses requirementsTaxonomy from demo.js (static JSON)
    ↓
Newly created requirements NEVER appear in search
```

### Issue 2: Graph Node ID Mismatch

**Problem:** Graph uses semantic IDs, database uses integers

**Flow:**
```
Graph Node Click
    ↓
Node ID = "REQ_41YC0107_0022" (string)
    ↓
Attempts: GET /departments/requirements/{id}
    ↓
Backend expects: INTEGER id (e.g., 42)
    ↓
Result: 404 Not Found / Type Error
```

### Issue 3: Session Dependency

**Problem:** Business data (requirements, assignments) lives in session state

**Flow:**
```
Pipeline Complete
    ↓
Creates database records (requirements, assignments)
    ↓
ALSO stores in session.analysis (demo data derivation)
    ↓
Graph, Analysis pages use session.analysis
    ↓
Exit Analysis
    ↓
Session cleared → Graph/Analysis unavailable
    ↓
BUT database records still exist, unreachable
```

---

## Single Source of Truth - Current State

| Entity | Database | Demo JSON | Session | Authoritative Source |
|--------|----------|-----------|---------|---------------------|
| Documents | ✅ Yes | ❌ No | ❌ No | ✅ Database |
| Requirements | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ **MULTIPLE SOURCES** |
| Assignments | ✅ Yes | ✅ Yes (as "maps") | ✅ Yes (as "maps") | ⚠️ **MIXED** |
| Departments | ✅ Yes | ❌ No | ❌ No | ✅ Database |
| Knowledge Graph | ❌ No | ✅ Yes | ✅ Yes | ⚠️ **NO DATABASE** |
| MAPs | ❌ **DOES NOT EXIST** | ✅ Yes (mapsOutput.json) | ✅ Yes | ⚠️ **PHANTOM ENTITY** |

---

## Impact Summary

### What Works
1. ✅ Assignment creation in database
2. ✅ Publishing workflow (draft → published)
3. ✅ Department assignment tracking
4. ✅ Status progression (pending → in_progress → completed)
5. ✅ Dashboard metrics (though mislabeled)

### What's Broken / Inconsistent
1. ❌ "MAP" terminology everywhere (no such entity)
2. ❌ Requirements search (uses demo, not database)
3. ❌ Knowledge Graph (session-only, no persistence)
4. ❌ Graph full text (ID type mismatch)
5. ❌ Total Requirements count (uses demo JSON)
6. ❌ Newly created requirements invisible in search

---

## Recommended Actions

### Phase 1: Terminology Reconciliation (Highest Priority)

**Goal:** Eliminate "MAP" terminology, use "Assignment" consistently

**Changes Required:**
1. Rename database column: `total_maps` → `total_assignments`
2. Update all backend variables: `*_maps` → `*_assignments`
3. Update schemas: `published_maps` → `published_assignments`
4. Update API responses: `"total_maps"` → `"total_assignments"`
5. Update UI labels: "MAPs" → "Assignments"

**Impact:** ~50 files, ~200 occurrences

### Phase 2: Requirements Single Source (High Priority)

**Goal:** Make database the authoritative source for requirements

**Changes Required:**
1. Create API endpoint: `GET /requirements/search?q=...`
2. Update Requirements.jsx to use API instead of demo JSON
3. Remove dashboard fallback to demo JSON
4. Ensure pipeline-created requirements are searchable

**Impact:** ~5 files

### Phase 3: Knowledge Graph Persistence (Medium Priority)

**Goal:** Store graph in database, remove session dependency

**Changes Required:**
1. Create tables: `graph_nodes`, `graph_edges`
2. Generate graph during pipeline processing
3. Store in database with document/batch reference
4. Update Graph.jsx to query database API
5. Support historical graph viewing

**Impact:** ~10 files, new migrations

### Phase 4: True MAP Generation (Low Priority / Future)

**Goal:** IF MAPs are desired as separate entities, implement properly

**Changes Required:**
1. Create `maps` table with MAP-specific fields
2. Implement MAP generation logic (AI analysis of requirements)
3. Change relationship: Assignment → links MAP to Department
4. Update all workflows

**Impact:** Major architectural change

---

## Decision Required

**Critical Question:** What is a "MAP"?

**Option A: MAP = Assignment (Current Reality)**
- Accept that "MAP" is just terminology
- Rename everything to "Assignment" for clarity
- **Recommended:** This is the simplest fix

**Option B: Make MAPs Real Entities**
- Create actual MAP generation process
- MAP becomes analysis/plan derived from Requirement
- Assignment links MAP to Department
- **Impact:** Major refactor, 2-3 weeks of work

**Recommendation:** **Choose Option A**. The current system works correctly as an assignment tracking system. The only issue is terminology.

---

## Next Steps

1. **Review this analysis** with stakeholders
2. **Decide on MAP definition** (Option A or B)
3. **Create implementation plan** for chosen option
4. **Begin terminology reconciliation** (if Option A)
5. **Implement requirements API** (both options)
6. **Consider graph persistence** (future enhancement)

