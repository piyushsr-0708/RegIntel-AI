# Count Reconciliation - Every Displayed Metric Mapped to Source

## Dashboard Metrics

### Published Assignments (Labeled: "Published MAPs")

**Backend:**
```python
# crud.py Line 308
published_maps = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `published_maps`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (e.g., 36, 0 after session exit)

---

### Draft Assignments (Labeled: "Draft MAPs" / "Unpublished MAPs")

**Backend:**
```python
# crud.py Line 309
total_assignments = db.query(func.count(models.Assignment.id)).scalar()
unpublished_maps = total_assignments - published_maps
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `unpublished_assignments`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (e.g., 34, 205)

---

### Total Requirements

**Backend:**
```python
# crud.py Lines 270-278
try:
    json_path = "data/requirements/requirements_taxonomy.json"
    with open(json_path, 'r') as f:
        total_reqs = len(json.load(f))  # Demo JSON
except:
    total_reqs = db.query(func.count(models.Requirement.id)).scalar()
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `total_requirements`  
**Frontend:** Dashboard.jsx (not displayed in current version)  
**Current Value:** 2941 (demo data)

**⚠️ ISSUE:** Uses demo JSON, not database

---

### Pending Tasks

**Backend:**
```python
# crud.py Lines 289-293
pending = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "pending",
    models.Assignment.is_published == True
).scalar()
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `pending_assignments`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (only published assignments)

---

### Completed Tasks

**Backend:**
```python
# crud.py Lines 301-305
completed = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "completed",
    models.Assignment.is_published == True
).scalar()
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `completed_assignments`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (only published assignments)

---

### Critical Priority (Labeled: "Critical MAPs")

**Backend:**
```python
# crud.py Lines 314-326
assignments = db.query(models.Assignment, models.Requirement).filter(
    models.Assignment.is_published == True
).outerjoin(models.Requirement).all()

priority_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `critical_assignments`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (only published assignments)

---

### High Priority (Labeled: "High Priority MAPs")

**Backend:**
```python
# Same query as Critical Priority
# priority_dist["High"]
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `high_assignments`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (only published assignments)

---

### Departments Impacted

**Backend:**
```python
# crud.py Line 312
departments_impacted = db.query(
    func.count(func.distinct(models.Assignment.department_id))
).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `departments_impacted`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (only departments with published assignments)

---

### Upcoming Deadlines

**Backend:**
```python
# crud.py Lines 318-329
from datetime import timedelta
now = datetime.utcnow()
upcoming_limit = now + timedelta(days=30)

upcoming_deadlines = 0
for a, r in assignments:  # Only published assignments
    if a.due_date and a.due_date <= upcoming_limit:
        upcoming_deadlines += 1
```

**API:** `GET /api/admin/dashboard`  
**Response Field:** `upcoming_deadlines`  
**Frontend:** Dashboard.jsx - KPI Card  
**Current Value:** Varies (only assignments with due_date within 30 days)

---

## Assignment Center Metrics

### Total MAPs (Should be: Total Assignments)

**Backend:**
```python
# assignment_center_router.py Lines 25-37
summary = crud.get_unpublished_assignment_summary(db)
total_maps = sum(dept["task_count"] for dept in summary.values())
```

**Where get_unpublished_assignment_summary:**
```python
# crud.py Lines 388-422
assignments = db.query(models.Assignment).filter(
    models.Assignment.is_published == False
).all()

for assignment in assignments:
    dept_id = assignment.department_id
    if dept_id in dept_summary:
        dept_summary[dept_id]["task_count"] += 1
```

**API:** `GET /api/assignment-center/summary`  
**Response Field:** `total_maps`  
**Frontend:** AssignmentCenter.jsx - Summary Card  
**Current Value:** Sum of unpublished assignments across all departments

---

### Department Task Count

**Backend:**
```python
# crud.py Lines 410-420
# For each department:
dept_summary[dept_id]["task_count"] += 1  # per assignment
```

**API:** `GET /api/assignment-center/summary`  
**Response Field:** `departments[i].task_count`  
**Frontend:** AssignmentCenter.jsx - Department Cards  
**Current Value:** Count of unpublished assignments per department

---

## Department Workspace Metrics

### Total Tasks

**Backend:**
```python
# department_workspace_router.py
assignments = db.query(models.Assignment).filter(
    models.Assignment.department_id == current_user.department_id,
    models.Assignment.is_published == True
).all()
```

**API:** `GET /api/departments/workspace/my-tasks`  
**Response Field:** `tasks` (array)  
**Frontend:** DepartmentWorkspace.jsx - Count of tasks array  
**Current Value:** Published assignments for user's department

---

### Completed / Pending

**Frontend Calculation:**
```javascript
// DepartmentWorkspace.jsx
const completedCount = tasks.filter(t => t.status === 'completed').length;
const pendingCount = tasks.length - completedCount;
```

**Source:** Derived from API response in frontend

---

## Department Dashboard (Admin View)

### Assigned / Completed / Remaining

**Backend:**
```python
# crud.py Lines 468-491
assignments = db.query(models.Assignment).filter(
    models.Assignment.department_id == dept.id,
    models.Assignment.is_published == True
).all()

total = len(assignments)
completed = sum(1 for a in assignments if a.status == models.ComplianceStatus.COMPLETED)
remaining = total - completed
```

**API:** `GET /api/assignment-center/admin-summary`  
**Response Field:** `departments[i].{assigned, completed, remaining}`  
**Frontend:** Dashboard.jsx - Department Assignment Status Table  
**Current Value:** Per-department breakdown of published assignments

---

## Pipeline Analysis Session Metrics

**⚠️ ALL SESSION METRICS USE DEMO DATA**

### Requirements Extracted

**Source:**
```javascript
// AnalysisSession.jsx - generateDocumentAnalysis()
const docRequirements = requirementsTaxonomy.filter(r => 
    selectedSources.includes(r.source_document)
);

stats.totalRequirements = docRequirements.length
```

**Frontend:** Pipeline.jsx - Analysis Results  
**Current Value:** Filtered demo JSON requirements

**⚠️ NOT DATABASE DATA**

---

### Generated MAPs

**Source:**
```javascript
// AnalysisSession.jsx
const docMapEntries = [];
for (const m of mapsOutput) {  // Demo JSON
    const detail = mapDetails[m.map_id];
    if (detail && docReqIds.has(detail.source_requirement?.req_id)) {
        docMapEntries.push(m);
    }
}

stats.totalMaps = docMapEntries.length
```

**Frontend:** Pipeline.jsx - Analysis Results  
**Current Value:** Filtered demo JSON "maps"

**⚠️ NOT DATABASE DATA**

---

### Critical MAPs

**Source:**
```javascript
// AnalysisSession.jsx
stats.criticalMaps = docMapEntries.filter(m => m.priority === "Critical").length
```

**Frontend:** Pipeline.jsx - Analysis Results  
**Current Value:** Count from filtered demo JSON

**⚠️ NOT DATABASE DATA**

---

### Departments Impacted

**Source:**
```javascript
// AnalysisSession.jsx
const docDepartments = Object.entries(deptMap).map(...)
stats.departmentsImpacted = docDepartments.length
```

**Frontend:** Pipeline.jsx - Analysis Results  
**Current Value:** Derived from demo JSON MAP department assignments

**⚠️ NOT DATABASE DATA**

---

## Department Risk Page

### Risk Score per Department

**Backend:**
```python
# crud.py Lines 497-555
PRIORITY_WEIGHTS = {"Critical": 40, "High": 20, "Medium": 5, "Low": 1}

for dept in departments:
    assignments = db.query(models.Assignment).filter(
        models.Assignment.department_id == dept.id
    ).all()
    
    priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for a in assignments:
        p = a.priority or req.priority  # Fallback to requirement
        priority_counts[p] += 1
    
    raw_score = sum(priority_counts[k] * PRIORITY_WEIGHTS[k] for k in priority_counts)

# Normalize to 0-100
max_raw = max(d["raw_score"] for d in raw)
risk_score = round(raw_score / max_raw * 100, 1)
```

**API:** `GET /api/assignment-center/department-risk`  
**Response Field:** `[{department, risk_score, ...}]`  
**Frontend:** Departments.jsx - Risk Cards  
**Current Value:** Calculated from all assignments (published + unpublished)

---

## Knowledge Graph Metrics

### Node Counts

**Source:**
```javascript
// Graph.jsx
const counts = {
    circular: graphData.nodes.filter(n => n.data.type === "circular").length,
    requirement: graphData.nodes.filter(n => n.data.type === "requirement").length,
    map: graphData.nodes.filter(n => n.data.type === "map").length,
};
```

**Frontend:** Graph.jsx - Statistics Panel  
**Current Value:** Derived from session graph data (demo-based)

**⚠️ NOT DATABASE DATA**

---

## Requirement Search Metrics

### Total Requirements

**Source:**
```javascript
// Requirements.jsx
import { requirementsTaxonomy } from "../data/demo";

// Display count
{requirementsTaxonomy.length} requirements
```

**Frontend:** Requirements.jsx - Page Subtitle  
**Current Value:** 2941 (demo JSON array length)

**⚠️ NOT DATABASE DATA**

---

### Search Results Count

**Frontend Calculation:**
```javascript
// Requirements.jsx
const results = useMemo(() => {
    const q = query.toLowerCase();
    return requirementsTaxonomy.filter(r =>
        (!q || r.text.toLowerCase().includes(q) || ...) &&
        (!domain || r.domain === domain)
    );
}, [query, domain]);

// Display
{results.length} results
```

**Source:** Filtered demo JSON in frontend

**⚠️ NOT DATABASE DATA**

---

## Summary: Metric Sources

| Metric | Database | Demo JSON | Session | Frontend Calc | Authoritative |
|--------|----------|-----------|---------|---------------|---------------|
| Published Assignments | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| Draft Assignments | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| **Total Requirements** | ❌ | ✅ | ❌ | ❌ | ⚠️ **Demo JSON** |
| Pending Tasks | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| Completed Tasks | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| Critical Priority | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| High Priority | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| Departments Impacted | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| Upcoming Deadlines | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| Assignment Center Total | ✅ | ❌ | ❌ | ❌ | ✅ Database |
| **Session Requirements** | ❌ | ✅ | ✅ | ❌ | ⚠️ **Demo JSON** |
| **Session MAPs** | ❌ | ✅ | ✅ | ❌ | ⚠️ **Demo JSON** |
| **Graph Nodes** | ❌ | ✅ | ✅ | ❌ | ⚠️ **Demo JSON** |
| **Requirement Search** | ❌ | ✅ | ❌ | ✅ | ⚠️ **Demo JSON** |
| Risk Scores | ✅ | ❌ | ❌ | ❌ | ✅ Database |

---

## Critical Issues

1. **Total Requirements** uses demo JSON (2941), not database
2. **Requirement Search** uses demo JSON, newly created requirements invisible
3. **Pipeline Session** uses demo JSON, not actual created records
4. **Knowledge Graph** uses demo JSON, no database persistence

---

## Duplicate Counting Logic

**NONE FOUND** - Each metric has exactly one query source.

The issue is not duplicate logic, but **wrong data sources** (demo JSON vs database).

