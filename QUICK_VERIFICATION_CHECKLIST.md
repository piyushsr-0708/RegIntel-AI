# Quick Verification Checklist

**Purpose:** Verify stabilization fixes work correctly  
**Time Required:** 5-10 minutes

---

## ✅ Pre-Flight Check

Before testing, ensure:
- [ ] Backend running: `http://localhost:8000/docs`
- [ ] Frontend running: `http://localhost:5173`
- [ ] Database has seed data (at least 1 admin user, 5 departments)

---

## Test 1: Knowledge Graph Full Text (3 min)

**What was fixed:** Graph.jsx now queries database for requirement text

### Steps:
1. Login as admin (`admin` / `admin123`)
2. Navigate to "Knowledge Graph"
3. Ensure you're in **Global Graph** mode (not active session)
4. Click any **green requirement node** (ellipse shape)
5. In right panel, click "View Full Text →"

### Expected Result:
- ✅ Modal opens with requirement details
- ✅ Text, domain, priority all visible
- ✅ No alert saying "Text unavailable"

### If it fails:
- Check browser console for errors
- Check backend is running
- Verify endpoint exists: `GET /api/admin/requirements/by-semantic-id/{id}`

---

## Test 2: Dashboard Metrics Consistency (2 min)

**What was fixed:** All dashboard metrics now filter by `is_published=True`

### Steps:
1. Still logged in as admin
2. Navigate to "Admin Dashboard"
3. Note the following numbers:
   - Published MAPs: ___
   - Pending Tasks: ___
   - Completed Tasks: ___
   - Critical Priority: ___

4. Navigate to "Assignment Center"
5. Count unpublished assignments shown
6. Calculate: Total = Published + Unpublished

### Expected Result:
- ✅ Published MAPs = sum of published assignments across departments
- ✅ Pending Tasks = only published pending (not all pending)
- ✅ Completed Tasks = only published completed
- ✅ Math works: Published + Unpublished = Total in database

### If it fails:
- Check `backend/crud.py` line 289-299 has `is_published == True`
- Check `backend/crud.py` line 316 has `is_published == True` filter
- Restart backend after code changes

---

## Test 3: Complete Workflow (5 min)

**What was fixed:** All pages should agree on metrics throughout workflow

### Steps:

#### A. Upload & Process
1. Navigate to "Pipeline"
2. Upload any PDF file
3. Click "Initiate Processing Pipeline"
4. Wait for completion (~15 seconds)
5. Note: "Requirements created: ___" (should be 14)

#### B. Assignment Center
1. Navigate to "Assignment Center"
2. Count total MAPs: ___ (should be 14)
3. Count Compliance tasks: ___ (should be 5)
4. Click "Publish" on Compliance

#### C. Dashboard Check
1. Navigate to "Admin Dashboard"
2. Check metrics:
   - Published MAPs: ___ (should be 5)
   - Unpublished MAPs: ___ (should be 9)
   - Total = Published + Unpublished = 14 ✓

#### D. Department View
1. Logout
2. Login as `compliance` / `compliance123`
3. Navigate to "My Assignments"
4. Count tasks: ___ (should be 5)
5. Click "Mark Completed" on first task

#### E. Final Verification
1. Logout
2. Login as admin
3. Check "Admin Dashboard"
4. Verify table shows:
   - Compliance: Assigned=5, Completed=1, Remaining=4

### Expected Result:
- ✅ All pages show consistent numbers
- ✅ Dashboard = Assignment Center = Department View
- ✅ No JSON fallback used
- ✅ All metrics from database

### If it fails:
- Check which step shows wrong number
- Verify database updates are committed
- Check API responses in browser Network tab
- Restart both frontend and backend

---

## Test 4: Graph During Active Session (1 min)

**What was tested:** Ensure session mode still works

### Steps:
1. Login as admin
2. Upload and process a document (from Test 3 if already done)
3. After pipeline completes, navigate to "Knowledge Graph"
4. Should automatically show "Active Session" mode
5. Click a requirement node
6. Click "View Full Text"

### Expected Result:
- ✅ Modal opens with requirement text
- ✅ Text from session data (faster)
- ✅ No database query needed (check console)

---

## Test 5: Exit Analysis Session (1 min)

**What was tested:** Ensure exiting doesn't corrupt global metrics

### Steps:
1. From active session in graph
2. Click "Exit Analysis" button
3. Navigate to "Admin Dashboard"
4. Check metrics (Published MAPs, Pending, Completed)

### Expected Result:
- ✅ Dashboard shows global metrics (not session metrics)
- ✅ Numbers match Assignment Center
- ✅ No corruption of global state

---

## Quick Pass/Fail Checklist

| Test | Status | Notes |
|------|--------|-------|
| 1. Graph Full Text (Global) | ☐ PASS / ☐ FAIL | |
| 2. Dashboard Metric Consistency | ☐ PASS / ☐ FAIL | |
| 3. Complete Workflow | ☐ PASS / ☐ FAIL | |
| 4. Graph During Session | ☐ PASS / ☐ FAIL | |
| 5. Exit Analysis | ☐ PASS / ☐ FAIL | |

---

## Common Issues & Quick Fixes

### Issue: "Text unavailable" still shows
**Fix:** Clear browser cache, hard refresh (Ctrl+Shift+R)

### Issue: Metrics don't match across pages
**Fix:** Check backend filters have `is_published == True`, restart server

### Issue: Import error on backend startup
**Fix:** Verify `backend/routers/admin_router.py` imports `get_current_active_user`

### Issue: Graph node click doesn't work
**Fix:** Check browser console, ensure API endpoint `/admin/requirements/by-semantic-id/{id}` exists

---

## Success Criteria

**All 5 tests PASS** = Stabilization complete ✅

If any test fails, check:
1. Backend logs for errors
2. Browser console for errors  
3. Network tab for failed API calls
4. Database state (use SQL queries from verification docs)

---

**Checklist Complete. Ready for testing.**
