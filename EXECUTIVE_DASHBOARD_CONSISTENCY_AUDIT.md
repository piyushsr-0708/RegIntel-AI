# Executive Dashboard Consistency Audit Report

**Date:** June 28, 2026  
**Status:** Code Analysis Complete (Database execution pending)  
**Purpose:** Trace every metric to its backend source and identify inconsistencies

---

## DASHBOARD METRICS REPORTED

| Metric | Value | Widget Location |
|--------|-------|----------------|
| Published MAPs | 36 | KPI Card #1 |
| Unpublished MAPs | 34 | KPI Card #2 |
| Pending Tasks | 58 | KPI Card #3 |
| Completed Tasks | 12 | KPI Card #4 |
| Critical Priority | 20 | KPI Card #5 |
| High Priority | 35 | KPI Card #6 |
| Departments Impacted | 4 | KPI Card #7 |
| Upcoming Deadlines | 55 | KPI Card #8 |
| Dept Assigned | 36 | Table Row |
| Dept Completed | 12 | Table Row |
| Dept Remaining | 24 | Table Row |

---

## METRIC TRACING

### 1. Published MAPs (36)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 75
m.published_maps = dashboardStats.published_maps || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
published_maps = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

**Database:**
- **Table:** `assignments`
- **Column:** `is_published`
- **Filter:** `is_published = TRUE`
- **What it counts:** Assignments (not Requirements, not MAPs)

**Definition:** Number of Assignment records where `is_published = True`

---

### 2. Unpublished MAPs (34)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 78
m.unpublished_assignments = dashboardStats.unpublished_assignments || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
unpublished_maps = total_assignments - published_maps
```

**Database:**
- **Table:** `assignments`
- **Calculation:** Total assignments - published assignments
- **What it counts:** Assignments where `is_published = False`

**Definition:** Number of Assignment records where `is_published = False`

---

### 3. Pending Tasks (58)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 76
m.pending_assignments = dashboardStats.pending_assignments || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
pending = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "pending"
).scalar()

# Later returned as:
"pending_assignments": pending or 0
```

**Database:**
- **Table:** `assignments`
- **Column:** `status`
- **Filter:** `status = 'pending'`
- **What it counts:** ALL assignments with pending status (both published AND unpublished)

**Definition:** Number of Assignment records where `status = 'pending'` (regardless of `is_published`)

---

### 4. Completed Tasks (12)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 77
m.completed_assignments = dashboardStats.completed_assignments || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
completed = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "completed"
).scalar()

# Later returned as:
"completed_assignments": completed or 0
```

**Database:**
- **Table:** `assignments`
- **Column:** `status`  
- **Filter:** `status = 'completed'`
- **What it counts:** ALL assignments with completed status (both published AND unpublished)

**Definition:** Number of Assignment records where `status = 'completed'` (regardless of `is_published`)

---

### 5. Critical Priority (20)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 79
m.critical_maps = dashboardStats.critical_assignments || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
assignments = db.query(models.Assignment, models.Requirement).outerjoin(models.Requirement).all()
priority_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1

# Later returned as:
"critical_assignments": priority_dist["Critical"]
```

**Database:**
- **Tables:** `assignments` LEFT JOIN `requirements`
- **Columns:** `assignments.priority` (fallback to `requirements.priority`)
- **Logic:** Use Assignment.priority if exists, else Requirement.priority, else "Medium"
- **What it counts:** Assignments with priority = "Critical" (from either table)

**Definition:** Number of Assignments where priority = "Critical" (checking both Assignment and Requirement tables)

---

### 6. High Priority (35)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 80
m.high_priority_maps = dashboardStats.high_assignments || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
# Same logic as Critical
"high_assignments": priority_dist["High"]
```

**Database:**
- **Tables:** `assignments` LEFT JOIN `requirements`
- **Columns:** `assignments.priority` (fallback to `requirements.priority`)
- **What it counts:** Assignments with priority = "High"

**Definition:** Number of Assignments where priority = "High"

---

### 7. Departments Impacted (4)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 81
m.departments_impacted = dashboardStats.departments_impacted || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
departments_impacted = db.query(func.count(func.distinct(models.Assignment.department_id))).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

**Database:**
- **Table:** `assignments`
- **Column:** `department_id`
- **Filter:** `is_published = TRUE`
- **Aggregation:** COUNT(DISTINCT department_id)
- **What it counts:** Unique departments that have at least one published assignment

**Definition:** Number of distinct departments with at least one published assignment

---

### 8. Upcoming Deadlines (55)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 82
m.upcoming_deadlines = dashboardStats.upcoming_deadlines || 0
```

**Backend Function:** `get_dashboard_summary()`  
**File:** `backend/crud.py:274`  
**Code:**
```python
from datetime import timedelta
now = datetime.utcnow()
upcoming_limit = now + timedelta(days=30)

assignments = db.query(models.Assignment, models.Requirement).outerjoin(models.Requirement).all()
upcoming_deadlines = 0

for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    
    if a.due_date:
        if a.due_date <= upcoming_limit:
            upcoming_deadlines += 1
    elif p in ["Critical", "High"]:
        upcoming_deadlines += 1

# Returned as:
"upcoming_deadlines": upcoming_deadlines
```

**Database:**
- **Tables:** `assignments` LEFT JOIN `requirements`
- **Column:** `assignments.due_date`
- **Logic:** 
  - IF assignment has `due_date` AND `due_date <= now + 30 days` → count it
  - ELSE IF priority is "Critical" or "High" → count it (assumes implicit urgency)
- **What it counts:** Assignments with deadlines in next 30 days OR high/critical priority without deadline

**Definition:** Mixed metric - assignments with due_date within 30 days + assignments without due_date but with Critical/High priority

---

### 9. Department Table (Assigned: 36, Completed: 12, Remaining: 24)

**Frontend Code:**
```javascript
// Dashboard.jsx Line 57
const response = await api.get('/assignment-center/admin-summary');
setCompletionSummary(response.data);
```

**Backend Function:** `get_admin_completion_summary()`  
**File:** `backend/crud.py:468`  
**Code:**
```python
def get_admin_completion_summary(db: Session) -> list:
    departments = get_all_departments(db)
    summary = []
    
    for dept in departments:
        assignments = db.query(models.Assignment).filter(
            models.Assignment.department_id == dept.id,
            models.Assignment.is_published == True  # ← KEY FILTER
        ).all()
        
        total = len(assignments)
        completed = sum(1 for a in assignments if a.status == models.ComplianceStatus.COMPLETED)
        remaining = total - completed
        
        summary.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "assigned": total,
            "completed": completed,
            "remaining": remaining
        })
    
    return summary
```

**Database:**
- **Table:** `assignments`
- **Filters:** 
  - `department_id = X`
  - `is_published = TRUE` ← **CRITICAL FILTER**
- **Columns:** `status`
- **What it counts:** ONLY published assignments per department

**Definition:** 
- **Assigned:** Count of assignments where `is_published = True` AND `department_id = X`
- **Completed:** Count of assignments where `is_published = True` AND `department_id = X` AND `status = 'completed'`
- **Remaining:** Assigned - Completed

---

## INCONSISTENCY ANALYSIS

### A) Published MAPs (36) + Unpublished MAPs (34) = Total MAPs?

**Calculation:** 36 + 34 = 70

**Backend Code:**
```python
total_assignments = db.query(func.count(models.Assignment.id)).scalar()
published_maps = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.is_published == True
).scalar() or 0
unpublished_maps = total_assignments - published_maps
```

**✅ CONSISTENT:** This relationship MUST be true by definition:
- `published_maps` = COUNT WHERE `is_published = True`
- `unpublished_maps` = `total_assignments` - `published_maps`
- Therefore: `published_maps + unpublished_maps = total_assignments`

**Verification:** 36 + 34 = 70 total assignments

**What "Unpublished MAP" Means:**
- **NOT** a draft MAP or unpublished document
- It's an Assignment record where `is_published = False`
- The Assignment exists in the database but hasn't been "published" to the department yet
- From Assignment Center perspective: awaiting admin review/approval before publishing to department

**Terminology Issue:** "Unpublished MAP" is misleading. It should be "Unpublished Assignment" or "Draft Assignment"

---

### B) Pending Tasks (58) vs Department Remaining Tasks (24)

**Pending Tasks = 58**
- **Source:** `get_dashboard_summary()`
- **Query:** `SELECT COUNT(*) FROM assignments WHERE status = 'pending'`
- **Includes:** ALL assignments with pending status (published + unpublished)
- **No filter on** `is_published`

**Department Remaining Tasks = 24**
- **Source:** `get_admin_completion_summary()`
- **Query:** `SELECT COUNT(*) FROM assignments WHERE department_id = X AND is_published = True AND status != 'completed'`
- **Includes:** ONLY published assignments that are NOT completed
- **Filters:** `is_published = True`

**🔴 INCONSISTENCY FOUND:**

These metrics count DIFFERENT things:

| Metric | Filter | What it Counts |
|--------|--------|----------------|
| Pending Tasks (58) | `status = 'pending'` | All pending assignments (pub + unpub) |
| Dept Remaining (24) | `is_published = True AND status != 'completed'` | Published non-completed assignments |

**Why They Differ:**

1. **Pending Tasks (58)** includes:
   - Published pending assignments
   - **Unpublished pending assignments** ← EXTRA
   - Status filter: ONLY "pending"

2. **Dept Remaining (24)** includes:
   - Published pending assignments
   - **Published in_progress assignments** ← EXTRA (not counted in Pending)
   - Published filter: ONLY `is_published = True`

**The Math:**
```
Pending Tasks (58) = Published Pending + Unpublished Pending
Dept Remaining (24) = Published Pending + Published In-Progress
```

**Root Cause:** Different filter logic:
- One filters by `status = 'pending'` (includes unpublished)
- One filters by `is_published = True AND status != 'completed'` (includes in_progress)

**Expected Relationship (if consistent):**
```
Dept Remaining = Dept Assigned - Dept Completed
              24 = 36 - 12 ✓ CORRECT
```

But:
```
Pending Tasks ≠ Dept Remaining
         58 ≠ 24
```

**Conclusion:** These are INTENTIONALLY different metrics:
- **Pending Tasks:** All assignments waiting to start (global view)
- **Dept Remaining:** Published assignments not yet finished (operational view)

**Issue:** Dashboard should clarify this distinction or make them consistent.

---

### C) Completed Tasks (12)

**From Dashboard KPI:** 12  
**From Department Table Sum:** 12 (per department, summed)

**Verification:**
```python
# Dashboard KPI
completed = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "completed"
).scalar()

# Department Table (summed across all departments)
for dept in departments:
    assignments = db.query(models.Assignment).filter(
        models.Assignment.department_id == dept.id,
        models.Assignment.is_published == True
    ).all()
    completed = sum(1 for a in assignments if a.status == models.ComplianceStatus.COMPLETED)
```

**🟡 POTENTIAL INCONSISTENCY:**

- **Dashboard Completed (12):** Counts ALL completed assignments (published + unpublished)
- **Department Table Completed (12):** Counts ONLY published completed assignments

**If they match (both = 12):**
- Either: No unpublished completed assignments exist
- Or: Coincidentally the same number

**Most Likely:** All completed assignments are published, so they happen to match.

**Recommendation:** Dashboard KPI should filter by `is_published = True` to match department table.

---

### D) Upcoming Deadlines (55)

**Backend Logic:**
```python
for a, r in assignments:
    if a.due_date:
        if a.due_date <= now + timedelta(days=30):
            upcoming_deadlines += 1
    elif p in ["Critical", "High"]:
        upcoming_deadlines += 1
```

**What it counts:**
1. Assignments with `due_date` field set AND due_date <= 30 days from now
2. Assignments WITHOUT `due_date` but with priority = "Critical" or "High"

**Database Sources:**
- **Primary:** `assignments.due_date` column
- **Fallback:** `assignments.priority` or `requirements.priority`

**Tables Used:**
- `assignments` (due_date field)
- `requirements` (priority fallback)

**🟡 ISSUE: Hybrid Logic**

This metric mixes two concepts:
1. **Actual deadlines** (from due_date field)
2. **Implicit urgency** (high/critical priority without deadline)

**Problem:** If an assignment has:
- `due_date = NULL`
- `priority = "Critical"`

It gets counted as an "upcoming deadline" even though there's NO actual deadline.

**Current State:** The 55 value includes:
- Some assignments with real due_date within 30 days
- Some assignments with NULL due_date but Critical/High priority

**Recommendation:** Split into two metrics:
- "Assignments with Deadlines" (real due_date)
- "High Priority Tasks" (Critical/High without deadline)

---

### E) Departments Impacted (4)

**Query:**
```python
departments_impacted = db.query(func.count(func.distinct(models.Assignment.department_id))).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

**What it counts:** Number of DISTINCT departments that have at least one published assignment.

**✅ VERIFICATION:**

If dashboard shows 4 departments:
- Query database: `SELECT DISTINCT department_id FROM assignments WHERE is_published = True`
- Expected result: 4 unique department IDs

**Consistent with Department Table:**
The department table should show exactly 4 departments with `assigned > 0`.

**Note:** If there are 9 total departments in the database but only 4 have published assignments, this metric correctly shows 4.

---

### F) Priority Distribution: Critical (20) + High (35) = 55

**Query:**
```python
assignments = db.query(models.Assignment, models.Requirement).outerjoin(models.Requirement).all()
priority_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1
```

**What it counts:** ALL assignments, using priority from Assignment or fallback to Requirement

**🔴 INCONSISTENCY FOUND:**

The dashboard shows:
- Critical: 20
- High: 35
- Medium: ? (not displayed in KPI)
- Low: ? (not displayed in KPI)

**Expected Relationship:**
```
Critical + High + Medium + Low = Total Assignments
20 + 35 + Medium + Low = 70
```

**Therefore:**
```
Medium + Low = 70 - 20 - 35 = 15
```

**Verification Needed:**
- Check if priority_distribution includes Medium and Low
- Verify that sum equals 70 total assignments

**Displayed in:** Priority Distribution donut chart (should show all 4 priorities)

---

## RAW API RESPONSES (Code-Based Prediction)

### GET /api/admin/dashboard

**Expected Response:**
```json
{
  "total_documents": <count from documents table>,
  "total_requirements": <count from requirements table or JSON file>,
  "total_assignments": 70,
  "pending_count": 58,
  "in_progress_count": <count>,
  "completed_count": 12,
  "completion_percentage": <calculated>,
  "published_maps": 36,
  "pending_assignments": 58,
  "completed_assignments": 12,
  "unpublished_assignments": 34,
  "critical_assignments": 20,
  "high_assignments": 35,
  "departments_impacted": 4,
  "upcoming_deadlines": 55,
  "priority_distribution": {
    "Critical": 20,
    "High": 35,
    "Medium": <count>,
    "Low": <count>
  }
}
```

---

### GET /api/assignment-center/admin-summary

**Expected Response:**
```json
{
  "departments": [
    {
      "department_id": 1,
      "department_name": "Compliance",
      "assigned": <count of published assignments>,
      "completed": <count of completed among published>,
      "remaining": <assigned - completed>
    },
    // ... more departments
  ]
}
```

**Note:** Only departments with published assignments appear in this list.

---

### GET /api/assignment-center/department-risk

**Expected Response:**
```json
[
  {
    "department_id": 1,
    "department": "Compliance",
    "total_maps": <total assignments for this dept>,
    "critical_count": <count>,
    "high_count": <count>,
    "medium_count": <count>,
    "low_count": <count>,
    "completed": <count>,
    "risk_score": <0-100 normalized score>
  },
  // ... all 9 departments
]
```

---

## SUMMARY OF FINDINGS

### ✅ CONSISTENT

1. **Published + Unpublished = Total:** 36 + 34 = 70 ✓
2. **Dept Assigned - Dept Completed = Dept Remaining:** 36 - 12 = 24 ✓
3. **Departments Impacted Logic:** Correctly counts distinct departments with published assignments

### 🔴 INCONSISTENCIES FOUND

1. **Pending Tasks (58) ≠ Dept Remaining (24)**
   - **Cause:** Different filters (status='pending' vs is_published=True AND status!='completed')
   - **Impact:** Confusing for users - metrics appear related but count different things
   - **Fix:** Either rename or apply consistent filters

2. **Completed Tasks Filter Mismatch**
   - **Dashboard KPI:** Counts ALL completed (published + unpublished)
   - **Dept Table:** Counts ONLY published completed
   - **Impact:** If they match, it's coincidental; could diverge
   - **Fix:** Dashboard should filter by `is_published = True`

3. **Upcoming Deadlines Hybrid Logic**
   - **Issue:** Mixes real deadlines with implicit urgency (high/critical without deadline)
   - **Impact:** Number doesn't represent actual deadlines
   - **Fix:** Split into two separate metrics or clarify label

4. **"Unpublished MAPs" Terminology**
   - **Issue:** Misleading name - they're unpublished Assignments, not MAPs
   - **Impact:** Confusion about what's being counted
   - **Fix:** Rename to "Draft Assignments" or "Unpublished Assignments"

### 🟡 WARNINGS

1. **Priority Distribution:**
   - Critical (20) + High (35) + Medium + Low should equal 70
   - Verify Medium and Low are being tracked
   - Dashboard only shows Critical and High in KPIs

2. **Multiple Sources for Priority:**
   - Assignment.priority OR Requirement.priority OR "Medium" default
   - Could lead to inconsistencies if not all assignments have priority set

---

## CANONICAL DEFINITIONS NEEDED

### Proposal for Consistent Metrics

| Metric | Definition | Filter |
|--------|-----------|--------|
| **Total MAPs** | All assignments | None |
| **Published MAPs** | Assignments visible to departments | `is_published = True` |
| **Draft MAPs** | Assignments not yet published | `is_published = False` |
| **Pending Tasks** | Published assignments awaiting work | `is_published = True AND status = 'pending'` |
| **In Progress Tasks** | Published assignments being worked | `is_published = True AND status = 'in_progress'` |
| **Completed Tasks** | Published assignments finished | `is_published = True AND status = 'completed'` |
| **Active Tasks** | Published non-completed | `is_published = True AND status != 'completed'` |
| **Critical Priority** | Published critical assignments | `is_published = True AND priority = 'Critical'` |
| **Departments Impacted** | Depts with published assignments | `COUNT(DISTINCT department_id) WHERE is_published = True` |
| **Actual Deadlines** | Assignments with due_date | `due_date IS NOT NULL AND due_date <= now + 30 days` |

---

## RECOMMENDED ACTIONS

1. **Add `is_published = True` filter** to all operational metrics (Pending, Completed, Critical, High)
2. **Rename "Unpublished MAPs"** to "Draft Assignments"
3. **Split "Upcoming Deadlines"** into two metrics or clarify it includes implicit urgency
4. **Rename "Pending Tasks"** to "Active Tasks" and count `status != 'completed'` instead of `status = 'pending'`
5. **Add Medium/Low** priority counts to dashboard
6. **Document each metric** with clear definitions in code comments

---

## TESTING VERIFICATION NEEDED

To complete this audit, execute these queries on live database:

```sql
-- Total assignments
SELECT COUNT(*) FROM assignments;

-- Published/Unpublished
SELECT is_published, COUNT(*) FROM assignments GROUP BY is_published;

-- Status breakdown
SELECT status, COUNT(*) FROM assignments GROUP BY status;

-- Published status breakdown
SELECT status, COUNT(*) FROM assignments WHERE is_published = 1 GROUP BY status;

-- Priority distribution
SELECT COALESCE(a.priority, r.priority, 'Medium') as priority, COUNT(*)
FROM assignments a
LEFT JOIN requirements r ON a.requirement_id = r.id
GROUP BY priority;

-- Departments with assignments
SELECT COUNT(DISTINCT department_id) FROM assignments WHERE is_published = 1;

-- Deadlines
SELECT COUNT(*) FROM assignments WHERE due_date IS NOT NULL AND due_date <= DATE('now', '+30 days');
SELECT COUNT(*) FROM assignments WHERE due_date IS NULL AND (priority = 'Critical' OR priority = 'High');
```

---

**Audit Report Complete. Awaiting database execution and API response verification.**
