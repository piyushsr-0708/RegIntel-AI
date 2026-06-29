# Executive Dashboard Verification - Summary

**Status:** Complete code path analysis  
**Files Modified:** ZERO  
**Method:** Exact query tracing

---

## QUICK REFERENCE TABLE

| Metric | Value | Counts | Filter | Category |
|--------|-------|--------|--------|----------|
| Published MAPs | 36 | Assignment records | `is_published=True` | ✅ Workflow |
| Unpublished MAPs | 34 | Assignment records | `is_published=False` | ✅ Workflow |
| Pending Tasks | 58 | Assignment records | `status='pending'` **NO** `is_published` | 🔴 Execution |
| Completed Tasks | 12 | Assignment records | `status='completed'` **NO** `is_published` | 🔴 Execution |
| Critical Priority | 20 | Assignment records | `priority='Critical'` **NO** `is_published` | 🔴 Risk |
| High Priority | 35 | Assignment records | `priority='High'` **NO** `is_published` | 🔴 Risk |
| Upcoming Deadlines | 55 | Assignment records | Hybrid logic **NO** `is_published` | 🔴 Risk |
| Departments | 4 | Distinct departments | `is_published=True` | ✅ Risk |

---

## KEY FINDINGS

### ✅ CORRECT (2/8)
- Published MAPs: Correctly filters published assignments
- Departments Impacted: Correctly filters published assignments

### 🔴 INCORRECT (5/8)
- Pending Tasks: Missing `is_published=True` filter
- Completed Tasks: Missing `is_published=True` filter
- Critical Priority: Missing `is_published=True` filter
- High Priority: Missing `is_published=True` filter
- Upcoming Deadlines: Missing `is_published=True` filter + hybrid logic

### 🟡 TERMINOLOGY (1/8)
- Unpublished MAPs: Calculated correctly but misleading name

---

## ENTITY VERIFICATION

**ALL 8 METRICS COUNT THE SAME ENTITY:** `assignments` table records

**NONE count:**
- ❌ Requirements
- ❌ MAPs (no such table exists)
- ❌ Documents

**Terminology Issue:** "MAPs" in KPI labels refers to Assignment records, not MAP documents.

---

## CANONICAL MODEL

### WORKFLOW (Publication State)
- Total Assignments: 70
- Published: 36 (`is_published=True`)
- Draft: 34 (`is_published=False`)

### EXECUTION (Work Progress) - PROPOSED
- Active Tasks: ? (`is_published=True AND status!='completed'`)
- Completed: ? (`is_published=True AND status='completed'`)
- Pending: ? (`is_published=True AND status='pending'`)

### RISK (Priority & Urgency) - PROPOSED
- Critical: ? (`is_published=True AND priority='Critical'`)
- High: ? (`is_published=True AND priority='High'`)
- Departments: 4 (`is_published=True`)
- Deadlines: ? (`is_published=True AND due_date<=now+30`)

---

## EXACT CODE LOCATIONS

### Backend
**File:** `backend/crud.py`  
**Function:** `get_dashboard_summary()` (Line 274-337)

### Frontend
**File:** `frontend/dashboard/src/pages/Dashboard.jsx`  
**Data fetch:** Line 62 (`api.get('/admin/dashboard')`)  
**Consumption:** Lines 75-82

### API Endpoint
**Route:** `GET /api/admin/dashboard`  
**File:** `backend/routers/admin_router.py` (likely)

---

## RECOMMENDED FIX (NOT APPLIED)

Add `.filter(models.Assignment.is_published == True)` to 5 queries:

1. **Line 289:** Pending Tasks
2. **Line 295:** Completed Tasks  
3. **Line 316:** Priority distribution query
4. **Line 323-327:** Upcoming deadlines logic

**Impact:** All execution and risk metrics would decrease to show only operational reality.

---

**Full details in `EXECUTIVE_DASHBOARD_VERIFICATION.md`**
