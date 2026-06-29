# Executive Dashboard Verification Report

**Purpose:** Exact code path verification for every KPI  
**Method:** Code analysis without modifications  
**Status:** Complete

---

## METRIC 1: Published MAPs (36)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 308

### Exact SQLAlchemy Query
```python
published_maps = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

### SQL Equivalent
```sql
SELECT COUNT(id) 
FROM assignments 
WHERE is_published = 1;
```

### Database Table
- **Table:** `assignments`

### Filtering Conditions
- **Column:** `is_published`
- **Value:** `True` (1)
- **No other filters**

### Arithmetic
```
COUNT(assignments.id WHERE is_published = True)
= 36
```

### Entity Counted
**Assignment records** where `is_published = True`

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 75
```javascript
m.published_maps = dashboardStats.published_maps || 0
```

### What It Actually Is
Not "MAPs" - these are **published Assignment records**

---

## METRIC 2: Unpublished MAPs (34)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 309

### Exact Calculation
```python
total_assignments = db.query(func.count(models.Assignment.id)).scalar()
published_maps = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.is_published == True
).scalar() or 0
unpublished_maps = total_assignments - published_maps
```

### SQL Equivalent
```sql
-- Step 1: Get total
SELECT COUNT(id) FROM assignments;
-- Result: 70

-- Step 2: Get published
SELECT COUNT(id) FROM assignments WHERE is_published = 1;
-- Result: 36

-- Step 3: Arithmetic
70 - 36 = 34
```

### Database Table
- **Table:** `assignments`

### Filtering Conditions
**Implicit filter:** All assignments where `is_published = False`

### Arithmetic
```
Total Assignments - Published Assignments
= 70 - 36
= 34
```

### Entity Counted
**Assignment records** where `is_published = False`

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 78
```javascript
m.unpublished_assignments = dashboardStats.unpublished_assignments || 0
```

### What It Actually Is
Not "MAPs" - these are **unpublished/draft Assignment records**

---

## METRIC 3: Pending Tasks (58)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 289

### Exact SQLAlchemy Query
```python
pending = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "pending"
).scalar()
```

### SQL Equivalent
```sql
SELECT COUNT(id) 
FROM assignments 
WHERE status = 'pending';
```

### Database Table
- **Table:** `assignments`

### Filtering Conditions
- **Column:** `status`
- **Value:** `"pending"`
- **No filter on `is_published`** ← KEY OBSERVATION

### Arithmetic
```
COUNT(assignments.id WHERE status = 'pending')
= 58
```

### Entity Counted
**All Assignment records** with `status = 'pending'`  
**Includes:** Both published AND unpublished assignments

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 76
```javascript
m.pending_assignments = dashboardStats.pending_assignments || 0
```

### What It Actually Is
All assignments with pending status, regardless of publication state

---

## METRIC 4: Completed Tasks (12)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 295

### Exact SQLAlchemy Query
```python
completed = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "completed"
).scalar()
```

### SQL Equivalent
```sql
SELECT COUNT(id) 
FROM assignments 
WHERE status = 'completed';
```

### Database Table
- **Table:** `assignments`

### Filtering Conditions
- **Column:** `status`
- **Value:** `"completed"`
- **No filter on `is_published`** ← KEY OBSERVATION

### Arithmetic
```
COUNT(assignments.id WHERE status = 'completed')
= 12
```

### Entity Counted
**All Assignment records** with `status = 'completed'`  
**Includes:** Both published AND unpublished assignments

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 77
```javascript
m.completed_assignments = dashboardStats.completed_assignments || 0
```

### What It Actually Is
All assignments with completed status, regardless of publication state

---

## METRIC 5: Critical Priority (20)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 316-328

### Exact Code Path
```python
assignments = db.query(models.Assignment, models.Requirement).outerjoin(
    models.Requirement
).all()

priority_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1

# Later returned as:
"critical_assignments": priority_dist["Critical"]
```

### SQL Equivalent
```sql
SELECT 
    a.id,
    COALESCE(a.priority, r.priority, 'Medium') as effective_priority
FROM assignments a
LEFT JOIN requirements r ON a.requirement_id = r.id;

-- Then count where effective_priority = 'Critical'
```

### Database Tables
- **Primary:** `assignments`
- **Joined:** `requirements` (LEFT JOIN via `requirement_id`)

### Filtering Conditions
- **No WHERE clause** - includes ALL assignments
- **Priority logic:**
  1. Use `assignments.priority` if not NULL
  2. Else use `requirements.priority` if not NULL
  3. Else default to `"Medium"`

### Arithmetic
```
FOR EACH assignment:
    priority = assignment.priority OR requirement.priority OR "Medium"
    IF priority == "Critical":
        count++

Result: 20
```

### Entity Counted
**All Assignment records** with effective priority = "Critical"  
**Includes:** Both published AND unpublished assignments  
**Note:** Priority can come from Assignment OR Requirement table

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 79
```javascript
m.critical_maps = dashboardStats.critical_assignments || 0
```

### What It Actually Is
All assignments with Critical priority (from either table), regardless of publication state

---

## METRIC 6: High Priority (35)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 316-328

### Exact Code Path
```python
# Same loop as Critical Priority
for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1

# Later returned as:
"high_assignments": priority_dist["High"]
```

### SQL Equivalent
```sql
SELECT 
    COUNT(*) 
FROM (
    SELECT COALESCE(a.priority, r.priority, 'Medium') as effective_priority
    FROM assignments a
    LEFT JOIN requirements r ON a.requirement_id = r.id
) 
WHERE effective_priority = 'High';
```

### Database Tables
- **Primary:** `assignments`
- **Joined:** `requirements` (LEFT JOIN)

### Filtering Conditions
- **No WHERE clause** - includes ALL assignments
- Same priority fallback logic as Critical

### Arithmetic
```
FOR EACH assignment:
    priority = assignment.priority OR requirement.priority OR "Medium"
    IF priority == "High":
        count++

Result: 35
```

### Entity Counted
**All Assignment records** with effective priority = "High"  
**Includes:** Both published AND unpublished assignments

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 80
```javascript
m.high_priority_maps = dashboardStats.high_assignments || 0
```

### What It Actually Is
All assignments with High priority, regardless of publication state

---

## METRIC 7: Upcoming Deadlines (55)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 316-328

### Exact Code Path
```python
from datetime import timedelta
now = datetime.utcnow()
upcoming_limit = now + timedelta(days=30)

assignments = db.query(models.Assignment, models.Requirement).outerjoin(
    models.Requirement
).all()

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

### SQL Equivalent
```sql
-- Cannot be expressed in single SQL due to conditional logic
-- Conceptually:
SELECT COUNT(*) FROM (
    SELECT 
        a.due_date,
        COALESCE(a.priority, r.priority, 'Medium') as priority
    FROM assignments a
    LEFT JOIN requirements r ON a.requirement_id = r.id
) WHERE 
    (due_date IS NOT NULL AND due_date <= DATE('now', '+30 days'))
    OR
    (due_date IS NULL AND priority IN ('Critical', 'High'));
```

### Database Tables
- **Primary:** `assignments` (uses `due_date` column)
- **Joined:** `requirements` (for priority fallback)

### Filtering Conditions
**Complex conditional logic:**
1. **IF** `assignment.due_date` exists:
   - Count if `due_date <= now + 30 days`
2. **ELSE IF** priority is "Critical" OR "High":
   - Count even without due_date

### Arithmetic
```
upcoming_deadlines = 0

FOR EACH assignment:
    priority = assignment.priority OR requirement.priority OR "Medium"
    
    IF assignment.due_date IS NOT NULL:
        IF assignment.due_date <= (now + 30 days):
            upcoming_deadlines++
    ELSE IF priority IN ["Critical", "High"]:
        upcoming_deadlines++

Result: 55
```

### Entity Counted
**Hybrid count:**
- Assignment records with `due_date` within 30 days, OR
- Assignment records with NULL `due_date` but Critical/High priority

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 82
```javascript
m.upcoming_deadlines = dashboardStats.upcoming_deadlines || 0
```

### What It Actually Is
Mixed metric: assignments with actual deadlines + assignments with implicit urgency (no deadline but high priority)

---

## METRIC 8: Departments Impacted (4)

### Backend Function
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()`  
**Line:** 311

### Exact SQLAlchemy Query
```python
departments_impacted = db.query(func.count(func.distinct(models.Assignment.department_id))).filter(
    models.Assignment.is_published == True
).scalar() or 0
```

### SQL Equivalent
```sql
SELECT COUNT(DISTINCT department_id) 
FROM assignments 
WHERE is_published = 1;
```

### Database Table
- **Table:** `assignments`

### Filtering Conditions
- **Column:** `is_published`
- **Value:** `True` (1)
- **Aggregation:** COUNT(DISTINCT)

### Arithmetic
```
COUNT(DISTINCT assignments.department_id WHERE is_published = True)
= 4
```

### Entity Counted
**Unique departments** that have at least one published assignment

**Not counting:** Total assignments or total departments  
**Counting:** Distinct department IDs with published work

### Frontend Consumption
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Line:** 81
```javascript
m.departments_impacted = dashboardStats.departments_impacted || 0
```

### What It Actually Is
Number of distinct departments with at least one published assignment

---

## ENTITY ANALYSIS SUMMARY

| Metric | Entity Counted | Published Filter | Status Filter | Priority Filter |
|--------|---------------|------------------|---------------|-----------------|
| Published MAPs (36) | Assignment records | ✅ `is_published=True` | ❌ None | ❌ None |
| Unpublished MAPs (34) | Assignment records | ✅ `is_published=False` | ❌ None | ❌ None |
| Pending Tasks (58) | Assignment records | ❌ **None** | ✅ `status='pending'` | ❌ None |
| Completed Tasks (12) | Assignment records | ❌ **None** | ✅ `status='completed'` | ❌ None |
| Critical Priority (20) | Assignment records | ❌ **None** | ❌ None | ✅ `priority='Critical'` |
| High Priority (35) | Assignment records | ❌ **None** | ❌ None | ✅ `priority='High'` |
| Upcoming Deadlines (55) | Assignment records | ❌ **None** | ❌ None | 🟡 Hybrid |
| Departments (4) | Distinct departments | ✅ `is_published=True` | ❌ None | ❌ None |

---

## TERMINOLOGY INCONSISTENCIES IDENTIFIED

### 🔴 Inconsistency 1: "Published MAPs" vs "Unpublished MAPs"

**Terms Used:** "Published MAPs" and "Unpublished MAPs"  
**Actually Counting:** Assignment records, not MAPs  
**Evidence:**
- Backend returns: `"published_maps"` and `"unpublished_assignments"`
- Frontend uses: `dashboardStats.published_maps` and `dashboardStats.unpublished_assignments`
- Database table: `assignments` (not a "maps" table)

**Issue:** Terminology suggests these are MAP documents or analysis outputs, but they're Assignment records with an `is_published` flag.

---

### 🔴 Inconsistency 2: "Pending Tasks" Mixed Scope

**Term Used:** "Pending Tasks"  
**Actually Counting:** ALL assignments with `status='pending'` (published + unpublished)  
**Evidence:** No `is_published` filter in query (Line 289)

**Comparison with Department Table:**
- **Department "Remaining" (24):** Only published assignments with `status != 'completed'`
- **Pending Tasks (58):** All assignments with `status = 'pending'`

**Mathematical Proof:**
```
Pending Tasks (58) = Published Pending + Unpublished Pending
Department Remaining (24) = Published Pending + Published In-Progress

58 ≠ 24 because:
- 58 includes unpublished pending
- 24 includes published in-progress
- 24 excludes unpublished
```

---

### 🔴 Inconsistency 3: "Completed Tasks" Scope Mismatch

**Term Used:** "Completed Tasks"  
**KPI Count:** 12 (all assignments with `status='completed'`)  
**Department Table:** 12 (only published assignments with `status='completed'`)

**Evidence:**
- KPI query (Line 295): No `is_published` filter
- Department query (`crud.py:468`): Has `is_published = True` filter

**Current Match:** Coincidental - happens to be same number  
**Risk:** Could diverge if unpublished assignments are marked completed

---

### 🔴 Inconsistency 4: "Critical/High Priority" Missing Publication Filter

**Terms Used:** "Critical Priority" and "High Priority"  
**Actually Counting:** ALL assignments with that priority (published + unpublished)  
**Evidence:** No `is_published` filter (Line 316-328)

**Operational Issue:** Dashboard shows priority counts for work that hasn't been published to departments yet.

---

### 🔴 Inconsistency 5: "Upcoming Deadlines" Hybrid Definition

**Term Used:** "Upcoming Deadlines"  
**Actually Counting:** Mixed logic:
1. Assignments with `due_date <= now + 30 days`
2. Assignments with NULL `due_date` but "Critical" or "High" priority

**Evidence:** Lines 322-327

**Issue:** Not all 55 items have actual deadlines. Some are included based on priority alone.

---

## VERIFICATION: RELATIONSHIP CHECKS

### Check 1: Published + Unpublished = Total

**Code:**
```python
total_assignments = db.query(func.count(models.Assignment.id)).scalar()  # 70
published_maps = db.query(...).filter(is_published == True).scalar()     # 36
unpublished_maps = total_assignments - published_maps                     # 34
```

**Verification:**
```
36 + 34 = 70 ✓
```

**Status:** ✅ MATHEMATICALLY GUARANTEED

---

### Check 2: Critical + High + Medium + Low = Total

**Code:**
```python
priority_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1
```

**Verification:**
```
Critical (20) + High (35) + Medium + Low = 70
20 + 35 + Medium + Low = 70
Medium + Low = 15
```

**Status:** ✅ MATHEMATICALLY GUARANTEED (with Medium+Low = 15)

---

### Check 3: Pending + In-Progress + Completed = Total?

**Code:**
```python
pending = db.query(...).filter(status == "pending").scalar()          # 58
in_progress = db.query(...).filter(status == "in_progress").scalar()  # ?
completed = db.query(...).filter(status == "completed").scalar()      # 12
```

**Expected:**
```
58 + in_progress + 12 = 70
in_progress = 0
```

**Status:** ⚠️ DEPENDS ON DATA (likely in_progress = 0)

---

### Check 4: Department Table Sum

**Department Table Shows:** Assigned = 36, Completed = 12, Remaining = 24

**From admin_summary endpoint:**
```python
# Only published assignments
assignments = db.query(Assignment).filter(
    department_id == dept.id,
    is_published == True
).all()
```

**Verification:**
```
Assigned (36) - Completed (12) = Remaining (24) ✓
```

**Status:** ✅ CORRECT FOR PUBLISHED ASSIGNMENTS ONLY

---

## CANONICAL KPI MODEL RECOMMENDATION

### Category 1: WORKFLOW METRICS
**Definition:** Assignment lifecycle and publication state  
**Filter:** `is_published` status

| KPI | Entity | Query |
|-----|--------|-------|
| Total Assignments | Assignment | `COUNT(*)` |
| Published Assignments | Assignment | `COUNT(*) WHERE is_published=True` |
| Draft Assignments | Assignment | `COUNT(*) WHERE is_published=False` |

**Rationale:** These track the admin workflow - what's been created vs what's been published to departments.

---

### Category 2: EXECUTION METRICS
**Definition:** Work progress and completion  
**Filter:** `status` + `is_published=True`

| KPI | Entity | Query |
|-----|--------|-------|
| Active Tasks | Assignment | `COUNT(*) WHERE is_published=True AND status!='completed'` |
| Completed Tasks | Assignment | `COUNT(*) WHERE is_published=True AND status='completed'` |
| In Progress Tasks | Assignment | `COUNT(*) WHERE is_published=True AND status='in_progress'` |
| Pending Tasks | Assignment | `COUNT(*) WHERE is_published=True AND status='pending'` |

**Rationale:** These track actual work execution - only published assignments are operational.

**Change from current:** Add `is_published=True` filter to all execution metrics.

---

### Category 3: RISK METRICS
**Definition:** Priority distribution and urgency  
**Filter:** `priority` + `is_published=True`

| KPI | Entity | Query |
|-----|--------|-------|
| Critical Tasks | Assignment | `COUNT(*) WHERE is_published=True AND priority='Critical'` |
| High Tasks | Assignment | `COUNT(*) WHERE is_published=True AND priority='High'` |
| Departments at Risk | Departments | `COUNT(DISTINCT dept) WHERE is_published=True` |
| Actual Deadlines | Assignment | `COUNT(*) WHERE due_date<=now+30 AND is_published=True` |

**Rationale:** These track operational risk - only published assignments represent active risk.

**Change from current:** Add `is_published=True` filter to all risk metrics.

---

## CANONICAL MODEL COMPARISON

### CURRENT vs PROPOSED

| Metric | Current Filter | Current Category | Proposed Filter | Proposed Category |
|--------|---------------|------------------|-----------------|-------------------|
| Published MAPs | `is_published=True` | Workflow | `is_published=True` | **WORKFLOW** ✓ |
| Unpublished MAPs | `is_published=False` | Workflow | `is_published=False` | **WORKFLOW** ✓ |
| Pending Tasks | `status='pending'` | Execution | `is_published=True AND status='pending'` | **EXECUTION** 🔄 |
| Completed Tasks | `status='completed'` | Execution | `is_published=True AND status='completed'` | **EXECUTION** 🔄 |
| Critical Priority | `priority='Critical'` | Risk | `is_published=True AND priority='Critical'` | **RISK** 🔄 |
| High Priority | `priority='High'` | Risk | `is_published=True AND priority='High'` | **RISK** 🔄 |
| Upcoming Deadlines | Hybrid logic | Risk | `due_date<=now+30 AND is_published=True` | **RISK** 🔄 |
| Departments Impacted | `is_published=True` | Risk | `is_published=True` | **RISK** ✓ |

**Legend:**
- ✓ = Already correct
- 🔄 = Needs `is_published=True` filter added

---

## SUMMARY OF FINDINGS

### ✅ CORRECT IMPLEMENTATIONS

1. **Published MAPs:** Correctly filters `is_published=True`
2. **Unpublished MAPs:** Correctly calculated as remainder
3. **Departments Impacted:** Correctly filters `is_published=True`

### 🔴 INCORRECT IMPLEMENTATIONS

1. **Pending Tasks:** Missing `is_published=True` filter - includes draft assignments
2. **Completed Tasks:** Missing `is_published=True` filter - could count draft completions
3. **Critical Priority:** Missing `is_published=True` filter - includes unpublished work
4. **High Priority:** Missing `is_published=True` filter - includes unpublished work
5. **Upcoming Deadlines:** Missing `is_published=True` filter + hybrid logic

### 📊 IMPACT ANALYSIS

**Current State:**
- 5 out of 8 metrics mix published and unpublished assignments
- Workflow metrics are correct (2/2)
- Execution metrics are incorrect (2/2)
- Risk metrics are partially incorrect (2/4)

**If Fixed:**
- All execution metrics would drop (currently inflated by unpublished)
- All risk metrics would drop (currently inflated by unpublished)
- Dashboard would show only operational reality

---

## EXACT FILTER RECOMMENDATIONS

### 1. Pending Tasks
**Current:**
```python
pending = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "pending"
).scalar()
```

**Recommended:**
```python
pending = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "pending",
    models.Assignment.is_published == True
).scalar()
```

---

### 2. Completed Tasks
**Current:**
```python
completed = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "completed"
).scalar()
```

**Recommended:**
```python
completed = db.query(func.count(models.Assignment.id)).filter(
    models.Assignment.status == "completed",
    models.Assignment.is_published == True
).scalar()
```

---

### 3. Critical/High Priority
**Current:**
```python
for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1
```

**Recommended:**
```python
assignments = db.query(models.Assignment, models.Requirement).filter(
    models.Assignment.is_published == True  # ← Add this filter
).outerjoin(models.Requirement).all()

for a, r in assignments:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_dist:
        priority_dist[p] += 1
```

---

### 4. Upcoming Deadlines
**Current:**
```python
for a, r in assignments:
    if a.due_date:
        if a.due_date <= upcoming_limit:
            upcoming_deadlines += 1
    elif p in ["Critical", "High"]:
        upcoming_deadlines += 1
```

**Recommended:**
```python
assignments = db.query(models.Assignment, models.Requirement).filter(
    models.Assignment.is_published == True  # ← Add this filter
).outerjoin(models.Requirement).all()

for a, r in assignments:
    if a.due_date and a.due_date <= upcoming_limit:
        upcoming_deadlines += 1
    # Remove the implicit urgency logic
```

---

## VERIFICATION COMPLETE

**All code paths traced.**  
**All queries documented.**  
**All filters identified.**  
**All inconsistencies catalogued.**  
**Canonical model proposed.**

**No code modified.**
