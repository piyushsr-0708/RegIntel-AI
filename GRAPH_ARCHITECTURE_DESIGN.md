# KNOWLEDGE GRAPH ARCHITECTURE DESIGN

## Executive Summary

**Question:** Can the active session knowledge graph be constructed entirely from backend data?  
**Answer:** ✅ **YES** - Complete graph construction is possible using only backend response data.

**Current Problem:** Frontend copies graph nodes from demo.js (old IDs)  
**Correct Solution:** Build graph nodes from backend `/admin/document-analysis/{id}` response (new IDs)

---

## BACKEND DATA AVAILABLE AFTER UPLOAD

### Endpoint: `GET /admin/document-analysis/{document_id}`

**Location:** `backend/routers/admin_router.py` lines 455-570

### Complete Response Structure

```json
{
  "document": {
    "id": 1,
    "filename": "test.pdf",
    "uploaded_at": "2026-06-28T10:00:00",
    "processed_at": "2026-06-28T10:01:00"
  },
  "counts": {
    "requirements_extracted": 14,
    "assignments_generated": 14,
    "departments_affected": 5,
    "critical_priority": 2,
    "high_priority": 6,
    "medium_priority": 4,
    "low_priority": 2
  },
  "assignments": [
    {
      "id": 1,
      "requirement_id": "REQ_DOC1_0000",           ← NEW FORMAT
      "requirement_text": "Banks must implement...",
      "department": "Compliance",
      "department_id": 3,
      "priority": "Critical",
      "domain": "AML",
      "classification": "Mandatory",
      "is_published": false,
      "status": "pending"
    },
    // ... 13 more assignments
  ],
  "department_summary": [
    {
      "department_id": 3,
      "department_name": "Compliance",
      "total_assignments": 5,
      "critical": 1,
      "high": 2,
      "medium": 1,
      "low": 1
    },
    // ... 4 more departments
  ],
  "priority_distribution": {
    "Critical": 2,
    "High": 6,
    "Medium": 4,
    "Low": 2
  }
}
```

---

## DATA ENTITIES IN RESPONSE

### ✅ Document
- **Source:** `response.document`
- **Fields:** id, filename, uploaded_at, processed_at
- **Available:** YES

### ✅ Requirements
- **Source:** Embedded in `response.assignments[].requirement_id` and `requirement_text`
- **Fields:** requirement_id (NEW FORMAT), text, domain, classification, priority
- **Available:** YES
- **Format:** `REQ_DOC{document_id}_{index}` (e.g., `REQ_DOC1_0000`)

### ✅ Assignments (MAPs)
- **Source:** `response.assignments[]`
- **Fields:** id, requirement_id, department, department_id, priority, status, is_published
- **Available:** YES
- **Note:** In this system, **assignments ARE the MAPs**

### ✅ Departments
- **Source:** `response.department_summary[]`
- **Fields:** department_id, department_name, total_assignments, priority breakdown
- **Available:** YES

### ✅ Circular
- **Source:** `response.document` (represents the circular)
- **Fields:** Same as Document
- **Available:** YES
- **Note:** Document entity IS the regulatory circular

---

## GRAPH NODE TYPES

Based on backend data, the knowledge graph should contain 4 node types:

### 1. Circular Node (Document)
- **Node ID:** `DOC_{document_id}` (e.g., `DOC_1`)
- **Label:** Document filename
- **Type:** `"circular"`
- **Source:** `response.document`

### 2. Requirement Nodes
- **Node ID:** `requirement_id` (e.g., `REQ_DOC1_0000`)
- **Label:** Truncated requirement_id or short text
- **Type:** `"requirement"`
- **Source:** Extract unique requirements from `response.assignments[]`
- **Count:** One node per unique `requirement_id`

### 3. MAP Nodes (Assignments)
- **Node ID:** `MAP_{assignment_id}` (e.g., `MAP_1`)
- **Label:** Department + priority
- **Type:** `"map"` or `"assignment"`
- **Source:** `response.assignments[]`
- **Count:** One node per assignment

### 4. Department Nodes
- **Node ID:** `DEPT_{department_id}` (e.g., `DEPT_3`)
- **Label:** Department name
- **Type:** `"department"`
- **Source:** `response.department_summary[]`
- **Count:** One node per department

---

## GRAPH RELATIONSHIPS (EDGES)

### Complete Node/Edge Architecture

```
CIRCULAR (Document)
    ↓ (defines)
REQUIREMENT 1
    ↓ (generates)
MAP 1 (Assignment to Dept A)
    ↓ (assigned_to)
DEPARTMENT A

REQUIREMENT 1
    ↓ (generates)
MAP 2 (Assignment to Dept B)
    ↓ (assigned_to)
DEPARTMENT B

CIRCULAR (Document)
    ↓ (defines)
REQUIREMENT 2
    ↓ (generates)
MAP 3 (Assignment to Dept A)
    ↓ (assigned_to)
DEPARTMENT A
```

### Edge Definitions

| Source | Target | Label | Cardinality |
|--------|--------|-------|-------------|
| Circular | Requirement | "defines" | 1 circular → N requirements |
| Requirement | MAP | "generates" | 1 requirement → N MAPs (1 per dept) |
| MAP | Department | "assigned_to" | 1 MAP → 1 department |

### Alternative Simplified Architecture (If MAPs = Assignments)

Since assignments ARE the MAPs in this system, you could simplify:

```
CIRCULAR
    ↓ (defines)
REQUIREMENT
    ↓ (assigned_to)
DEPARTMENT
```

**Edges:**
- Circular → Requirement: "defines"
- Requirement → Department: "assigned_to"

**Advantage:** Simpler graph, fewer nodes  
**Disadvantage:** Loses assignment-level metadata (status, remarks, etc.)

---

## RECOMMENDED ARCHITECTURE

### Option A: 4-Level Graph (RECOMMENDED)

**Nodes:** Circular → Requirement → MAP → Department

**Why:** 
- Preserves full system semantics
- MAP nodes can show assignment status (pending/completed)
- Matches existing UI language ("MAPs")
- Supports future features (assignment lifecycle, remarks)

### Option B: 3-Level Graph

**Nodes:** Circular → Requirement → Department

**Why:**
- Simpler
- Fewer nodes to render
- Sufficient for read-only knowledge graph

**Use Case:** If graph is purely informational, not interactive

---

## DETAILED NODE CONSTRUCTION

### From Backend Response to Graph Nodes

#### 1. Circular Node
```javascript
{
  data: {
    id: `DOC_${response.document.id}`,           // DOC_1
    label: response.document.filename,            // "test.pdf"
    type: "circular"
  }
}
```

#### 2. Requirement Nodes
```javascript
// Extract unique requirements
const uniqueRequirements = [...new Set(
  response.assignments.map(a => a.requirement_id)
)];

// Create nodes
uniqueRequirements.map(reqId => ({
  data: {
    id: reqId,                                    // REQ_DOC1_0000
    label: reqId.slice(0, 18),                    // "REQ_DOC1_0000"
    type: "requirement"
  }
}))
```

#### 3. MAP Nodes (Assignment Nodes)
```javascript
response.assignments.map(assignment => ({
  data: {
    id: `MAP_${assignment.id}`,                   // MAP_1
    label: `${assignment.department} - ${assignment.priority}`,
    type: "map",
    status: assignment.status,                    // pending/completed
    priority: assignment.priority                 // Critical/High/Medium/Low
  }
}))
```

#### 4. Department Nodes
```javascript
response.department_summary.map(dept => ({
  data: {
    id: `DEPT_${dept.department_id}`,            // DEPT_3
    label: dept.department_name,                  // "Compliance"
    type: "department",
    totalAssignments: dept.total_assignments      // 5
  }
}))
```

---

## DETAILED EDGE CONSTRUCTION

### From Backend Response to Graph Edges

#### 1. Circular → Requirement Edges
```javascript
// Get circular ID
const circularId = `DOC_${response.document.id}`;

// Get unique requirements
const uniqueRequirements = [...new Set(
  response.assignments.map(a => a.requirement_id)
)];

// Create edges
uniqueRequirements.map(reqId => ({
  data: {
    source: circularId,                          // DOC_1
    target: reqId,                               // REQ_DOC1_0000
    label: "defines"
  }
}))
```

#### 2. Requirement → MAP Edges
```javascript
response.assignments.map(assignment => ({
  data: {
    source: assignment.requirement_id,           // REQ_DOC1_0000
    target: `MAP_${assignment.id}`,              // MAP_1
    label: "generates"
  }
}))
```

#### 3. MAP → Department Edges
```javascript
response.assignments.map(assignment => ({
  data: {
    source: `MAP_${assignment.id}`,              // MAP_1
    target: `DEPT_${assignment.department_id}`,  // DEPT_3
    label: "assigned_to"
  }
}))
```

---

## COMPLETE GRAPH BUILDER PSEUDOCODE

```javascript
function buildKnowledgeGraph(response) {
  const nodes = [];
  const edges = [];
  
  // 1. Create Circular node
  const circularId = `DOC_${response.document.id}`;
  nodes.push({
    data: {
      id: circularId,
      label: response.document.filename,
      type: "circular"
    }
  });
  
  // 2. Create Requirement nodes
  const uniqueRequirements = [...new Set(
    response.assignments.map(a => a.requirement_id)
  )];
  
  uniqueRequirements.forEach(reqId => {
    nodes.push({
      data: {
        id: reqId,
        label: reqId.slice(0, 18),
        type: "requirement"
      }
    });
    
    // Edge: Circular → Requirement
    edges.push({
      data: {
        source: circularId,
        target: reqId,
        label: "defines"
      }
    });
  });
  
  // 3. Create MAP nodes
  response.assignments.forEach(assignment => {
    const mapId = `MAP_${assignment.id}`;
    
    nodes.push({
      data: {
        id: mapId,
        label: `${assignment.department} - ${assignment.priority}`,
        type: "map",
        status: assignment.status,
        priority: assignment.priority
      }
    });
    
    // Edge: Requirement → MAP
    edges.push({
      data: {
        source: assignment.requirement_id,
        target: mapId,
        label: "generates"
      }
    });
  });
  
  // 4. Create Department nodes
  response.department_summary.forEach(dept => {
    const deptId = `DEPT_${dept.department_id}`;
    
    nodes.push({
      data: {
        id: deptId,
        label: dept.department_name,
        type: "department",
        totalAssignments: dept.total_assignments
      }
    });
  });
  
  // 5. Create MAP → Department edges
  response.assignments.forEach(assignment => {
    const mapId = `MAP_${assignment.id}`;
    const deptId = `DEPT_${assignment.department_id}`;
    
    edges.push({
      data: {
        source: mapId,
        target: deptId,
        label: "assigned_to"
      }
    });
  });
  
  return { nodes, edges };
}
```

---

## EXAMPLE WITH REAL DATA

### Input: Backend Response
```json
{
  "document": { "id": 1, "filename": "RBI_Circular_2024.pdf" },
  "assignments": [
    {
      "id": 1,
      "requirement_id": "REQ_DOC1_0000",
      "requirement_text": "Implement KYC updates",
      "department": "Compliance",
      "department_id": 3,
      "priority": "Critical"
    },
    {
      "id": 2,
      "requirement_id": "REQ_DOC1_0000",
      "requirement_text": "Implement KYC updates",
      "department": "Risk",
      "department_id": 5,
      "priority": "High"
    },
    {
      "id": 3,
      "requirement_id": "REQ_DOC1_0001",
      "requirement_text": "Update AML policies",
      "department": "Compliance",
      "department_id": 3,
      "priority": "High"
    }
  ],
  "department_summary": [
    { "department_id": 3, "department_name": "Compliance", "total_assignments": 2 },
    { "department_id": 5, "department_name": "Risk", "total_assignments": 1 }
  ]
}
```

### Output: Knowledge Graph

#### Nodes (7 total)
```javascript
[
  // 1 Circular node
  { data: { id: "DOC_1", label: "RBI_Circular_2024.pdf", type: "circular" } },
  
  // 2 Requirement nodes (unique)
  { data: { id: "REQ_DOC1_0000", label: "REQ_DOC1_0000", type: "requirement" } },
  { data: { id: "REQ_DOC1_0001", label: "REQ_DOC1_0001", type: "requirement" } },
  
  // 3 MAP nodes (assignments)
  { data: { id: "MAP_1", label: "Compliance - Critical", type: "map", status: "pending", priority: "Critical" } },
  { data: { id: "MAP_2", label: "Risk - High", type: "map", status: "pending", priority: "High" } },
  { data: { id: "MAP_3", label: "Compliance - High", type: "map", status: "pending", priority: "High" } },
  
  // 2 Department nodes
  { data: { id: "DEPT_3", label: "Compliance", type: "department", totalAssignments: 2 } },
  { data: { id: "DEPT_5", label: "Risk", type: "department", totalAssignments: 1 } }
]
```

#### Edges (8 total)
```javascript
[
  // Circular → Requirements (2 edges)
  { data: { source: "DOC_1", target: "REQ_DOC1_0000", label: "defines" } },
  { data: { source: "DOC_1", target: "REQ_DOC1_0001", label: "defines" } },
  
  // Requirements → MAPs (3 edges)
  { data: { source: "REQ_DOC1_0000", target: "MAP_1", label: "generates" } },
  { data: { source: "REQ_DOC1_0000", target: "MAP_2", label: "generates" } },
  { data: { source: "REQ_DOC1_0001", target: "MAP_3", label: "generates" } },
  
  // MAPs → Departments (3 edges)
  { data: { source: "MAP_1", target: "DEPT_3", label: "assigned_to" } },
  { data: { source: "MAP_2", target: "DEPT_5", label: "assigned_to" } },
  { data: { source: "MAP_3", target: "DEPT_3", label: "assigned_to" } }
]
```

#### Visual Structure
```
                    DOC_1 (RBI_Circular_2024.pdf)
                      ↓               ↓
         REQ_DOC1_0000           REQ_DOC1_0001
            ↓        ↓                  ↓
       MAP_1      MAP_2             MAP_3
    (Compl-Crit) (Risk-High)    (Compl-High)
         ↓           ↓                ↓
      DEPT_3      DEPT_5          DEPT_3
   (Compliance)   (Risk)       (Compliance)
```

---

## IS DEMO.JS NEEDED?

### Answer: ❌ NO

**For Active Session Graph:**
- ✅ All data exists in backend response
- ✅ Nodes can be built from response
- ✅ Edges can be derived from relationships
- ✅ Node IDs use NEW format (`REQ_DOC1_*`)
- ❌ No need to import demo.js

**For Global Graph (All Documents):**
- Demo.js would still be needed if you want to show ALL documents/requirements from multiple uploads
- But for single-document "Active Session" mode, backend response is sufficient

---

## COMPARISON: DEMO vs BACKEND

### Current (BROKEN) - Using Demo

| Entity | Source | ID Format |
|--------|--------|-----------|
| Requirement Nodes | `demo.js` → JSON files | `REQ_70MK0107_*` (OLD) |
| Edges | `demo.js` → JSON files | Points to OLD IDs |
| Circular | `demo.js` → JSON files | Hardcoded demo data |
| Departments | `demo.js` → JSON files | Hardcoded demo data |

**Problem:** Graph nodes have OLD IDs that don't exist in database

### Proposed (CORRECT) - Using Backend

| Entity | Source | ID Format |
|--------|--------|-----------|
| Circular Node | `response.document` | `DOC_{id}` |
| Requirement Nodes | `response.assignments[]` | `REQ_DOC1_*` (NEW) |
| MAP Nodes | `response.assignments[]` | `MAP_{id}` |
| Department Nodes | `response.department_summary[]` | `DEPT_{id}` |

**Solution:** Graph nodes built from backend data with NEW IDs

---

## MIGRATION STRATEGY

### Current Code (AnalysisSession.jsx lines 103-109)
```javascript
graphData: {
  nodes: graphData.nodes,  // ← FROM DEMO
  edges: graphData.edges,  // ← FROM DEMO
  requirementNodes: data.counts.requirements_extracted,
  assignmentNodes: data.counts.assignments_generated,
  departmentNodes: data.counts.departments_affected
},
```

### Proposed Code
```javascript
const graph = buildKnowledgeGraph(data);  // ← NEW FUNCTION

graphData: {
  nodes: graph.nodes,     // ← FROM BACKEND
  edges: graph.edges,     // ← FROM BACKEND
  requirementNodes: data.counts.requirements_extracted,
  assignmentNodes: data.counts.assignments_generated,
  departmentNodes: data.counts.departments_affected
},

// Also create scopedGraph for Graph.jsx compatibility
scopedGraph: {
  nodes: graph.nodes,
  edges: graph.edges
}
```

---

## DATA MAPPING TABLE

### Backend Response → Graph Nodes

| Backend Field | Graph Node Type | Node ID | Label |
|---------------|----------------|---------|-------|
| `response.document.id` | Circular | `DOC_{id}` | `document.filename` |
| `response.assignments[].requirement_id` | Requirement | `requirement_id` | `requirement_id` (truncated) |
| `response.assignments[].id` | MAP | `MAP_{id}` | `{department} - {priority}` |
| `response.department_summary[].department_id` | Department | `DEPT_{id}` | `department_name` |

### Relationships → Graph Edges

| Relationship | Source | Target | Label |
|--------------|--------|--------|-------|
| Document defines Requirement | `DOC_{document_id}` | `requirement_id` | "defines" |
| Requirement generates MAP | `requirement_id` | `MAP_{assignment_id}` | "generates" |
| MAP assigned to Department | `MAP_{assignment_id}` | `DEPT_{department_id}` | "assigned_to" |

---

## VERIFICATION CHECKLIST

After implementing backend-driven graph builder:

### ✅ Graph Nodes Show NEW IDs
- Requirement nodes display `REQ_DOC1_0000` (not `REQ_70MK0107_*`)
- All node IDs match backend database

### ✅ Click Requirement Works
- Click requirement node in graph
- API call: `GET /admin/requirements/by-semantic-id/REQ_DOC1_0000`
- Backend returns 200 OK (found in database)
- Requirement text displays correctly

### ✅ Graph Reflects Backend State
- Number of requirement nodes = `response.counts.requirements_extracted`
- Number of MAP nodes = `response.counts.assignments_generated`
- Number of department nodes = `response.counts.departments_affected`

### ✅ No Demo Dependency
- Graph renders correctly without demo.js import
- Graph data comes entirely from backend API
- No hardcoded IDs

---

## ADVANTAGES OF BACKEND-DRIVEN GRAPH

### 1. **Consistency**
- Graph IDs match database IDs
- Clicking nodes works (no 404 errors)
- Single source of truth

### 2. **Correctness**
- Shows actual uploaded document data
- Not demo/sample data
- Reflects real assignments and departments

### 3. **Maintainability**
- No need to update demo JSON files
- Backend changes automatically propagate
- Fewer data sources to maintain

### 4. **Scalability**
- Works for any document
- Supports multiple uploads
- No hardcoded limits

### 5. **Accuracy**
- Real-time data (not cached)
- Shows current assignment status
- Reflects database state

---

## ANSWER TO KEY QUESTIONS

### Q: What backend response is returned after upload?

**A:** `GET /admin/document-analysis/{document_id}` returns complete analysis including:
- Document metadata
- Requirement counts
- All assignments with requirement text, department, priority
- Department summary with counts
- Priority distribution

**Location:** `backend/routers/admin_router.py` lines 455-570

---

### Q: Does that response contain assignments, requirements, departments, circular, maps?

**A:** ✅ YES - All entities are present:

| Entity | Available? | Source Field |
|--------|-----------|--------------|
| Circular | ✅ YES | `response.document` |
| Requirements | ✅ YES | `response.assignments[].requirement_id` & `requirement_text` |
| Assignments/MAPs | ✅ YES | `response.assignments[]` |
| Departments | ✅ YES | `response.department_summary[]` |

**Note:** Requirements are embedded in assignment objects (not separate array), but all unique requirements can be extracted.

---

### Q: Is there enough information to construct the active knowledge graph entirely from backend data?

**A:** ✅ **YES - 100% Complete**

**What's Available:**
- ✅ All node types (Circular, Requirement, MAP, Department)
- ✅ All node IDs (in NEW format)
- ✅ All relationships (Document→Requirement→Assignment→Department)
- ✅ All metadata (priority, status, department names, counts)

**What's NOT Needed:**
- ❌ Demo JSON files
- ❌ Hardcoded graph data
- ❌ Additional API calls

**Conclusion:** A frontend graph builder can construct the complete knowledge graph from a single backend API response.

---

### Q: Show exactly which backend objects should become nodes

**A:**

| Backend Object | Becomes | Node ID | Count |
|----------------|---------|---------|-------|
| `response.document` | Circular node | `DOC_{document.id}` | 1 |
| Unique `response.assignments[].requirement_id` | Requirement nodes | `requirement_id` | ~14 |
| Each `response.assignments[]` | MAP nodes | `MAP_{assignment.id}` | ~14 |
| Each `response.department_summary[]` | Department nodes | `DEPT_{department_id}` | ~5 |

**Total Nodes:** ~34 nodes per document

---

### Q: Draw the node/edge relationships

**A:**

```
┌─────────────────────────────────────────────────────────────┐
│                    CIRCULAR (Document)                      │
│                      DOC_1                                  │
│                  "RBI_Circular_2024.pdf"                    │
└──────────┬───────────────────────────────────┬──────────────┘
           │ defines                           │ defines
           ↓                                   ↓
    ┌──────────────┐                    ┌──────────────┐
    │ REQUIREMENT  │                    │ REQUIREMENT  │
    │REQ_DOC1_0000 │                    │REQ_DOC1_0001 │
    │ "KYC Updates"│                    │"AML Policies"│
    └──┬───────┬───┘                    └──────┬───────┘
       │       │ generates                     │ generates
       │       │                               │
       │       ↓                               ↓
       │  ┌─────────┐                    ┌─────────┐
       │  │  MAP_2  │                    │  MAP_3  │
       │  │Risk-High│                    │Comp-High│
       │  └────┬────┘                    └────┬────┘
       │       │ assigned_to                  │ assigned_to
       │       ↓                              ↓
       │  ┌──────────┐                  ┌──────────┐
       │  │  DEPT_5  │                  │  DEPT_3  │
       │  │   Risk   │                  │Compliance│
       │  └──────────┘                  └────┬─────┘
       │                                     ↑
       │ generates                           │ assigned_to
       ↓                                     │
  ┌─────────┐                                │
  │  MAP_1  │                                │
  │Comp-Crit│────────────────────────────────┘
  └─────────┘
```

**Legend:**
- **Circular:** 1 node (document)
- **Requirement:** N nodes (extracted requirements)
- **MAP:** N×M nodes (assignments = requirements × departments)
- **Department:** M nodes (affected departments)

**Edge Types:**
1. Circular → Requirement: "defines" (1-to-many)
2. Requirement → MAP: "generates" (1-to-many, one MAP per department)
3. MAP → Department: "assigned_to" (many-to-one)

---

### Q: Can a frontend graph builder be constructed directly from the upload response without querying demo.js?

**A:** ✅ **YES - No demo.js required**

**Implementation:**
```javascript
// In buildAnalysisResult(), after fetching backend data:

function buildKnowledgeGraphFromBackend(data) {
  const nodes = [];
  const edges = [];
  const nodeIds = new Set();
  
  // 1. Circular node
  const circularId = `DOC_${data.document.id}`;
  nodes.push({ data: { id: circularId, label: data.document.filename, type: "circular" } });
  nodeIds.add(circularId);
  
  // 2. Requirement nodes + edges
  const uniqueReqs = [...new Set(data.assignments.map(a => a.requirement_id))];
  uniqueReqs.forEach(reqId => {
    nodes.push({ data: { id: reqId, label: reqId.slice(0, 18), type: "requirement" } });
    nodeIds.add(reqId);
    edges.push({ data: { source: circularId, target: reqId, label: "defines" } });
  });
  
  // 3. MAP nodes + edges
  data.assignments.forEach(a => {
    const mapId = `MAP_${a.id}`;
    nodes.push({ data: { id: mapId, label: `${a.department}-${a.priority}`, type: "map" } });
    nodeIds.add(mapId);
    edges.push({ data: { source: a.requirement_id, target: mapId, label: "generates" } });
  });
  
  // 4. Department nodes + edges
  data.department_summary.forEach(d => {
    const deptId = `DEPT_${d.department_id}`;
    if (!nodeIds.has(deptId)) {
      nodes.push({ data: { id: deptId, label: d.department_name, type: "department" } });
      nodeIds.add(deptId);
    }
  });
  
  data.assignments.forEach(a => {
    const mapId = `MAP_${a.id}`;
    const deptId = `DEPT_${a.department_id}`;
    edges.push({ data: { source: mapId, target: deptId, label: "assigned_to" } });
  });
  
  return { nodes, edges };
}

// Then use it:
const graph = buildKnowledgeGraphFromBackend(data);

// Replace demo imports with:
graphData: {
  nodes: graph.nodes,  // ← FROM BACKEND
  edges: graph.edges   // ← FROM BACKEND
},
scopedGraph: {
  nodes: graph.nodes,
  edges: graph.edges
}
```

**No demo.js import needed for active session graph.**

---

## CONCLUSION

### ✅ Complete Graph Construction Possible

The backend `/admin/document-analysis/{document_id}` response contains **all necessary information** to construct a complete knowledge graph:

1. **Circular node** from `response.document`
2. **Requirement nodes** from unique `response.assignments[].requirement_id`
3. **MAP nodes** from `response.assignments[]`
4. **Department nodes** from `response.department_summary[]`
5. **All relationships** can be derived from assignment objects

### ✅ No External Dependencies

- No demo.js import needed
- No additional API calls needed
- Single backend response is sufficient

### ✅ Correct ID Format

- Graph uses NEW requirement IDs: `REQ_DOC1_0000`
- Matches database schema
- Clicking nodes works (no 404 errors)

### 🎯 Recommended Implementation

Build a `buildKnowledgeGraphFromBackend(data)` function in `AnalysisSession.jsx` that:
1. Takes backend response as input
2. Generates nodes and edges
3. Returns graph object
4. Replaces demo imports

This will fix the Knowledge Graph OLD ID issue completely.
