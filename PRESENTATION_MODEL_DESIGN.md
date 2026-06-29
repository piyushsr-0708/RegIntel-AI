# PRESENTATION MODEL DESIGN - MVP STABILIZATION

## OBJECTIVE
Create a single `AnalysisResult` object that guarantees all pages display consistent numbers for the same uploaded document.

---

## AnalysisResult Structure

```typescript
AnalysisResult {
  // Document Metadata
  document: {
    id: number                    // Source: Backend (document.id)
    filename: string              // Source: Backend (document.original_filename)
    uploadedAt: timestamp         // Source: Backend (document.uploaded_at)
    processedAt: timestamp        // Source: Backend (document.processed_at)
  }
  
  // Core Counts (SINGLE SOURCE OF TRUTH)
  counts: {
    requirementsExtracted: number // Source: Backend (response.requirements_created)
    assignmentsGenerated: number  // Source: Backend (response.assignments_created)
    departmentsAffected: number   // Source: Derived (COUNT DISTINCT department_id from assignments)
    criticalPriority: number      // Source: Derived (COUNT assignments WHERE priority='Critical')
    highPriority: number          // Source: Derived (COUNT assignments WHERE priority='High')
    mediumPriority: number        // Source: Derived (COUNT assignments WHERE priority='Medium')
    lowPriority: number           // Source: Derived (COUNT assignments WHERE priority='Low')
  }
  
  // Assignments List (for display)
  assignments: [{
    id: number                    // Source: Backend (assignment.id)
    requirementId: string         // Source: Backend (requirement.requirement_id)
    requirementText: string       // Source: Backend (requirement.text)
    department: string            // Source: Backend (department.name)
    priority: string              // Source: Backend (requirement.priority)
    domain: string                // Source: Backend (requirement.domain)
    classification: string        // Source: Backend (requirement.classification)
    isPublished: boolean          // Source: Backend (assignment.is_published)
  }]
  
  // Department Breakdown
  departmentSummary: [{
    departmentId: number          // Source: Backend (department.id)
    departmentName: string        // Source: Backend (department.name)
    totalAssignments: number      // Source: Derived (COUNT assignments)
    critical: number              // Source: Derived (COUNT WHERE priority='Critical')
    high: number                  // Source: Derived (COUNT WHERE priority='High')
    medium: number                // Source: Derived (COUNT WHERE priority='Medium')
    low: number                   // Source: Derived (COUNT WHERE priority='Low')
  }]
  
  // Priority Distribution (for charts)
  priorityDistribution: {
    Critical: number              // Source: Derived (from counts.criticalPriority)
    High: number                  // Source: Derived (from counts.highPriority)
    Medium: number                // Source: Derived (from counts.mediumPriority)
    Low: number                   // Source: Derived (from counts.lowPriority)
  }
  
  // Dashboard Metrics
  dashboardSummary: {
    totalUnpublished: number      // Source: Derived (COUNT assignments WHERE is_published=false)
    totalPublished: number        // Source: Derived (COUNT assignments WHERE is_published=true)
    pendingTasks: number          // Source: Derived (COUNT WHERE status='pending')
    completedTasks: number        // Source: Derived (COUNT WHERE status='completed')
  }
  
  // Graph Data (for visualization)
  graphData: {
    nodes: []                     // Source: Demo (fallback until backend implements)
    edges: []                     // Source: Demo (fallback until backend implements)
    requirementNodes: number      // Source: Derived (counts.requirementsExtracted)
    assignmentNodes: number       // Source: Derived (counts.assignmentsGenerated)
    departmentNodes: number       // Source: Derived (counts.departmentsAffected)
  }
}
```

---

## Field Source Matrix

| Field | Source Type | Backend Table | Derived From | Demo Fallback | Builder Function |
|-------|-------------|---------------|--------------|---------------|------------------|
| document.id | Backend | documents | - | No | Direct copy |
| document.filename | Backend | documents | - | No | Direct copy |
| counts.requirementsExtracted | Backend | requirements | COUNT(*) | No | Query DB |
| counts.assignmentsGenerated | Backend | assignments | COUNT(*) | No | Query DB |
| counts.departmentsAffected | Derived | assignments | COUNT DISTINCT department_id | No | Aggregate |
| counts.criticalPriority | Derived | requirements+assignments | JOIN + COUNT WHERE priority='Critical' | No | Aggregate |
| assignments[] | Backend | assignments+requirements+departments | JOIN all 3 tables | No | Query + Join |
| departmentSummary[] | Derived | assignments+departments | GROUP BY department_id | No | Aggregate |
| priorityDistribution | Derived | - | Transform counts.* | No | Transform |
| dashboardSummary | Derived | assignments | Various COUNT queries | No | Aggregate |
| graphData.nodes | Demo | - | - | Yes (until backend) | Use demo structure |
| graphData.edges | Demo | - | - | Yes (until backend) | Use demo structure |

---

## Builder Function Design

### Location
`context/AnalysisSession.jsx` → Replace `generateDocumentAnalysis()`

### Signature
```javascript
async function buildAnalysisResult(documentId, api) {
  // 1. Fetch requirements for this document
  const requirements = await api.get(`/admin/requirements?document_id=${documentId}`);
  
  // 2. Fetch assignments for this document
  const assignments = await api.get(`/admin/assignments?document_id=${documentId}`);
  
  // 3. Derive all counts from fetched data
  // 4. Build departmentSummary from assignments
  // 5. Build priorityDistribution from counts
  // 6. Use demo graph structure (temporary)
  
  return AnalysisResult;
}
```

### Data Flow
```
Backend Database
    ↓
GET /admin/requirements?document_id=X (returns 14)
GET /admin/assignments?document_id=X (returns 14)
    ↓
buildAnalysisResult(documentId, api)
    ↓
    ├─ counts.requirementsExtracted = 14
    ├─ counts.assignmentsGenerated = 14
    ├─ counts.departmentsAffected = COUNT DISTINCT(department)
    ├─ assignments = [...] (full list)
    ├─ departmentSummary = GROUP BY department
    ├─ priorityDistribution = aggregate by priority
    ├─ dashboardSummary = aggregate by status
    └─ graphData = demo structure (fallback)
    ↓
AnalysisResult (SINGLE OBJECT)
    ↓
session.analysisResult (stored in context)
    ↓
All pages read from session.analysisResult
```

---

## Consumer Pages

### Pipeline Results
**Consumes:**
- `counts.requirementsExtracted` → "14 requirements found"
- `counts.assignmentsGenerated` → "14 assignments created"
- `counts.departmentsAffected` → "5 departments impacted"
- `counts.criticalPriority` → "2 critical tasks"
- `departmentSummary[]` → Department breakdown cards
- `assignments[]` → Top priority assignments list

**Status:** ✅ Can consume directly

---

### Dashboard (Session Mode)
**Consumes:**
- `counts.requirementsExtracted` → KPI "Requirements Extracted"
- `counts.assignmentsGenerated` → KPI "Assignments Generated"
- `counts.criticalPriority` → KPI "Critical Priority"
- `counts.departmentsAffected` → KPI "Departments Impacted"
- `priorityDistribution` → Pie chart
- `departmentSummary[]` → Department risk bar chart

**Status:** ✅ Can consume directly

---

### MAP Management (Document Scoped)
**Consumes:**
- `assignments[]` → Full list with filters
- `counts.assignmentsGenerated` → Total count
- `priorityDistribution` → Filter counts

**Status:** ✅ Can consume directly (just rename "maps" to "assignments")

---

### Knowledge Graph (Active Mode)
**Consumes:**
- `graphData.nodes` → Cytoscape nodes
- `graphData.edges` → Cytoscape edges
- `counts.*` → Stats display
- `assignments[]` → Node details on click

**Status:** ⚠️ Partial - Graph structure from demo, counts from backend

---

### Department Dashboard
**Consumes:**
- `departmentSummary[]` → Department cards
- `counts.departmentsAffected` → Total departments
- `priorityDistribution` → Heatmap

**Status:** ✅ Can consume directly

---

### Requirements Summary
**Consumes:**
- `counts.requirementsExtracted` → Total count
- `assignments[].requirementText` → List of requirement texts
- `assignments[].domain` → Filter by domain

**Status:** ✅ Can consume directly (display requirements from assignments)

---

## Pages That Cannot Consume (with reasons)

### Assignment Center
**Reason:** Needs unpublished assignments across ALL documents, not just current
**Workaround:** Keep existing API `GET /assignment-center/summary`
**Status:** ✅ Already correct - no change needed

---

### Department Workspace
**Reason:** Needs published assignments for specific department, not current document
**Workaround:** Keep existing API `GET /workspace/tasks`
**Status:** ✅ Already correct - no change needed

---

### MAP Detail Page
**Reason:** Needs single assignment by ID, not document-scoped
**Workaround:** Create new API `GET /admin/assignments/{id}/detail` OR keep demo fallback
**Status:** ⚠️ Needs backend endpoint (not critical for MVP)

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────┐
│           Backend Database                      │
│  • requirements table (14 records)              │
│  • assignments table (14 records)               │
│  • departments table (9 records)                │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│     API Endpoints (already exist)               │
│  GET /admin/requirements?document_id=X          │
│  GET /admin/assignments?document_id=X           │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  buildAnalysisResult(documentId, api)           │
│  • Fetch requirements                           │
│  • Fetch assignments                            │
│  • Derive all counts                            │
│  • Build departmentSummary                      │
│  • Build priorityDistribution                   │
│  • Use demo graph (temporary)                   │
│  Returns: AnalysisResult (single object)        │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  session.analysisResult                         │
│  (stored in AnalysisSession context)            │
└──────────────┬──────────────────────────────────┘
               │
               ├─────────────┬─────────────┬──────────────┬────────────┐
               ▼             ▼             ▼              ▼            ▼
         ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌─────────┐
         │ Pipeline │  │Dashboard │  │    MAP    │  │Knowledge │  │  Dept   │
         │ Results  │  │(Session) │  │Management │  │  Graph   │  │Dashboard│
         └──────────┘  └──────────┘  └───────────┘  └──────────┘  └─────────┘
         
         ┌────────────────┐
         │  Requirements  │
         │    Summary     │
         └────────────────┘
```

All 6 pages read from SAME object → Guaranteed consistency!

---

## Consistency Guarantees

### ✅ GUARANTEED
1. Pipeline shows "14 requirements" → Dashboard shows "14 requirements" → Requirements page shows 14 items
2. Pipeline shows "5 departments" → Dashboard shows "5 departments" → Department breakdown has 5 cards
3. Pipeline shows "2 critical" → Dashboard pie chart shows "2 critical" → MAP list filters to 2 critical
4. All counts derived from SAME assignments array → mathematically impossible to be inconsistent

### ⚠️ TEMPORARY INCONSISTENCY (acceptable for MVP)
1. Knowledge Graph structure from demo (nodes/edges don't match exact counts)
   - **Mitigation:** Display counts from backend, structure from demo
   - **User sees:** "14 requirements" (correct) but graph shows ~20 nodes (demo)
   - **Acceptable:** Graph is visualization aid, not data source

---

## Missing Backend Endpoints

### Required for Full Backend Integration
1. `GET /admin/requirements?document_id={id}` - **Already exists?** Need to verify
2. `GET /admin/assignments?document_id={id}` - **Needs filter parameter added**
3. `GET /admin/assignments/{id}/detail` - **Missing** (for MAP Detail page)

### Optional for Future
4. `GET /admin/graph?document_id={id}` - **Missing** (Knowledge Graph structure)

---

## MVP Migration Order

### Phase 1: SAFEST (Zero Risk)
1. **Create `buildAnalysisResult()` function**
   - Build in parallel with existing `generateDocumentAnalysis()`
   - Does NOT break anything
   - Can be tested independently

2. **Add API filter parameters**
   - `GET /admin/assignments?document_id={id}`
   - Backend change only, no frontend impact

### Phase 2: LOW RISK
3. **Pipeline Results Page**
   - Switch from `session.analysis` to `session.analysisResult`
   - Only affects Pipeline results display
   - Easy to revert

4. **Requirements Summary Page**
   - Switch from `requirementsTaxonomy` to `session.analysisResult.assignments`
   - Isolated page, low traffic

### Phase 3: MEDIUM RISK
5. **Dashboard Session Mode**
   - Switch from `session.analysis.stats` to `session.analysisResult.counts`
   - Affects main dashboard but has fallback modes
   - Test thoroughly

6. **MAP Management (Document Scoped)**
   - Switch from `session.analysis.maps` to `session.analysisResult.assignments`
   - Only affects document-scoped view
   - Global view unchanged

### Phase 4: HIGHER RISK (After MVP)
7. **Knowledge Graph Active Mode**
   - Use `session.analysisResult.graphData`
   - Keep demo structure, use backend counts
   - Complex visualization

8. **Department Dashboard**
   - Switch from demo `departmentHeatmap` to `session.analysisResult.departmentSummary`
   - Affects department risk page

### Phase 5: FUTURE (Not for MVP)
9. **MAP Detail Page** - Needs new backend endpoint
10. **Delete Demo Data** - Only after 100% backend migration

---

## Implementation Checklist (For Reference Only - DO NOT IMPLEMENT YET)

- [ ] Backend: Add `document_id` filter to assignments endpoint
- [ ] Context: Create `buildAnalysisResult()` function
- [ ] Context: Call `buildAnalysisResult()` after pipeline completes
- [ ] Pipeline: Switch to `session.analysisResult.counts`
- [ ] Dashboard: Switch to `session.analysisResult.counts`
- [ ] Maps: Switch to `session.analysisResult.assignments`
- [ ] Requirements: Switch to `session.analysisResult.assignments`
- [ ] Knowledge Graph: Switch to `session.analysisResult.graphData`
- [ ] Test: Verify all pages show same numbers
- [ ] Test: Upload different document, verify numbers change
- [ ] Test: Compare Pipeline vs Dashboard vs Maps counts

---

## SUCCESS CRITERIA

**Before Migration:**
- Pipeline: 720 requirements (varies by filename)
- Dashboard: 85 MAPs (varies by filename)  
- Assignment Center: 14 tasks (backend)
- ❌ INCONSISTENT

**After Migration:**
- Pipeline: 14 requirements (from backend)
- Dashboard: 14 assignments (from backend)
- Assignment Center: 14 tasks (from backend)
- ✅ CONSISTENT

**All numbers derived from SAME source → consistency guaranteed!**
