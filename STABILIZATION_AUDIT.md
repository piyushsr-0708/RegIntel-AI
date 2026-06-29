# Stabilization Audit Report

**Date:** June 28, 2026  
**Purpose:** Identify root causes of inconsistencies and bugs in the working application

---

## ISSUE 1: Pipeline Exit Lifecycle (CRITICAL)

### Current Behavior
- After exiting analysis session via "✕ Exit Analysis" button
- Dashboard correctly shows: Published = 0, Draft = 205
- **BUT** Assignment Center still displays 34 draft assignments from exited session
- **INCONSISTENT APPLICATION STATE**

### Root Cause Analysis

**Traced Execution Flow:**

1. **Pipeline.jsx (Line 332):** `resetSession()` called on "Exit Analysis"
2. **AnalysisSession.jsx (Line 185):** `resetSession` → `setSession(null)`
3. **Dashboard.jsx:** Correctly switches from session mode to global mode
4. **Assignment Center:** Still uses frontend demo data fallback

**Key Finding:**
```javascript
// AnalysisSession.jsx - Session is only CLIENT-SIDE state
const [session, setSession] = useState(null);

// When resetSession() is called:
resetSession = () => setSession(null)  // Only clears React state

// Backend assignments REMAIN in database with is_published = False
```

**The Codebase Model:** **OPTION B** (Preserve Session)

Evidence:
1. `Assignment` table has persistent `is_published` flag
2. Pipeline creates REAL database assignments (backend/routers/admin_router.py)
3. No cleanup logic exists in exit flow
4. AssignmentCenter fetches from `GET /assignment-center/summary` which queries database

### Current Inconsistency

**Problem:** Application mixes two behaviors:
- Dashboard: Uses strict backend API when session cleared
- Assignment Center: Falls back to demo.js when API returns empty (incorrect)

### Affected Files
- `frontend/dashboard/src/context/AnalysisSession.jsx` - Session lifecycle
- `frontend/dashboard/src/pages/Pipeline.jsx` - Exit button
- `frontend/dashboard/src/pages/AssignmentCenter.jsx` - Data fetching
- `backend/routers/assignment_center_router.py` - Summary endpoint

### Root Cause
**Assignment Center does NOT properly handle empty state.** When API returns 0 departments with tasks, the component should display "No assignments to review" instead of falling back to demo data.

### Proposed Minimal Fix

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`

**Change:** Remove demo.js fallback, trust backend API exclusively.

```javascript
// Current (WRONG):
import { assignmentCenterData } from '../data/demo';  // REMOVE THIS
// Falls back to demo when API empty

// Fixed:
// Only use API data
// If empty, show "No assignments" message
```

**No backend changes needed.** The backend already returns correct empty state.

---

## ISSUE 2: 5500% Confidence Score

### Current Behavior
- MapDetail.jsx displays confidence as `5500%`
- Impossible value (must be 0-100%)

### Root Cause Analysis

**Traced Data Flow:**

1. **demo.js:** Department confidence stored as decimal (0.91 = 91%)
2. **MapDetail.jsx (Line 117):**
   ```javascript
   {(data.department.confidence * 100).toFixed(0)}%
   ```
   This multiplies by 100 correctly for demo data

3. **Backend models.py:** NO confidence field in Assignment table
4. **Backend returns:** Confidence comes from mapDetails demo JSON

**The Bug:** Data stored in demo.js has inconsistent format

**Inspection of demo.js:**
```javascript
// Some entries:
department: { name: "Compliance", confidence: 0.91, ... }  // Decimal (correct)

// Other entries (legacy):
department: { name: "AML", confidence: 55, ... }  // Already percentage (wrong)
```

### Affected Files
- `frontend/dashboard/src/data/demo.js` - Inconsistent data
- `frontend/dashboard/src/pages/MapDetail.jsx` - Displays confidence

### Root Cause
**Demo data has mixed formats:** Some confidence values are decimals (0-1), others are already percentages (0-100). When frontend multiplies by 100, values like `55` become `5500%`.

### Proposed Minimal Fix

**File:** `frontend/dashboard/src/data/demo.js`

**Change:** Normalize ALL confidence values to decimal format (0-1)

Find all entries with `confidence > 1` and divide by 100:
```javascript
// Before: confidence: 55
// After:  confidence: 0.55
```

**Alternative Fix (safer):** Add defensive code in MapDetail.jsx:
```javascript
// Normalize confidence to 0-1 range
const confidenceValue = data.department.confidence > 1 
  ? data.department.confidence / 100 
  : data.department.confidence;

// Display
{(confidenceValue * 100).toFixed(0)}%
```

---

## ISSUE 3: Full Text Retrieval Failures

### Current Behavior
- Requirement Search: Shows truncated text (fixed in previous work)
- Graph View: "Failed to load full text" error
- Assignment Center: Sometimes shows excerpts

### Root Cause Analysis

**Traced Data Flow:**

1. **Requirements.jsx:** ✅ WORKING - Uses demo data directly (full text available)
2. **Graph.jsx (Line 195-215):** Attempts API calls but fails:
   ```javascript
   // For requirements:
   await api.get(`/departments/requirements/${sel.id}`)  // sel.id = "REQ-XXXX"
   
   // For MAPs:
   await api.get(`/admin/assignments/${sel.id}`)  // sel.id = "MAP-XXXX"
   ```

3. **Backend Issue:**
   - `GET /departments/requirements/{requirement_id}` expects **INTEGER ID**
   - Graph nodes use **STRING IDs** like "REQ_41YC0107_0022"
   - **Type mismatch causes 404 errors**

### Affected Files
- `frontend/dashboard/src/pages/Graph.jsx` - API calls with wrong ID format
- `backend/routers/department_workspace_router.py` - Endpoint expects integer
- `backend/routers/admin_router.py` - Assignment endpoint expects integer

### Root Cause
**ID Format Mismatch:** 
- Graph uses semantic IDs (e.g., "REQ_41YC0107_0022")
- Database uses auto-increment integer IDs (1, 2, 3, ...)
- No mapping between them

### Proposed Minimal Fix

**Option A:** Graph should NOT call backend (session is demo-only)
- Graph is populated from AnalysisSession (demo data)
- When clicking nodes, use demo data directly
- No API calls needed

**Option B:** Add endpoint to query by semantic ID
- Create `GET /departments/requirements/by-code/{requirement_id}`
- Query: `WHERE requirement_id = 'REQ_41YC0107_0022'`

**RECOMMENDATION:** **Option A** (minimal change)

**File:** `frontend/dashboard/src/pages/Graph.jsx`

**Change:** Use session data directly instead of API calls

```javascript
// Current (WRONG):
const response = await api.get(`/departments/requirements/${sel.id}`);

// Fixed:
// Find requirement in session.analysis.requirements
const requirement = session?.analysis?.requirements?.find(r => r.req_id === sel.id);
if (requirement) {
  setSelectedNodeData(requirement);
  setShowFullText(true);
}
```

---

## ISSUE 4: Dashboard Metric Consistency

### Current Behavior
Previously fixed, need to verify all metrics are internally consistent.

### Verification Results

**Traced All Metrics:**

1. **Published Assignments** → `GET /admin/dashboard` → `COUNT(is_published = True)`
2. **Draft Assignments** → `GET /admin/dashboard` → `COUNT(is_published = False)`
3. **Pending Tasks** → `GET /admin/dashboard` → `COUNT(is_published = True AND status = 'pending')`
4. **Completed Tasks** → `GET /admin/dashboard` → `COUNT(is_published = True AND status = 'completed')`
5. **Critical Priority** → `GET /admin/dashboard` → `COUNT(is_published = True AND priority = 'Critical')`
6. **High Priority** → `GET /admin/dashboard` → `COUNT(is_published = True AND priority = 'High')`
7. **Departments Impacted** → `GET /admin/dashboard` → `COUNT(DISTINCT department_id)`
8. **Upcoming Deadlines** → `GET /admin/dashboard` → `COUNT(is_published = True AND due_date WITHIN 30 days)`

**All metrics now use is_published filter correctly** ✅

### Affected Files
- `backend/crud.py` - Dashboard metrics (already fixed)
- `frontend/dashboard/src/pages/Dashboard.jsx` - Display (already fixed)

### Root Cause
**NO ISSUE FOUND** - Previously corrected in Task 1.

### Proposed Action
**VERIFY ONLY** - No changes needed.

---

## ISSUE 5: Assignment Center Count (205 vs 34)

### Current Behavior
- Dashboard: 205 Draft Assignments
- Assignment Center: 34 MAPs

### Root Cause Analysis

**Traced Data Sources:**

1. **Dashboard "Draft Assignments":**
   ```python
   # backend/crud.py get_dashboard_summary()
   unpublished = db.query(Assignment).filter(
       Assignment.is_published == False
   ).count()
   # Returns: 205 total assignment records
   ```

2. **Assignment Center "34 MAPs":**
   ```python
   # backend/crud.py get_unpublished_assignment_summary()
   summary = db.query(
       Department.id,
       Department.name,
       func.count(Assignment.id).label('task_count')
   ).join(Assignment).filter(
       Assignment.is_published == False
   ).group_by(Department.id, Department.name).all()
   
   # Returns: {
   #   "total_maps": 34,  # This is COUNT of DEPARTMENT GROUPS with unpublished assignments
   #   "departments": [...]
   # }
   ```

**Root Cause:** Different aggregation levels
- Dashboard counts **INDIVIDUAL ASSIGNMENTS** (205 total)
- Assignment Center counted **DEPARTMENTS** (not total assignments)

### Affected Files
- `backend/routers/assignment_center_router.py` - Summary calculation
- `frontend/dashboard/src/pages/AssignmentCenter.jsx` - Display

### Root Cause
**Incorrect calculation in assignment_center_router.py Line 27:**
```python
total_maps = sum(dept["task_count"] for dept in summary.values())
```

This should sum task_count from ALL departments, but the bug is in how `get_unpublished_assignment_summary()` builds the summary.

### Verification Needed
Check `backend/crud.py` function `get_unpublished_assignment_summary()` implementation.

### Proposed Minimal Fix

**File:** `backend/crud.py`

**Find:** `get_unpublished_assignment_summary()` function

**Fix:** Ensure it returns correct per-department task counts and frontend sums them properly.

---

## ISSUE 6: Remove Demo Data Fallbacks

### Current Behavior
Several pages may still fall back to demo.js when API returns empty/error.

### Pages to Verify

1. **Dashboard** ✅ - Already uses strict API (verified in Issue 4)
2. **Assignment Center** ❌ - Falls back to demo (see Issue 1)
3. **Department Dashboard** - Need to verify
4. **MAP Management** - Need to verify
5. **Graph** ✅ - Uses session data (demo-only feature)
6. **Requirement Search** ✅ - Uses demo data intentionally (searchable taxonomy)

### Affected Files
- `frontend/dashboard/src/pages/AssignmentCenter.jsx` - Remove demo fallback
- `frontend/dashboard/src/pages/DepartmentWorkspace.jsx` - Verify API usage
- `frontend/dashboard/src/pages/Departments.jsx` - Verify API usage
- `frontend/dashboard/src/pages/Maps.jsx` - Check if uses API or demo

### Root Cause
**Defensive programming with demo fallbacks** that mask backend issues.

### Proposed Minimal Fix

**Strategy:**
1. Remove ALL imports of demo.js except in:
   - Requirement Search (intentional searchable taxonomy)
   - Graph (session-scoped feature)
   - MapDetail (detail expansion data)

2. For each page, use ONLY backend API
3. Display proper empty states when API returns no data

---

## Summary of Root Causes

| Issue | Root Cause | Files Affected | Priority |
|-------|------------|----------------|----------|
| 1. Pipeline Exit | Assignment Center falls back to demo instead of showing empty state | AssignmentCenter.jsx | CRITICAL |
| 2. 5500% Confidence | Demo data has mixed formats (decimals + percentages) | demo.js, MapDetail.jsx | HIGH |
| 3. Full Text Failure | Graph uses semantic IDs, backend expects integers | Graph.jsx | HIGH |
| 4. Metric Consistency | RESOLVED - No issues found | N/A | NONE |
| 5. Count Mismatch | Wrong aggregation level in summary calculation | crud.py, assignment_center_router.py | MEDIUM |
| 6. Demo Fallbacks | Defensive fallbacks mask real backend state | Multiple pages | MEDIUM |

---

## Proposed Implementation Order

1. **CRITICAL:** Fix Assignment Center empty state handling
2. **HIGH:** Fix confidence score display (normalize demo data)
3. **HIGH:** Fix Graph full text retrieval (use session data)
4. **MEDIUM:** Fix Assignment Center count calculation
5. **MEDIUM:** Remove remaining demo fallbacks

---

## Files to Modify (Minimal Set)

### Backend (2 files)
1. `backend/crud.py` - Verify get_unpublished_assignment_summary()
2. `frontend/dashboard/src/data/demo.js` - Normalize confidence values

### Frontend (2 files)
1. `frontend/dashboard/src/pages/AssignmentCenter.jsx` - Remove demo fallback
2. `frontend/dashboard/src/pages/Graph.jsx` - Use session data for full text

---

## No Changes Needed
- Backend models (schema is correct)
- Database migrations (no schema changes)
- API routes (endpoints are correct)
- Authentication (working correctly)
- Dashboard metrics (already fixed)

---

## Next Steps

1. Review this audit with stakeholders
2. Confirm proposed fixes align with intended behavior
3. Implement changes in order of priority
4. Test each fix independently
5. Produce verification report

