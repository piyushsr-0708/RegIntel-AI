# ASSIGNMENT CENTER COUNT DISCREPANCY INVESTIGATION

## Executive Summary

**Problem:** Pipeline shows "14 Requirements Extracted / 14 MAPs" for current document, but Assignment Center immediately shows "47 Total MAPs Across 9 Departments"

**Root Cause:** Assignment Center displays ALL unpublished assignments in the database (historical + current), not just the current document's assignments.

**Classification:** **INTENDED ARCHITECTURE** - Assignment Center is designed as a global workspace, not document-scoped.

---

## INVESTIGATION RESULTS

### 1. React Component Rendering Assignment Center

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`  
**Component Name:** `AssignmentCenter` (default export)  
**Lines:** 1-300 (entire file)

**Key Code:**
- **Line 1-5:** Imports and setup
- **Line 6-16:** Component state declarations
- **Line 18-21:** useEffect that calls `loadSummary()` on mount and when `hasSession` changes
- **Line 23-31:** `loadSummary()` function that calls backend API
- **Line 120-128:** Summary card that displays total_maps count

**Rendering Logic (Lines 120-128):**
```javascript
<div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
  {summary.total_maps}  // ← DISPLAYS TOTAL FROM BACKEND
</div>
<div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
  Total MAPs Across {summary.departments.length} Departments
</div>
```

---

### 2. API Endpoint Called

**Endpoint:** `GET /assignment-center/summary`

**Location:** `backend/routers/assignment_center_router.py`  
**Function:** `get_assignment_summary()`  
**Lines:** 18-33

**Code:**
```python
@router.get("/summary")
def get_assignment_summary(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get unpublished assignments grouped by department
    Shows after pipeline completes
    """
    summary = crud.get_unpublished_assignment_summary(db)
    
    # Get total MAPs
    total_maps = sum(dept["task_count"] for dept in summary.values())
    
    return {
        "total_maps": total_maps,
        "departments": list(summary.values())
    }
```

**Key Observation:** No document_id filter - queries ALL unpublished assignments.

---

### 3. Data Source Analysis

**Assignment Center loads:** **ALL PERSISTED UNPUBLISHED ASSIGNMENTS IN DATABASE**

**Evidence:**

**File:** `backend/crud.py`  
**Function:** `get_unpublished_assignment_summary()`  
**Lines:** 394-427

**Critical SQL Query (Lines 410-412):**
```python
assignments = db.query(models.Assignment).filter(
    models.Assignment.is_published == False
).all()
```

**What this returns:**
- ✅ ALL unpublished assignments
- ✅ Across ALL documents
- ✅ Across ALL departments
- ❌ NOT filtered by document_id
- ❌ NOT filtered by session
- ❌ NOT filtered by upload date

---

### 4. Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ DATABASE (compliance.db)                                    │
│ - 56 total assignments                                      │
│ - 47 unpublished (is_published = 0)                         │
│ - 9 published (is_published = 1)                            │
│ - Across 4 documents                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓ SQL: SELECT * WHERE is_published = False
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: crud.get_unpublished_assignment_summary()          │
│ File: backend/crud.py                                       │
│ Lines: 394-427                                              │
│ Returns: {                                                  │
│   dept_1: { task_count: 15, requirements: [...] },         │
│   dept_2: { task_count: 8, requirements: [...] },          │
│   ...                                                       │
│   total across 5 departments = 47 assignments               │
│ }                                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓ HTTP Response
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: assignment_center_router.py                        │
│ Function: get_assignment_summary()                          │
│ Lines: 18-33                                                │
│ Returns JSON:                                               │
│ {                                                           │
│   "total_maps": 47,                                         │
│   "departments": [                                          │
│     { "department_id": 1, "task_count": 15, ... },          │
│     { "department_id": 2, "task_count": 8, ... },           │
│     ...                                                     │
│   ]                                                         │
│ }                                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓ GET /assignment-center/summary
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: AssignmentCenter.jsx                              │
│ Function: loadSummary()                                     │
│ Lines: 23-31                                                │
│ Stores in state: setSummary(response.data)                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓ React State Update
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: AssignmentCenter.jsx                              │
│ Component Render                                            │
│ Lines: 120-128                                              │
│ UI Displays:                                                │
│ "47 Total MAPs Across 9 Departments"                        │
└─────────────────────────────────────────────────────────────┘
```

---

### 5. Why UI Shows 47 MAPs While Current Analysis Produced Only 14

**Database Evidence:**
```
Total documents: 4
Total requirements: 56
Total assignments: 56
Unpublished assignments: 47

Breakdown by Document:
- Doc 1: 14 requirements → 14 assignments (7 unpublished, 7 published)
- Doc 2: 14 requirements → 14 assignments (12 unpublished, 2 published)
- Doc 3: 14 requirements → 14 assignments (14 unpublished, 0 published)
- Doc 4: 14 requirements → 14 assignments (14 unpublished, 0 published)

Total Unpublished: 7 + 12 + 14 + 14 = 47 assignments
```

**Explanation:**
1. User uploads Document 4 (most recent)
2. Pipeline processes Document 4 → Creates 14 requirements → Creates 14 assignments
3. Pipeline UI shows "14 Requirements Extracted / 14 MAPs" ← Document 4 only
4. User navigates to Assignment Center
5. Assignment Center queries ALL unpublished assignments in database
6. Database contains 47 unpublished assignments from Documents 1, 2, 3, and 4
7. Assignment Center displays "47 Total MAPs" ← ALL documents

**The 47 count includes:**
- ✅ Doc 4: 14 assignments (current upload)
- ✅ Doc 3: 14 assignments (previous upload)
- ✅ Doc 2: 12 assignments (partially published)
- ✅ Doc 1: 7 assignments (partially published)

---

### 6. Is This Intentional or a Bug?

**Classification:** ✅ **INTENDED ARCHITECTURE**

**Evidence:**

**1. Function Documentation (backend/routers/assignment_center_router.py, Lines 24-26):**
```python
"""
Get unpublished assignments grouped by department
Shows after pipeline completes
"""
```

**Key phrase:** "Get unpublished assignments" (not "current document assignments")

**2. Function Name:**
- `get_unpublished_assignment_summary()` - Global scope
- NOT `get_document_unpublished_assignments(document_id)` - Document scope

**3. Workflow Design:**
The Assignment Center is designed as a **batch review workspace**:
- Accumulates assignments from multiple circulars
- Reviews all pending work in one place
- Publishes assignments to departments in batches
- Acts as a queue/inbox, not a document-specific view

**4. Business Logic:**
- Head Office users process multiple circulars over time
- Need to see ALL pending assignments awaiting publication
- Not just the current document's assignments
- Similar to an email inbox (shows all unread, not just latest sender)

**5. Consistent Behavior:**
Assignment Center has 3 tabs/views:
- **Unpublished** (47) - Shows ALL unpublished across all documents
- **Published** (9) - Shows ALL published across all documents
- Both are global, not document-scoped

**Conclusion:** This is **intended architecture**, not a bug. Assignment Center is a global workspace.

---

### 7. How UI Should Distinguish Current vs Historical MAPs

**Current State:** NO DISTINCTION

The UI does not currently differentiate between:
- Current document's assignments (14)
- Historical documents' assignments (33)

**User Confusion Points:**

1. **Pipeline:** "14 Requirements Extracted"
2. **User clicks:** "Assignment Center"
3. **Assignment Center:** "47 Total MAPs"
4. **User thinks:** "Wait, I only uploaded one document with 14 requirements!"

**Problem:** User doesn't know they're seeing accumulated data from 4 documents.

**Recommended UI Enhancements (Without Changing Logic):**

#### Option A: Add Document Context
```
📊 47 Total MAPs Across 9 Departments
   (From 4 processed circulars)
```

#### Option B: Show Document Breakdown
```
Assignment Center - Pending Review

Total Pending: 47 MAPs from 4 Circulars
├─ Current Session: 14 MAPs (Document 4)
└─ Previous Sessions: 33 MAPs (Documents 1, 2, 3)

[Show All] [Show Current Only]
```

#### Option C: Add Filter Toggle
```
View: [All Documents ▼]
      └─ All Documents (47)
      └─ Current Session (14)
      └─ Last 7 Days (28)
```

#### Option D: Add Breadcrumb Trail
```
Pipeline → Analysis → Assignment Center (All Documents)
                                      ^^^^^^^^^^^^^^^^
```

#### Option E: Add Info Icon with Tooltip
```
47 Total MAPs ⓘ
   │
   └─ Tooltip: "This includes all unpublished assignments
                from all processed circulars, not just the
                current document."
```

---

### 8. Smallest Possible Change for Internal Consistency

**Recommended Fix:** **Update UI Text to Clarify Scope**

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`  
**Lines:** 120-128

**Current:**
```javascript
<div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
  {summary.total_maps}
</div>
<div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
  Total MAPs Across {summary.departments.length} Departments
</div>
```

**Proposed:**
```javascript
<div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
  {summary.total_maps}
</div>
<div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
  Total Pending MAPs Across {summary.departments.length} Departments
  <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginLeft: 8 }}>
    (From all processed circulars)
  </span>
</div>
```

**Why This Is Minimal:**
- ✅ 1 file changed
- ✅ 2 lines modified
- ✅ No backend changes
- ✅ No API changes
- ✅ No state changes
- ✅ No routing changes
- ✅ No other modules affected
- ✅ Clarifies scope without changing behavior
- ✅ Maintains existing architecture

**Impact:**
- Users understand they're seeing accumulated data
- No confusion about count mismatch
- No changes to functionality
- No performance impact

---

## DETAILED COMPONENT ANALYSIS

### Assignment Center Component Structure

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`

#### State Variables (Lines 8-15)
```javascript
const [summary, setSummary] = useState(null);              // Stores backend response
const [loading, setLoading] = useState(true);              // Loading indicator
const [publishing, setPublishing] = useState({});          // Publishing state per dept
const [selectedAssignment, setSelectedAssignment] = useState(null);  // Modal data
const [showFullText, setShowFullText] = useState(false);   // Modal visibility
const [loadingFullText, setLoadingFullText] = useState(false);  // Modal loading
```

#### Data Loading (Lines 18-31)
```javascript
useEffect(() => {
  console.log('[ASSIGNMENT_CENTER] Loading summary from backend (session state:', hasSession, ')');
  loadSummary();
}, [hasSession]); // ← Re-loads when session state changes

const loadSummary = async () => {
  setLoading(true);
  try {
    const response = await api.get('/assignment-center/summary');  // ← API CALL
    console.log('[ASSIGNMENT_CENTER] Summary loaded:', response.data);
    setSummary(response.data);  // ← Stores ALL unpublished assignments
  } catch (error) {
    console.error('Failed to load assignment summary:', error);
  } finally {
    setLoading(false);
  }
};
```

**Key Observations:**
1. API call has NO document_id parameter
2. No filtering of response data
3. Stores entire backend response directly
4. Re-loads when `hasSession` changes (but doesn't filter by session)

#### Display Logic (Lines 120-128)
```javascript
<div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
  {summary.total_maps}  // ← Direct display of backend value
</div>
<div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
  Total MAPs Across {summary.departments.length} Departments
</div>
```

**No client-side filtering** - displays raw backend count.

---

## BACKEND ARCHITECTURE ANALYSIS

### CRUD Function: get_unpublished_assignment_summary()

**File:** `backend/crud.py`  
**Lines:** 394-427

#### Step-by-Step Logic:

**Step 1: Initialize All Departments (Lines 397-406)**
```python
departments = get_all_departments(db)  # Get all 9 departments
dept_summary = {}
for dept in departments:
    dept_summary[dept.id] = {
        "department_id": dept.id,
        "department_name": dept.name,
        "department_code": dept.code,
        "task_count": 0,  # ← Start with 0
        "requirements": []
    }
```

**Purpose:** Ensures 0-count departments are included (show "0 tasks" instead of hidden).

**Step 2: Query ALL Unpublished Assignments (Lines 408-412)**
```python
assignments = db.query(models.Assignment).filter(
    models.Assignment.is_published == False  # ← ONLY FILTER
).all()
```

**SQL Equivalent:**
```sql
SELECT * FROM assignments WHERE is_published = 0;
```

**What's NOT filtered:**
- ❌ document_id
- ❌ created_at (date range)
- ❌ batch_id
- ❌ session_id
- ❌ user_id

**Step 3: Group by Department (Lines 414-427)**
```python
for assignment in assignments:  # ← ALL 47 assignments
    dept_id = assignment.department_id
    if dept_id in dept_summary:
        dept_summary[dept_id]["task_count"] += 1  # ← Increment count
        dept_summary[dept_id]["requirements"].append({
            "assignment_id": assignment.id,
            "requirement_id": assignment.requirement.id,
            "requirement_text": assignment.requirement.text,
            "priority": assignment.requirement.priority,
            "domain": assignment.requirement.domain
        })

return dept_summary
```

**Result:** Returns dictionary with all departments and their unpublished counts.

---

## DATABASE STATE VERIFICATION

### Current Database Contents

**Query Results:**
```sql
-- Total counts
SELECT COUNT(*) FROM assignments;          → 56
SELECT COUNT(*) FROM assignments WHERE is_published = 0;  → 47
SELECT COUNT(*) FROM requirements;         → 56
SELECT COUNT(*) FROM documents;            → 4

-- Document details
SELECT id, original_filename, processed FROM documents;
┌────┬──────────────────────────────────────────┬───────────┐
│ id │ original_filename                        │ processed │
├────┼──────────────────────────────────────────┼───────────┤
│ 1  │ MDCD060220266033C352C548475B9E...BB.pdf  │ 1         │
│ 2  │ MDCD060220266033C352C548475B9E...BB.pdf  │ 1         │
│ 3  │ PR385D71D4FFF59D42D382378B358E...A.pdf   │ 1         │
│ 4  │ PR385D71D4FFF59D42D382378B358E...A.pdf   │ 1         │
└────┴──────────────────────────────────────────┴───────────┘

-- Assignments per document
SELECT 
  d.id, 
  COUNT(DISTINCT r.id) as req_count,
  COUNT(DISTINCT a.id) as assign_count,
  SUM(CASE WHEN a.is_published = 0 THEN 1 ELSE 0 END) as unpublished,
  SUM(CASE WHEN a.is_published = 1 THEN 1 ELSE 0 END) as published
FROM documents d
LEFT JOIN requirements r ON r.document_id = d.id
LEFT JOIN assignments a ON a.requirement_id = r.id
GROUP BY d.id;

┌────┬───────────┬──────────────┬─────────────┬───────────┐
│ id │ req_count │ assign_count │ unpublished │ published │
├────┼───────────┼──────────────┼─────────────┼───────────┤
│ 1  │ 14        │ 14           │ 7           │ 7         │
│ 2  │ 14        │ 14           │ 12          │ 2         │
│ 3  │ 14        │ 14           │ 14          │ 0         │
│ 4  │ 14        │ 14           │ 14          │ 0         │
└────┴───────────┴──────────────┴─────────────┴───────────┘

TOTAL: 56 requirements → 56 assignments
       47 unpublished + 9 published = 56 ✓

-- Unpublished by department
SELECT department_id, COUNT(*) 
FROM assignments 
WHERE is_published = 0 
GROUP BY department_id;

┌───────────────┬──────┐
│ department_id │ count│
├───────────────┼──────┤
│ 1             │ 15   │
│ 2             │ 8    │
│ 3             │ 8    │
│ 4             │ 4    │
│ 5             │ 12   │
└───────────────┴──────┘

TOTAL: 15 + 8 + 8 + 4 + 12 = 47 ✓
```

**Verification:** Numbers match Assignment Center display (47 total, 5 departments with tasks).

---

## COMPARISON: PIPELINE vs ASSIGNMENT CENTER

### Pipeline Analysis View

**File:** `frontend/dashboard/src/pages/Pipeline.jsx`  
**Data Source:** `session.analysis` (from AnalysisSession context)  
**Scope:** **CURRENT DOCUMENT ONLY**

**Display (Lines 65-70):**
```javascript
{ label: "Requirements Extracted", value: s.totalRequirements, ... },
// s = session.analysis.stats
// s.totalRequirements = 14 (from current document)
```

**Data Flow:**
```
Current Document Upload
  ↓
Backend processes document_id=4
  ↓
Creates 14 requirements
  ↓
GET /admin/document-analysis/4
  ↓
Returns: { counts: { requirements_extracted: 14, assignments_generated: 14 } }
  ↓
Frontend buildAnalysisResult(4, api)
  ↓
session.analysis.stats.totalRequirements = 14
  ↓
Pipeline displays: "14 Requirements Extracted"
```

**Scope:** Document-scoped (document_id = 4)

### Assignment Center View

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`  
**Data Source:** `/assignment-center/summary` API  
**Scope:** **ALL UNPUBLISHED ASSIGNMENTS (GLOBAL)**

**Display (Lines 120-122):**
```javascript
{summary.total_maps}
// summary.total_maps = 47 (from all documents)
```

**Data Flow:**
```
User navigates to Assignment Center
  ↓
GET /assignment-center/summary
  ↓
Backend queries: SELECT * WHERE is_published = False
  ↓
Returns ALL unpublished assignments (docs 1, 2, 3, 4)
  ↓
Frontend displays: "47 Total MAPs"
```

**Scope:** Global (all documents)

### Side-by-Side Comparison

| Aspect | Pipeline | Assignment Center |
|--------|----------|-------------------|
| **Data Source** | Session state | Database query |
| **Scope** | Current document | All documents |
| **Filter** | document_id = 4 | is_published = False |
| **Count** | 14 | 47 |
| **Context** | "This RBI Circular" | "Total MAPs" |
| **Intent** | Show current analysis | Show pending workload |
| **User Expectation** | Current upload | Could be ambiguous |

---

## USER JOURNEY ANALYSIS

### Scenario: First-Time User Uploads Document

**Step 1:** User uploads RBI circular PDF  
**Step 2:** Pipeline processes → "14 Requirements Extracted"  
**Step 3:** User sees success message  
**Step 4:** User clicks "Assignment Center"  
**Step 5:** Sees "47 Total MAPs Across 9 Departments"  

**User Reaction:** 🤔 "Wait, I only uploaded one document with 14 requirements. Where did 47 come from?"

**Confusion Points:**
1. No indication that count includes historical data
2. No visual connection between Pipeline (14) and Assignment Center (47)
3. No explanation that 47 = current (14) + historical (33)
4. No document-level breakdown

**User Questions:**
- "Did something go wrong?"
- "Are there duplicates?"
- "Is this counting multiple times?"
- "Should I only see 14?"

---

## ARCHITECTURAL INTENT

### Design Pattern: Accumulator/Queue Model

Assignment Center follows a **queue/inbox pattern**:

1. **Accumulation:** Multiple circulars processed over time → assignments accumulate
2. **Review:** Head Office reviews all pending assignments in one place
3. **Batch Publishing:** Publish assignments to departments in batches
4. **Clearance:** Published assignments leave the queue (is_published = True)

**Similar to:**
- Email inbox (shows all unread emails, not just from latest sender)
- Task queue (shows all pending tasks, not just from latest project)
- Shopping cart (shows all items, not just latest addition)

### Why Global Scope Makes Sense

**Business Context:**
- RBI issues multiple circulars per month
- Each circular generates 10-20 requirements
- Each requirement assigned to 1-3 departments
- Result: Hundreds of assignments accumulating

**Workflow:**
1. Monday: Upload Circular A → 14 assignments
2. Tuesday: Upload Circular B → 15 assignments
3. Wednesday: Upload Circular C → 18 assignments
4. Thursday: Head Office reviews ALL 47 pending assignments
5. Thursday: Publish all 47 to departments at once

**If document-scoped:**
- Would need to review each circular separately
- Would need to publish each circular separately
- More clicks, more time, less efficient

**Global scope = Batch efficiency**

---

## TECHNICAL OBSERVATIONS

### No Session Dependency

Assignment Center does NOT depend on AnalysisSession context:
```javascript
const { hasSession, resetSession } = useAnalysisSession();
```

**Uses:**
- `hasSession` - Only to trigger reload (Lines 18-21)
- `resetSession` - Not used in component

**Does NOT use:**
- `session.analysis` - Not accessed
- `session.document` - Not accessed
- `session.counts` - Not accessed

**Why:** Assignment Center is independent of current session. Shows all data regardless of whether user has active analysis session.

### API Independence

Assignment Center API has no parameters:
```javascript
const response = await api.get('/assignment-center/summary');
// No document_id
// No session_id
// No filter parameters
```

**Backend endpoint signature:**
```python
@router.get("/summary")
def get_assignment_summary(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
```

**Only dependencies:**
- Authentication (current_user)
- Database access (db)

**No context parameters** - Always returns same data for any head_office user.

---

## RECOMMENDATIONS SUMMARY

### Classification

✅ **INTENDED ARCHITECTURE** - Not a bug

### Smallest Change for Consistency

**Update UI text** to clarify scope:
```
"47 Total Pending MAPs Across 9 Departments (From all processed circulars)"
```

**Rationale:**
- 1 file changed
- 2 lines modified
- No backend changes
- No API changes
- Maintains existing architecture
- Eliminates user confusion

### Alternative Solutions (If More Changes Acceptable)

**Option 1: Add Document Filter**
- Add dropdown: "View: [All Documents] [Current Session] [Last 7 Days]"
- Backend adds optional document_id parameter
- Requires backend + frontend changes

**Option 2: Add Document Breakdown Section**
```
Current Session: 14 MAPs (Document 4)
Previous Sessions: 33 MAPs (3 documents)
────────────────────────────────
Total: 47 MAPs
```

**Option 3: Split Into Tabs**
```
[Current Document (14)] [All Pending (47)] [Published (9)]
```

**Option 4: Add Context Banner**
```
ℹ️ This view shows all unpublished assignments from all processed 
   circulars. To view only the current document's assignments, 
   return to the Pipeline page.
```

---

## CONCLUSION

### Question Answers

**Q1: Which React component renders Assignment Center?**  
**A:** `AssignmentCenter` component in `frontend/dashboard/src/pages/AssignmentCenter.jsx`

**Q2: Which API endpoint(s) does it call?**  
**A:** `GET /assignment-center/summary` (Lines 23-31 in AssignmentCenter.jsx, defined in `backend/routers/assignment_center_router.py` Lines 18-33)

**Q3: Is it loading current session, persisted data, cached data, or demo data?**  
**A:** **ALL PERSISTED UNPUBLISHED ASSIGNMENTS** from database (no caching, no demo data, no session filtering)

**Q4: Data flow trace?**  
**A:** Database (WHERE is_published=False) → backend/crud.py::get_unpublished_assignment_summary() → backend/routers/assignment_center_router.py::get_assignment_summary() → GET /assignment-center/summary → frontend/AssignmentCenter.jsx::loadSummary() → React state (summary) → UI rendering (Lines 120-128)

**Q5: Why does UI show 47 MAPs while current analysis produced 14?**  
**A:** Assignment Center displays ALL unpublished assignments across ALL 4 documents in database (7 + 12 + 14 + 14 = 47), not just current document's 14 assignments.

**Q6: Is this intended, unfinished, legacy, or bug?**  
**A:** **INTENDED ARCHITECTURE** - Assignment Center is designed as global batch review workspace, not document-scoped view.

**Q7: How should UI distinguish current vs historical?**  
**A:** Add clarifying text: "Total Pending MAPs Across 9 Departments (From all processed circulars)" or add document breakdown section.

**Q8: Smallest possible change?**  
**A:** Modify `frontend/dashboard/src/pages/AssignmentCenter.jsx` Lines 120-128 to add "(From all processed circulars)" text - 1 file, 2 lines changed.

---

## STATUS

**Investigation Complete:** ✅  
**Classification:** Intended Architecture (Not a Bug)  
**Recommended Fix:** Minimal UI text clarification  
**No Code Changed:** ✅ (Investigation only)
