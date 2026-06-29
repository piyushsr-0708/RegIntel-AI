# KNOWLEDGE GRAPH OLD REQUIREMENT ID ROOT CAUSE REPORT

## Executive Summary

**Problem:** Knowledge Graph displays old requirement IDs (`REQ_70MK0107_0059_572D39`) causing 404 errors  
**Root Cause:** Graph nodes use **demo JSON data** with old IDs instead of backend data  
**First Failing Line:** `frontend/dashboard/src/context/AnalysisSession.jsx` line ~63-68

---

## EXECUTION FLOW TRACE

### 1. Knowledge Graph Page Renders

**File:** `frontend/dashboard/src/pages/Graph.jsx`  
**Line:** 27

```javascript
const graphData = viewMode === "active" && hasSession 
  ? session.analysis.scopedGraph 
  : globalGraphData;
```

**Behavior:**
- If "Active Session" mode: Uses `session.analysis.scopedGraph`
- If "Global Graph" mode: Uses `globalGraphData` (imported from demo)

---

### 2. Global Graph Data Source (Demo JSON)

**File:** `frontend/dashboard/src/data/demo.js`  
**Lines:** 83-121

**How nodes are built:**

```javascript
// Line 83-88: MAPs come from demo JSON
for (let i = 0; i < mapsOutputRaw.length; i += Math.floor(mapsOutputRaw.length / 40)) {
  if (sampleMaps.length < 40) sampleMaps.push(mapsOutputRaw[i]);
}

// Lines 90-98: Requirements come from demo JSON
const reqsForMaps = new Set();
for (const m of sampleMaps) {
  if (m.requirement_id) reqsForMaps.add(m.requirement_id);  // ← OLD IDs from JSON
}
for (const reqId of reqsForMaps) {
  const req = requirementsTaxonomyRaw.find(r => r.requirement_id === reqId);
  if (req && req.source_document && globalNodeIds.has(req.source_document)) {
    globalNodes.push({ 
      data: { 
        id: reqId,  // ← OLD ID: REQ_70MK0107_0059_572D39
        label: reqId.slice(0, 18), 
        type: "requirement" 
      } 
    });
    globalNodeIds.add(reqId);
    globalEdges.push({ data: { source: req.source_document, target: reqId, label: "defines" } });
  }
}
```

**Data Source:**
- `mapsOutputRaw`: Imported from `./maps_output.json` (line 3)
- `requirementsTaxonomyRaw`: Imported from `./requirements_taxonomy.json` (line 6)

**requirement_id format in JSON files:**
```
REQ_70MK0107_0059_572D39  ← OLD FORMAT (filename + hash)
```

---

### 3. Active Session Graph Data Source (buildAnalysisResult)

**File:** `frontend/dashboard/src/context/AnalysisSession.jsx`  
**Lines:** 63-68

```javascript
// Graph data (use demo structure for MVP, but with backend counts)
graphData: {
  nodes: graphData.nodes,  // ← DEMO STRUCTURE (OLD IDs!)
  edges: graphData.edges,  // ← DEMO STRUCTURE (OLD IDs!)
  requirementNodes: data.counts.requirements_extracted,
  assignmentNodes: data.counts.assignments_generated,
  departmentNodes: data.counts.departments_affected
},
```

**Problem:** Uses `graphData.nodes` from demo import instead of building from backend data

**Import:** Line 3-8
```javascript
import {
  dashboardMetrics, mapsOutput, departmentHeatmap,
  requirementsTaxonomy, graphData, departmentSummary, mapDetails
} from "../data/demo";
```

**Result:** Even "Active Session" mode uses demo JSON nodes with old requirement IDs

---

### 4. Legacy Function (Fallback - generateDocumentAnalysis)

**File:** `frontend/dashboard/src/context/AnalysisSession.jsx`  
**Lines:** 265-270

```javascript
// 4. Add those Requirements and link strictly to the Circular node
for (const reqId of requiredReqIds) {
  scopedNodes.push({ 
    data: { 
      id: reqId,  // ← OLD ID from mapDetails/demo JSON
      label: reqId.slice(0, 18), 
      type: "requirement" 
    } 
  });
  nodeIdSet.add(reqId);
  scopedEdges.push({ data: { source: circularId, target: reqId, label: "defines" } });
}
```

**Data source:** `mapDetails[m.map_id].source_requirement.req_id`  
**Import:** From demo.js which loads from `./map_details.json`  
**Format:** Old requirement IDs from demo JSON

---

### 5. When User Clicks Requirement Node

**File:** `frontend/dashboard/src/pages/Graph.jsx`  
**Lines:** 35-76

```javascript
const handleViewNodeFullText = async () => {
  if (!sel || !sel.id) {
    alert('Please select a node first');
    return;
  }
  
  setLoadingFullText(true);
  
  try {
    if (sel.type === "requirement") {
      // Try session first if available
      if (hasSession && session?.analysis?.requirements) {
        const requirement = session.analysis.requirements.find(
          r => r.req_id === sel.id  // ← Looking for OLD ID in new data
        );
        if (requirement) {
          setSelectedNodeData(requirement);
          setShowFullText(true);
          setLoadingFullText(false);
          return;
        }
      }
      
      // Query database by semantic ID
      try {
        const response = await api.get(`/admin/requirements/by-semantic-id/${sel.id}`);
        // ← API call with OLD ID: GET /admin/requirements/by-semantic-id/REQ_70MK0107_0059_572D39
        // Database has: REQ_DOC1_0000, REQ_DOC1_0001, etc.
        // Result: 404 NOT FOUND
```

**Problem:**
- `sel.id` contains old requirement ID from graph node
- API endpoint looks for this ID in database
- Database only has new IDs (`REQ_DOC1_*`)
- Returns 404

---

## DETAILED SOURCE TRACKING

### Demo JSON Files Location

**Path:** `frontend/dashboard/src/data/`

| File | Contains | Format |
|------|----------|--------|
| `requirements_taxonomy.json` | All requirements | `REQ_70MK0107_0059_572D39` |
| `maps_output.json` | All MAPs | Links to old requirement_ids |
| `map_details.json` | MAP details | Contains old requirement_ids |

### Where Old IDs Are Used

**1. Global Graph (demo.js lines 90-98)**
- Source: `requirementsTaxonomyRaw` from JSON
- Builds nodes with old requirement_ids
- Used when "Global Graph" mode selected

**2. buildAnalysisResult (AnalysisSession.jsx lines 63-68)**
- Source: `graphData` imported from demo.js
- Uses demo structure instead of building from backend
- Used when "Active Session" mode selected
- **THIS IS THE BUG**

**3. generateDocumentAnalysis (AnalysisSession.jsx lines 265-270)**
- Source: `mapDetails` from demo.js
- Extracts old requirement_ids from demo data
- Only used as fallback

**4. Requirements array (AnalysisSession.jsx lines 75-82)**
- Source: Backend `data.assignments`
- Maps to `req_id: a.requirement_id`
- **THESE ARE CORRECT** (new format)

---

## THE ROOT CAUSE LINE

**File:** `frontend/dashboard/src/context/AnalysisSession.jsx`  
**Function:** `buildAnalysisResult()`  
**Lines:** 63-68

```javascript
graphData: {
  nodes: graphData.nodes,  // ← THIS LINE (line 64)
  edges: graphData.edges,  // ← THIS LINE (line 65)
  requirementNodes: data.counts.requirements_extracted,
  assignmentNodes: data.counts.assignments_generated,
  departmentNodes: data.counts.departments_affected
},
```

**Why this is wrong:**
- `graphData` is imported from demo.js (line 3-8)
- demo.js builds nodes from JSON files with old requirement IDs
- Should build nodes from `data.assignments` (backend data) instead
- Backend data has new requirement IDs: `REQ_DOC1_0000`, `REQ_DOC1_0001`, etc.

---

## DATA FLOW DIAGRAM

```
Demo JSON Files (data/*.json)
  ↓ (contains REQ_70MK0107_* IDs)
demo.js (builds globalNodes from JSON)
  ↓
graphData.nodes = [...globalNodes]
  ↓ (imported by AnalysisSession.jsx line 3-8)
buildAnalysisResult() line 64-65
  ↓
graphData: { nodes: graphData.nodes, ... }  ← USES OLD IDs
  ↓
session.analysis.graphData
  ↓
Graph.jsx line 27 (viewMode === "active")
  ↓
session.analysis.scopedGraph  ← NULL (doesn't exist)
Falls back to globalGraphData  ← DEMO DATA (OLD IDs)
  ↓
Cytoscape renders nodes with OLD requirement IDs
  ↓
User clicks node → sel.id = "REQ_70MK0107_..."
  ↓
handleViewNodeFullText() line 60
  ↓
api.get(`/admin/requirements/by-semantic-id/${sel.id}`)
  ↓
Backend queries: SELECT * WHERE requirement_id = 'REQ_70MK0107_...'
  ↓
Database has: REQ_DOC1_0000, REQ_DOC1_0001, ...
  ↓
Result: 404 NOT FOUND
```

---

## WHY IT HAPPENS

### Issue #1: scopedGraph Not Created in buildAnalysisResult

**AnalysisSession.jsx** line ~63-68 creates `graphData` but NOT `scopedGraph`

**Graph.jsx** line 27 expects:
```javascript
session.analysis.scopedGraph  // ← DOES NOT EXIST
```

Falls back to `globalGraphData` from demo.js

### Issue #2: graphData Uses Demo Structure

Even if `graphData` were used, it still references demo nodes:

```javascript
graphData: {
  nodes: graphData.nodes,  // ← From demo.js, not backend
  edges: graphData.edges,  // ← From demo.js, not backend
  ...
}
```

Should be:
```javascript
graphData: {
  nodes: [...build from data.assignments...],
  edges: [...build from data.assignments...],
  ...
}
```

---

## BACKEND ENDPOINT CHECK

**File:** `backend/routers/admin_router.py`  
**Endpoint:** `GET /admin/requirements/by-semantic-id/{semantic_id}`  
**Lines:** 238-248

```python
@router.get("/requirements/by-semantic-id/{semantic_id}", response_model=schemas.RequirementResponse)
def get_requirement_by_semantic_id(
    semantic_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    requirement = crud.get_requirement_by_requirement_id(db, semantic_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement
```

**CRUD Function:** `backend/crud.py` line ~142
```python
def get_requirement_by_requirement_id(db: Session, requirement_id: str):
    return db.query(models.Requirement).filter(
        models.Requirement.requirement_id == requirement_id
    ).first()
```

**Database Query:**
```sql
SELECT * FROM requirements WHERE requirement_id = 'REQ_70MK0107_0059_572D39';
-- Returns: NULL (no rows)
-- Database contains: REQ_DOC1_0000, REQ_DOC1_0001, etc.
```

**Result:** 404 NOT FOUND (correct behavior - old ID doesn't exist)

---

## ANSWER TO KEY QUESTIONS

### Q: Which React component generates or requests these requirement IDs?

**A: Multiple locations:**

1. **Graph.jsx** line 27: Renders graph using `graphData`
2. **Graph.jsx** line 60: Requests requirement details using node ID
3. **demo.js** lines 90-98: Generates global graph nodes from JSON
4. **AnalysisSession.jsx** lines 63-68: Copies demo nodes (doesn't generate new)

### Q: Which backend endpoint serves these requests?

**A:** `GET /admin/requirements/by-semantic-id/{semantic_id}`
- Location: `backend/routers/admin_router.py` line 238
- Queries database by requirement_id
- Returns 404 because old IDs don't exist

### Q: Which backend service constructs graph nodes?

**A: None.** Backend does NOT generate graph nodes.
- Only generates requirements and assignments
- Graph nodes are built on frontend from demo JSON

### Q: Where the requirement ID is assigned to graph nodes?

**A: Frontend demo.js:**

| Location | Function | Line | ID Source |
|----------|----------|------|-----------|
| `demo.js` | Global graph builder | 95-97 | `requirementsTaxonomyRaw` (JSON) |
| `AnalysisSession.jsx` | `buildAnalysisResult()` | 64 | `graphData.nodes` (demo import) |
| `AnalysisSession.jsx` | `generateDocumentAnalysis()` | 267 | `mapDetails` (demo import) |

### Q: Do IDs come from database, graph generation logic, cached graph, frontend transformation, or hardcoded logic?

**A: Demo JSON files (cached/hardcoded)**

**Not from:**
- ❌ Database (backend generates new IDs: REQ_DOC1_*)
- ❌ Graph generation logic (doesn't build from backend)
- ❌ Frontend transformation (just copies demo data)

**From:**
- ✅ Cached demo JSON files in `frontend/dashboard/src/data/`
- ✅ `requirements_taxonomy.json` contains old IDs
- ✅ `maps_output.json` references old IDs
- ✅ `map_details.json` contains old IDs

### Q: Exactly which line of code is responsible for producing REQ_70MK... IDs?

**A: Multiple lines, but the PRIMARY bug is:**

**`frontend/dashboard/src/context/AnalysisSession.jsx` line 64**

```javascript
nodes: graphData.nodes,  // ← Uses demo data instead of backend data
```

**Why:** This line copies demo graph nodes (which have old IDs) into the session analysis object instead of building new nodes from backend data.

---

## SECONDARY SOURCES OF OLD IDs

**1. demo.js line 95-97** (Global graph)
```javascript
globalNodes.push({ 
  data: { 
    id: reqId,  // ← OLD ID from requirementsTaxonomyRaw
    label: reqId.slice(0, 18), 
    type: "requirement" 
  } 
});
```

**2. AnalysisSession.jsx line 267** (Fallback function)
```javascript
scopedNodes.push({ 
  data: { 
    id: reqId,  // ← OLD ID from mapDetails
    label: reqId.slice(0, 18), 
    type: "requirement" 
  } 
});
```

**3. Graph.jsx line 27** (No scopedGraph, falls back to global)
```javascript
const graphData = viewMode === "active" && hasSession 
  ? session.analysis.scopedGraph  // ← DOESN'T EXIST
  : globalGraphData;  // ← Falls back to DEMO DATA
```

---

## VERIFICATION

### What Database Contains

```sql
SELECT requirement_id FROM requirements ORDER BY requirement_id;
-- REQ_DOC1_0000
-- REQ_DOC1_0001
-- REQ_DOC1_0002
-- ... (all with REQ_DOC{id}_ format)
```

### What Graph Displays

```javascript
// Node IDs in graph:
REQ_70MK0107_0059_572D39  ← OLD FORMAT
REQ_70MK0107_0060_ABC123  ← OLD FORMAT
REQ_41YC01072013KF_0001   ← OLD FORMAT
```

### What API Receives

```
GET /admin/requirements/by-semantic-id/REQ_70MK0107_0059_572D39
→ 404 Not Found (correct - doesn't exist in DB)
```

---

## CONCLUSION

**Root Cause:** `buildAnalysisResult()` uses demo graph structure instead of building from backend data

**Exact Line:** `frontend/dashboard/src/context/AnalysisSession.jsx` line 64

**Why:** After fixing requirement_id generation in backend to use `REQ_DOC{id}_*` format, the frontend graph still uses demo JSON files with old `REQ_FILENAME_HASH_*` format

**Impact:**
- Knowledge Graph displays old requirement IDs
- Clicking requirement nodes triggers API calls with old IDs
- Backend correctly returns 404 (ID doesn't exist)
- User sees "Requirement text not found in database"

**Not Fixed During Previous Fix:** The requirement_id fix only changed backend generation logic. Frontend graph data sources were not updated to use new backend data.
