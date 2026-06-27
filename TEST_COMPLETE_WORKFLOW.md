# Complete MVP Workflow Testing Guide

**Date:** June 27, 2026  
**Purpose:** Verify end-to-end workflow from upload to department completion

---

## 🎯 Overview

This guide tests the COMPLETE workflow that was requested:

```
Admin Login
    ↓
Upload Circular
    ↓
Pipeline Completes
    ↓
Assignment Center Shows Departments
    ↓
Publish Compliance
    ↓
Logout
    ↓
Compliance Login
    ↓
Tasks Visible
    ↓
Mark Completed
    ↓
Logout
    ↓
Admin Login
    ↓
Dashboard Updated
```

---

## 🔧 Prerequisites

### 1. Start Backend

```bash
cd backend
uvicorn main:main --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Start Frontend

```bash
cd frontend/dashboard
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 3. Verify Database

```bash
cd backend
python -c "
from database import SessionLocal
from models import User, Department
db = SessionLocal()
print('Users:', db.query(User).count())
print('Departments:', db.query(Department).count())
"
```

**Expected Output:**
```
Users: 6
Departments: 5
```

If counts are 0, run seed script:
```bash
cd backend
python -c "from utils.seed_data import seed_all; from database import SessionLocal; seed_all(SessionLocal())"
```

---

## 📋 Complete Workflow Test

### Step 1: Admin Login ✅

1. Open browser: `http://localhost:5173`
2. You should see the login page
3. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
4. Click "Sign In"

**Expected Result:**
- ✅ Redirects to Admin Dashboard
- ✅ Shows "Admin Dashboard" heading
- ✅ Sidebar shows: Pipeline, Upload, Assignment Center, Admin Dashboard
- ✅ Topbar shows: Logo, LIVE badge, User menu with "admin"

**Verify Console:**
```
[AUTH] Login attempt: admin
[AUTH] Login response received: {...}
[AUTH] Token stored: eyJ...
[AUTH] User info received: {id: 1, username: "admin", ...}
```

**If Login Fails:**
- Check backend is running on port 8000
- Check frontend proxy configuration
- Check browser console for errors
- Verify seed data exists

---

### Step 2: Upload Circular ✅

1. Click "Pipeline" in sidebar
2. You should see "Regulatory Intelligence Pipeline" page
3. Prepare a test PDF file (any PDF works)
4. Either:
   - **Drag and drop** PDF into upload zone, OR
   - **Click "Browse File"** and select PDF

**Expected Result:**
- ✅ File appears with filename, size, timestamp
- ✅ "Initiate Processing Pipeline" button appears
- ✅ No horizontal scrolling

**If Upload Zone Not Visible:**
- Refresh page
- Check sidebar navigation
- Check route `/pipeline`

---

### Step 3: Pipeline Execution ✅

1. Click "Initiate Processing Pipeline"
2. Watch the visual progression

**Expected UI:**
```
Processing Status:
┌────────────────────────────────────┐
│ PROCESSING...          0.0s        │
│ ████████░░░░░░░░ 45%              │
└────────────────────────────────────┘

Stages List:
✓ Circular Loaded
✓ Text Extraction
✓ Requirement Extraction
→ Requirement Classification (in progress)
  Cross-reference Analysis
  Knowledge Graph Construction
  Department Assignment
  MAP Generation
  Dashboard Ready
```

**Expected Console Logs:**
```
[PIPELINE] Starting pipeline for file: test.pdf
[PIPELINE] Uploading file...
[PIPELINE] File uploaded, document ID: 1
[PIPELINE] Starting visual stage progression...
```

**After ~10-18 seconds:**
```
[PIPELINE] Visual stages complete, calling process endpoint...
[PIPELINE] Processing document ID: 1
[PIPELINE] Processing complete: {status: "success", document_id: 1, ...}
[PIPELINE] Requirements created: 14
[PIPELINE] Assignments created: 14
[PIPELINE] Pipeline successfully completed
```

**Expected Final UI:**
```
┌────────────────────────────────────┐
│ ✓ ANALYSIS COMPLETE    14.2s       │
│ █████████████████████ 100%         │
│ Generating analysis report...      │
└────────────────────────────────────┘
```

**If Error Occurs:**
```
┌────────────────────────────────────┐
│ ✕ ERROR                5.3s        │
│ Upload failed. Please try again.   │
│ [ Try Again ]                      │
└────────────────────────────────────┘
```

Check:
- Backend logs for errors
- Network tab in browser DevTools
- Console for error messages

---

### Step 4: Assignment Center Populated ✅

1. Wait for "✓ ANALYSIS COMPLETE"
2. Click "Assignment Center" in sidebar
3. Navigate to `/assignment-center`

**Expected Result:**
```
Assignment Center
─────────────────────────────────────────

Total Unpublished MAPs: 14

┌────────────────────────────────────┐
│ Compliance                         │
│ Code: COMP                         │
│ Tasks: 5                           │
│ [ Publish ]                        │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Cyber Security                     │
│ Code: CYBER                        │
│ Tasks: 3                           │
│ [ Publish ]                        │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Risk Management                    │
│ Code: RISK                         │
│ Tasks: 2                           │
│ [ Publish ]                        │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Treasury                           │
│ Code: TREAS                        │
│ Tasks: 2                           │
│ [ Publish ]                        │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Operations                         │
│ Code: OPS                          │
│ Tasks: 2                           │
│ [ Publish ]                        │
└────────────────────────────────────┘
```

**If Assignment Center is Empty:**

Check backend:
```bash
cd backend
python -c "
from database import SessionLocal
from models import Assignment
db = SessionLocal()
count = db.query(Assignment).count()
print(f'Assignments: {count}')
"
```

If count is 0:
- Check process endpoint was called (console logs)
- Check backend logs for errors
- Manually call: `POST http://localhost:8000/api/admin/process-document/1`

**Verify Network Request:**
```http
GET /api/assignment-center/summary
Status: 200 OK

Response:
{
  "total_maps": 14,
  "departments": [
    {"department_id": 1, "department_name": "Compliance", "task_count": 5},
    {"department_id": 2, "department_name": "Cyber Security", "task_count": 3},
    // ...
  ]
}
```

---

### Step 5: Publish to Compliance ✅

1. In Assignment Center, find "Compliance" card
2. Click "Publish" button

**Expected Result:**
- ✅ Button shows loading state briefly
- ✅ Success message: "Published 5 tasks to Compliance"
- ✅ Compliance card disappears from Assignment Center
- ✅ Total count updates: "Total Unpublished MAPs: 9"

**Verify Network Request:**
```http
POST /api/assignment-center/publish
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "department_id": 1
}

Response:
{
  "status": "success",
  "published_count": 5
}
```

**Verify Database:**
```bash
cd backend
python -c "
from database import SessionLocal
from models import Assignment
db = SessionLocal()
published = db.query(Assignment).filter(Assignment.is_published == True).count()
print(f'Published Assignments: {published}')
"
```

Expected: `Published Assignments: 5`

---

### Step 6: Logout from Admin ✅

1. Click user menu in top-right (shows "admin")
2. Click "Logout"

**Expected Result:**
- ✅ Redirects to login page
- ✅ localStorage cleared (token removed)
- ✅ Console shows: `[AUTH] Logout complete - token and user cleared`

**Verify:**
Open browser DevTools → Application → Local Storage → Check:
- `token` should be gone
- `user` should be gone

---

### Step 7: Compliance Login ✅

1. On login page, enter credentials:
   - **Username:** `compliance`
   - **Password:** `compliance123`
2. Click "Sign In"

**Expected Result:**
- ✅ Redirects to Department Dashboard
- ✅ Shows "Department Workspace" heading
- ✅ Sidebar shows: Dashboard, My Assignments, Knowledge Graph, Requirements, Search, Logout
- ✅ Sidebar does NOT show: Pipeline, Upload, Assignment Center, Admin Dashboard
- ✅ Topbar shows "compliance" user

**Verify Role-Based Navigation:**
- ❌ Should NOT see "Pipeline"
- ❌ Should NOT see "Assignment Center"
- ❌ Should NOT see "Admin Dashboard"
- ✅ Should see "My Assignments"
- ✅ Should see "Knowledge Graph"
- ✅ Should see "Requirements"

---

### Step 8: View Assigned Tasks ✅

1. Click "My Assignments" in sidebar
2. Navigate to `/department/workspace`

**Expected Result:**
```
My Assigned Tasks
─────────────────────────────────────────

Department: Compliance
Total Tasks: 5
Completed: 0

┌────────────────────────────────────┐
│ ⚠ Critical                         │
│ REQ_TEST_0000                      │
│ Banks must implement enhanced      │
│ customer due diligence...          │
│ Domain: KYC                        │
│ Status: Pending                    │
│ [ Mark Completed ]                 │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ ⚠ High                             │
│ REQ_TEST_0001                      │
│ Suspicious transaction monitoring  │
│ systems must be updated...         │
│ Domain: AML                        │
│ Status: Pending                    │
│ [ Mark Completed ]                 │
└────────────────────────────────────┘

... (3 more tasks)
```

**Verify Network Request:**
```http
GET /api/departments/workspace/my-tasks
Authorization: Bearer {compliance_token}

Response:
{
  "department_name": "Compliance",
  "total_tasks": 5,
  "completed_count": 0,
  "tasks": [
    {
      "assignment_id": 1,
      "requirement_id": 1,
      "requirement_text": "Banks must implement...",
      "priority": "Critical",
      "domain": "KYC",
      "status": "pending",
      "assigned_at": "2026-06-27T12:34:56"
    },
    // ... 4 more
  ]
}
```

**If No Tasks Visible:**

Check database:
```bash
cd backend
python -c "
from database import SessionLocal
from models import Assignment, Department
db = SessionLocal()
dept = db.query(Department).filter(Department.name == 'Compliance').first()
if dept:
    tasks = db.query(Assignment).filter(
        Assignment.department_id == dept.id,
        Assignment.is_published == True
    ).count()
    print(f'Compliance Published Tasks: {tasks}')
"
```

Expected: `Compliance Published Tasks: 5`

If 0:
- Check Step 5 was completed (Publish)
- Check `is_published` column in database
- Manually set: `UPDATE assignments SET is_published = TRUE WHERE department_id = 1`

---

### Step 9: Mark Task Completed ✅

1. On first task (Critical, KYC), click "Mark Completed"
2. Watch for confirmation

**Expected Result:**
- ✅ Button shows loading state briefly
- ✅ Success message: "Task marked as completed"
- ✅ Task status changes to "Completed"
- ✅ Task shows completion timestamp
- ✅ Completed count updates: "Completed: 1"
- ✅ Button changes to "Completed ✓" (disabled)

**Verify Network Request:**
```http
POST /api/departments/workspace/tasks/1/complete
Authorization: Bearer {compliance_token}

Response:
{
  "status": "success",
  "assignment_id": 1
}
```

**Verify Database:**
```bash
cd backend
python -c "
from database import SessionLocal
from models import Assignment
db = SessionLocal()
completed = db.query(Assignment).filter(
    Assignment.status == 'COMPLETED'
).count()
print(f'Completed Assignments: {completed}')
"
```

Expected: `Completed Assignments: 1`

---

### Step 10: Logout from Compliance ✅

1. Click user menu (shows "compliance")
2. Click "Logout"

**Expected Result:**
- ✅ Redirects to login page
- ✅ localStorage cleared

---

### Step 11: Admin Login Again ✅

1. Login with:
   - **Username:** `admin`
   - **Password:** `admin123`

**Expected Result:**
- ✅ Redirects to Admin Dashboard
- ✅ Sidebar shows admin navigation

---

### Step 12: Verify Dashboard Updated ✅

1. Navigate to "Admin Dashboard" (should be default)
2. Check completion table

**Expected Result:**
```
Admin Dashboard
─────────────────────────────────────────

Department Completion Summary

┌──────────────────┬──────────┬───────────┬───────────┐
│ Department       │ Assigned │ Completed │ Remaining │
├──────────────────┼──────────┼───────────┼───────────┤
│ Compliance       │    5     │     1     │     4     │
│ Cyber Security   │    0     │     0     │     0     │
│ Risk Management  │    0     │     0     │     0     │
│ Treasury         │    0     │     0     │     0     │
│ Operations       │    0     │     0     │     0     │
└──────────────────┴──────────┴───────────┴───────────┘

Overall Progress: 1/5 (20%)
```

**Verify Network Request:**
```http
GET /api/assignment-center/admin-summary
Authorization: Bearer {admin_token}

Response:
{
  "departments": [
    {
      "department_id": 1,
      "department_name": "Compliance",
      "assigned": 5,
      "completed": 1,
      "remaining": 4
    },
    {
      "department_id": 2,
      "department_name": "Cyber Security",
      "assigned": 0,
      "completed": 0,
      "remaining": 0
    },
    // ... etc
  ]
}
```

**Verify Database:**
```bash
cd backend
python -c "
from database import SessionLocal
from models import Assignment, Department
from sqlalchemy import func
db = SessionLocal()

# Get Compliance department
dept = db.query(Department).filter(Department.name == 'Compliance').first()

# Count published assignments
assigned = db.query(Assignment).filter(
    Assignment.department_id == dept.id,
    Assignment.is_published == True
).count()

# Count completed
completed = db.query(Assignment).filter(
    Assignment.department_id == dept.id,
    Assignment.status == 'COMPLETED'
).count()

print(f'Compliance - Assigned: {assigned}, Completed: {completed}, Remaining: {assigned - completed}')
"
```

Expected:
```
Compliance - Assigned: 5, Completed: 1, Remaining: 4
```

---

## ✅ Success Criteria

All steps should pass without errors:

- [x] Step 1: Admin login successful
- [x] Step 2: File upload works
- [x] Step 3: Pipeline processes file
- [x] Step 4: Assignment Center shows 14 tasks across 5 departments
- [x] Step 5: Publish to Compliance succeeds
- [x] Step 6: Admin logout works
- [x] Step 7: Compliance login successful
- [x] Step 8: Compliance sees 5 assigned tasks
- [x] Step 9: Mark completed works
- [x] Step 10: Compliance logout works
- [x] Step 11: Admin login again works
- [x] Step 12: Dashboard shows updated counts (1 completed, 4 remaining)

---

## 🐛 Common Issues & Fixes

### Issue 1: Assignment Center Empty After Pipeline

**Symptoms:**
- Pipeline completes successfully
- Assignment Center shows "No unpublished assignments"

**Root Cause:**
- Process endpoint not called
- Database insertion failed

**Fix:**
```bash
# Check console logs
[PIPELINE] Processing complete: {...} 
# Should show requirements_created: 14

# Check database
cd backend
python -c "from database import SessionLocal; from models import Assignment; db = SessionLocal(); print(db.query(Assignment).count())"

# If 0, manually call process endpoint
curl -X POST http://localhost:8000/api/admin/process-document/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Issue 2: Department Sees No Tasks

**Symptoms:**
- Compliance login successful
- My Assignments shows "No tasks assigned yet"

**Root Cause:**
- Tasks not published
- Wrong department ID
- is_published = FALSE

**Fix:**
```bash
# Check published status
cd backend
python -c "
from database import SessionLocal
from models import Assignment
db = SessionLocal()
published = db.query(Assignment).filter(Assignment.is_published == True).count()
print(f'Published: {published}')
"

# If 0, manually publish
python -c "
from database import SessionLocal
from models import Assignment, Department
db = SessionLocal()
dept = db.query(Department).filter(Department.name == 'Compliance').first()
assignments = db.query(Assignment).filter(Assignment.department_id == dept.id).all()
for a in assignments:
    a.is_published = True
db.commit()
print('Published all Compliance assignments')
"
```

---

### Issue 3: Dashboard Not Updating

**Symptoms:**
- Task marked completed
- Dashboard still shows 0 completed

**Root Cause:**
- Status not updated in database
- Dashboard API not filtering correctly
- Cache issue

**Fix:**
```bash
# Check assignment status
cd backend
python -c "
from database import SessionLocal
from models import Assignment
db = SessionLocal()
completed = db.query(Assignment).filter(Assignment.status == 'COMPLETED').count()
print(f'Completed: {completed}')
"

# If 0, check API endpoint
curl http://localhost:8000/api/assignment-center/admin-summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Hard refresh browser (Ctrl+Shift+R)
```

---

### Issue 4: Login Fails

**Symptoms:**
- "Login failed. Please check credentials"
- Network error

**Root Cause:**
- Backend not running
- Wrong credentials
- Database not seeded

**Fix:**
```bash
# Check backend
curl http://localhost:8000/docs
# Should return Swagger UI

# Re-seed database
cd backend
python -c "
from database import SessionLocal, engine
from models import Base
from utils.seed_data import seed_all

# Drop and recreate
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Seed
db = SessionLocal()
seed_all(db)
print('Database reseeded')
"

# Try login again with admin / admin123
```

---

### Issue 5: Sidebar Navigation Missing

**Symptoms:**
- Can't see Pipeline or Assignment Center
- Sidebar items missing

**Root Cause:**
- Routing issue
- Sidebar component not rendering
- Role-based logic incorrect

**Fix:**
```javascript
// Check App.jsx - Sidebar should be rendered
<div style={{ display: "flex", height: "100vh" }}>
  <Sidebar />  // ← Must be here
  <div style={{ flex: 1, overflow: "auto" }}>
    {/* Content */}
  </div>
</div>

// Check Sidebar.jsx - Role logic
{user.role === "HEAD_OFFICE" && (
  <Link to="/assignment-center">Assignment Center</Link>
)}
```

---

## 📊 Performance Benchmarks

### Expected Timings

| Operation | Expected Duration |
|-----------|------------------|
| File Upload | < 2 seconds |
| Visual Stages | 10-18 seconds |
| Backend Processing | < 1 second |
| Total Pipeline | 12-20 seconds |
| Assignment Center Load | < 500ms |
| Publish Action | < 300ms |
| Mark Completed | < 300ms |
| Dashboard Load | < 500ms |

---

## 📝 Test Results Template

```
=== COMPLETE WORKFLOW TEST RESULTS ===
Date: __________
Tester: __________

[ ] Step 1: Admin Login
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 2: Upload Circular
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 3: Pipeline Execution
    Status: PASS / FAIL
    Duration: _____ seconds
    Notes: _______________________________

[ ] Step 4: Assignment Center
    Status: PASS / FAIL
    Total Tasks: _____
    Departments: _____
    Notes: _______________________________

[ ] Step 5: Publish to Compliance
    Status: PASS / FAIL
    Published Count: _____
    Notes: _______________________________

[ ] Step 6: Admin Logout
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 7: Compliance Login
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 8: View Assigned Tasks
    Status: PASS / FAIL
    Task Count: _____
    Notes: _______________________________

[ ] Step 9: Mark Task Completed
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 10: Compliance Logout
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 11: Admin Login Again
    Status: PASS / FAIL
    Notes: _______________________________

[ ] Step 12: Dashboard Updated
    Status: PASS / FAIL
    Completed Count: _____
    Remaining Count: _____
    Notes: _______________________________

OVERALL RESULT: PASS / FAIL
Additional Comments: _______________________________
_______________________________
```

---

## 🎉 Success Indicators

You know the integration is working when:

1. ✅ Assignment Center populates automatically after pipeline
2. ✅ Departments see tasks after publish
3. ✅ Completion status updates in real-time
4. ✅ Admin dashboard reflects current state
5. ✅ No horizontal scrolling anywhere
6. ✅ All navigation links work
7. ✅ Role-based access control works
8. ✅ Console shows proper logs
9. ✅ No errors in browser console
10. ✅ No 404 or 500 errors

---

**Test Guide Complete. Ready for end-to-end verification.**
