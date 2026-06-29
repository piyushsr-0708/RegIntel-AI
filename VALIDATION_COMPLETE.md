# Domain Model Validation Pass - COMPLETE ✅

**Date:** June 28, 2026  
**Status:** Validation complete, awaiting stakeholder decision  
**Duration:** Complete lifecycle trace with code evidence

---

## Deliverables Created

### 1. ✅ DOMAIN_MODEL_VALIDATION.md (Comprehensive)
**Comprehensive validation document with:**
- Complete lifecycle trace (upload → dashboard)
- Evidence-based number reconciliation
- Page-by-page data source mapping
- Department impact zero count explanation
- Graph full text loss root cause
- Entity mapping table with code references
- Demo JSON purpose analysis
- Architectural intent hypotheses

**Key Sections:**
- Part 1: Complete Lifecycle Trace
- Part 2: Number Reconciliation with Evidence
- Part 3: Page-by-Page Data Source Mapping
- Part 4: Department Impact Investigation
- Part 5: Graph Full Text Loss Investigation
- Part 6: Entity Mapping Table
- Part 7: Demo JSON Purpose Analysis
- Part 8: Revised Conclusions
- Part 9: Architectural Intent Hypothesis
- Part 10: Recommended Actions
- Part 11: Final Validation Summary

### 2. ✅ VALIDATION_EXECUTIVE_SUMMARY.md
**Executive summary including:**
- Key validated findings
- Number reconciliation table
- Department impact explanation
- Graph full text loss solution
- Critical insight: Hybrid architecture may be intentional
- Critical decisions required
- Comparison: intended vs actual
- Recommended path forward

### 3. ✅ UI_TO_CODE_MAPPING.md
**Quick reference guide:**
- Every displayed metric mapped to code location
- Data source matrix (Database vs JSON vs Session)
- Workflow understanding
- Terminology mapping
- Per-page breakdowns:
  - Dashboard
  - Pipeline Results
  - Assignment Center
  - MAP Management
  - Requirements Search
  - Knowledge Graph
  - Department Dashboard
  - Department Workspace
  - Risk Analysis

---

## Validation Results

### All Original Conclusions: ✅ VALIDATED

1. ✅ **"MAP" does not exist as database entity**
   - Confirmed with schema, models, processing code
   - Evidence: No maps table, no MAP creation in pipeline

2. ✅ **Requirements have dual unsynchronized sources**
   - Confirmed JSON (2941) + Database (variable)
   - Evidence: Dashboard prefers JSON, Search uses only JSON

3. ✅ **Knowledge Graph is session-only demo data**
   - Confirmed no database persistence
   - Evidence: Generated from demo JSON in AnalysisSession

4. ✅ **Numbers represent different data sources**
   - All counts traced to exact source
   - Evidence: See number reconciliation table

5. ✅ **Semantic drift exists**
   - "maps", "MAPs", "assignments" all refer to same entity
   - Evidence: Variable names throughout codebase


### Critical New Insight: 🔍 Nuance Added

**JSON may be intentional production taxonomy, not demo data**

**Evidence:**
- Dashboard prefers JSON over database (JSON in try, DB in except)
- 2941 items suggests curated production dataset
- Production-grade RBI circular data
- Search/Browse features use JSON exclusively

**Implication:** Hybrid architecture may be by design:
- **JSON = Reference knowledge base** (historical requirements catalog)
- **Database = Operational workflow** (current compliance tasks)

---

## Questions Answered with Evidence

### Q1: Do MAPs exist as database entities?
**A:** ❌ No. Only `assignments` table exists.

**Evidence:**
- `backend/routers/admin_router.py` Line 175: Creates `Assignment`, not MAP
- `backend/models.py`: No MAP model
- Database schema: No `maps` table
- Pipeline creates 14 assignments, labels them as "maps" in variables

### Q2: Are requirements and MAPs the same entity?
**A:** Depends on context.

**In Database:**
- Requirements = `requirements` table (compliance rules)
- Assignments = `assignments` table (requirement → department links)
- MAPs = Do not exist

**In Demo JSON:**
- Requirements = 2941 items in `requirements_taxonomy.json`
- MAPs = 2941 items in `maps_output.json` (1:1 mapping)
- Separate but related entities

### Q3: Why does pipeline report "205 Generated MAPs"?
**A:** Demo data visualization, not actual pipeline output.

**Evidence:**
- `AnalysisSession.jsx` Lines 26-48: Filters demo JSON by filename
- `Pipeline.jsx` Line 68: Displays session stats from demo data
- Actual pipeline creates 14 assignments in database
- Frontend shows ~205 from filtered demo JSON

### Q4: Why does Assignment Center show different count?
**A:** Different data source.

**Evidence:**
- Assignment Center: Database unpublished assignments (~70)
- Pipeline Results: Filtered demo JSON (~205)
- MAP Management: Full demo JSON (2941)
- Three different sources, three different counts

### Q5: Why do departments show 0 after pipeline reports 9 impacted?
**A:** Workflow design + demo data disconnect.

**Evidence:**
- Pipeline creates 14 **unpublished** assignments in DB
- Pipeline shows "9 departments" from **demo JSON** (not DB)
- Department Dashboard queries **published** assignments only
- Result: 0 published = all zeros

**Solution:** Publish via Assignment Center


### Q6: Why does graph lose requirement text after exiting?
**A:** ID mapping issue, not session dependency.

**Evidence:**
- Requirements in DB have semantic IDs: `requirement_id = "REQ_XXX"`
- Graph nodes correctly use semantic IDs: `node.data.id = "REQ_XXX"`
- Previous fix attempted integer ID endpoint: `/requirements/42` ❌
- Should use semantic ID endpoint ✅

**Minimal Fix:**
```python
@router.get("/requirements/by-requirement-id/{requirement_id}")
def get_by_semantic_id(requirement_id: str, db: Session):
    return db.query(Requirement).filter(
        Requirement.requirement_id == requirement_id
    ).first()
```

### Q7: Should demo JSON be removed?
**A:** ⚠️ **UNCLEAR - Stakeholder decision required**

**Evidence suggesting keep:**
- Dashboard prefers JSON (primary source)
- 2941 items = curated production taxonomy
- Search/Browse depend on it entirely
- Production-grade data quality

**Evidence suggesting remove:**
- Creates confusion with database
- New requirements don't sync
- Duplicate counts
- Two parallel systems

**Decision needed:** Is this intentional hybrid architecture or incomplete migration?

---

## Critical Decisions Required

### Decision 1: What is a "MAP"?

| Option | Description | Impact |
|--------|-------------|--------|
| **A** | MAP = Assignment (operational task) | Rename variables/labels only |
| **B** | MAP = Reference proposal (separate from Assignment) | Keep JSON MAPs, document distinction |
| **C** | MAP = AI-generated mitigation plan (new feature) | Major implementation required |

**Validation finding:** Currently MAP label refers to assignments in code, but JSON has separate MAP entities.

### Decision 2: Is JSON production or temporary?

| Option | Description | Impact |
|--------|-------------|--------|
| **A** | Production reference taxonomy | Keep JSON, maintain hybrid |
| **B** | Temporary demo data | Complete migration to DB |

**Validation finding:** Evidence suggests JSON may be intentional production taxonomy.

---

## Minimal Architectural Fixes

### If Keeping Hybrid Architecture:

**1. Add Semantic ID Endpoint**
```python
# backend/routers/admin_router.py
@router.get("/requirements/by-requirement-id/{requirement_id}")
def get_requirement_by_semantic_id(requirement_id: str, db: Session):
    return db.query(Requirement).filter(
        Requirement.requirement_id == requirement_id
    ).first()
```
**Purpose:** Fix graph full text retrieval

**2. Document Architecture**
- Explain JSON = reference knowledge base
- Explain Database = operational workflow
- Update user documentation

**3. Terminology Cleanup**
- Rename `total_maps` → `total_assignments` in schemas
- Update UI labels for consistency
- Keep JSON "MAPs" as reference term


### If Migrating to Database-Only:

**1. Requirements Search API**
```python
# backend/routers/requirement_router.py (NEW)
@router.get("/requirements/search")
def search_requirements(q: str = None, domain: str = None, db: Session):
    query = db.query(Requirement)
    if q:
        query = query.filter(Requirement.text.ilike(f"%{q}%"))
    if domain:
        query = query.filter(Requirement.domain == domain)
    return query.all()
```

**2. Update Requirements.jsx**
- Remove demo JSON import
- Use API for search
- Display database results

**3. Update Maps.jsx**
- Query assignments from database
- Remove demo JSON dependency

**4. Graph Persistence**
- Create graph tables
- Generate during pipeline
- Store in database

**5. Phase Out JSON**
- Migrate existing JSON data to database
- Remove JSON files
- Update all imports

---

## Verification Methodology

### Complete Lifecycle Traced:

1. ✅ **Document Upload**
   - File: `admin_router.py` Lines 22-73
   - Action: Creates document record only
   - Database write: `documents` table

2. ✅ **Document Processing**
   - File: `admin_router.py` Lines 76-187
   - Action: Creates 14 requirements + 14 assignments
   - Database writes: `requirements`, `assignments` tables
   - No MAP creation found

3. ✅ **Frontend Analysis Session**
   - File: `AnalysisSession.jsx` Lines 11-138
   - Action: Generates demo data visualization
   - Source: Filters `requirements_taxonomy.json` and `maps_output.json`
   - Database query: None

4. ✅ **Dashboard Display**
   - File: `Dashboard.jsx`
   - API: `GET /api/admin/dashboard`
   - Backend: `crud.py` Lines 268-355
   - Sources: Mixed (JSON for requirements, DB for assignments)

### Every Number Traced:

| Display | Source File | Line Number | Query/Calculation |
|---------|-------------|-------------|-------------------|
| 2941 Requirements | `requirements_taxonomy.json` | N/A | Array length |
| 2941 MAPs | `maps_output.json` | N/A | Array length |
| 205 Generated MAPs | `AnalysisSession.jsx` | 26-48 | Filtered array |
| 70 Total MAPs | `assignment_center_router.py` | 31 | SUM(unpublished) |
| 14 Requirements | `admin_router.py` | 141 | Loop iterations |
| 0 Dept Assignments | `crud.py` | 468-491 | COUNT WHERE published |

### Every Page Analyzed:

✅ Dashboard  
✅ Pipeline Results  
✅ Assignment Center  
✅ MAP Management  
✅ Department Dashboard  
✅ Department Workspace  
✅ Requirements Search  
✅ Knowledge Graph  
✅ Risk Analysis

**All data sources identified and documented.**

---

## Files Referenced in Validation

### Backend Files:
- `backend/main.py` - API routes registration
- `backend/models.py` - Database models (no MAP model)
- `backend/schemas.py` - API schemas (uses "total_maps")
- `backend/crud.py` - All database operations
- `backend/routers/admin_router.py` - Document processing pipeline
- `backend/routers/assignment_center_router.py` - Assignment management
- `backend/routers/department_workspace_router.py` - Department tasks

### Frontend Files:
- `frontend/dashboard/src/pages/Dashboard.jsx` - Main dashboard
- `frontend/dashboard/src/pages/Pipeline.jsx` - Analysis results
- `frontend/dashboard/src/pages/AssignmentCenter.jsx` - Assignment review
- `frontend/dashboard/src/pages/Maps.jsx` - MAP management
- `frontend/dashboard/src/pages/Requirements.jsx` - Requirements search
- `frontend/dashboard/src/pages/Graph.jsx` - Knowledge graph
- `frontend/dashboard/src/pages/DepartmentWorkspace.jsx` - User tasks
- `frontend/dashboard/src/context/AnalysisSession.jsx` - Session state
- `frontend/dashboard/src/data/demo.js` - Demo data imports

### Data Files:
- `frontend/dashboard/src/data/requirements_taxonomy.json` - 2941 requirements
- `frontend/dashboard/src/data/maps_output.json` - 2941 MAPs
- `frontend/dashboard/src/data/map_details.json` - MAP metadata

**All files examined for complete understanding.**

---

## Next Steps

### Immediate (Before Any Code Changes):

1. **Stakeholder Meeting**
   - Review validation findings
   - Clarify business definition of "MAP"
   - Confirm JSON taxonomy role
   - Choose architecture model

2. **Document Decisions**
   - Record architectural intent
   - Update system documentation
   - Create user guides

3. **Plan Implementation** (After Decisions)
   - Choose minimal fix approach
   - Create implementation tasks
   - Estimate effort

### DO NOT Proceed With:

❌ Renaming "MAP" to "Assignment" (until decision)  
❌ Removing demo JSON (until purpose confirmed)  
❌ Building new APIs (until architecture chosen)  
❌ Modifying database schema (until workflow confirmed)

---

## Conclusion

**Validation Status:** ✅ **COMPLETE**

**All audit conclusions validated with code evidence.**

**Critical insight:** What appeared to be incomplete implementation may actually be intentional hybrid architecture (JSON reference + DB workflow).

**Confidence Level:** HIGH - Every claim backed by file paths and line numbers.

**Next Required Action:** **Stakeholder meeting to clarify architectural intent.**

**No code changes recommended** until business decisions are made.

---

## Document Index

1. **DOMAIN_MODEL_VALIDATION.md** - Comprehensive technical validation (11 parts)
2. **VALIDATION_EXECUTIVE_SUMMARY.md** - Executive summary with key findings
3. **UI_TO_CODE_MAPPING.md** - Quick reference for all displayed metrics
4. **VALIDATION_COMPLETE.md** - This summary document

**All validation deliverables complete and ready for review.**

