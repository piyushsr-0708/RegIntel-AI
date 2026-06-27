# Test MVP Fixes - Quick Verification Guide

**Use this guide to test all fixes systematically**

---

## 🚀 Setup (2 minutes)

### Terminal 1 - Start Backend
```bash
cd backend
uvicorn main:main --reload
```

**Wait for:**
```
✓ Backend is ready!
✓ API Documentation: http://localhost:8000/api/docs
```

### Terminal 2 - Start Frontend
```bash
cd frontend/dashboard
npm run dev
```

**Wait for:**
```
➜  Local:   http://localhost:5173/
```

---

## ✅ Test 1: Layout & Navigation (2 minutes)

### Admin View

1. **Open:** http://localhost:5173
2. **Login:** `admin` / `admin123`
3. **Check Sidebar (LEFT):**
   - ✅ Logo visible
   - ✅ "Executive Dashboard"
   - ✅ "Pipeline"
   - ✅ "Assignment Center" ← **NEW - Must be visible!**
   - ✅ "MAP Management"
   - ✅ "Department Risk"
   - ✅ "Requirement Search"
   - ✅ "Knowledge Graph"

4. **Check Topbar (TOP):**
   - ✅ "RegIntel AI" logo
   - ✅ "Compliance Platform" subtitle
   - ✅ LIVE badge
   - ✅ User avatar with "admin"
   - ✅ NO "Demo" button ← **Must be removed!**
   - ✅ NO navigation links ← **Must be in sidebar!**

5. **Check Layout:**
   - ✅ No horizontal scrollbar
   - ✅ Page fits screen width
   - ✅ Sidebar stays on left
   - ✅ Content area scrolls vertically only

6. **Resize Browser:**
   - Make window smaller
   - ✅ Still no horizontal scroll
   - ✅ Layout adapts properly

**PASS:** ✅ All items checked  
**FAIL:** ❌ Any item missing → Check `App.jsx` and `Topbar.jsx`

---

## ✅ Test 2: Assignment Center Visibility (3 minutes)

### Admin Can Access

1. **Still logged in as admin**
2. **Click "Assignment Center" in sidebar**
3. **URL changes to:** `/assignment-center`
4. **Page loads without errors**

**Expected:** Assignment Center page appears

**If Empty:**
- This is OK if no pipeline has run yet
- Shows "No Assignments to Review"

**If Has Data:**
- Shows "Total MAPs Across X Departments"
- Shows department cards
- Each has "Publish" button

**PASS:** ✅ Page loads, URL correct  
**FAIL:** ❌ 404 or error → Check route in `App.jsx`

### Department Cannot Access

1. **Logout** (user menu top-right)
2. **Login:** `compliance` / `compliance123`
3. **Check Sidebar:**
   - ✅ "My Assignments" (first item)
   - ✅ "Requirement Search"
   - ✅ "Knowledge Graph"
   - ❌ NO "Assignment Center" ← **Must NOT be visible**
   - ❌ NO "Pipeline" ← **Must NOT be visible**
   - ❌ NO "MAP Management" ← **Must NOT be visible**

4. **Try direct URL:** http://localhost:5173/assignment-center
5. **Expected:** Redirects or shows access denied

**PASS:** ✅ Department users don't see/access Assignment Center  
**FAIL:** ❌ Can access → Check `Sidebar.jsx` role logic

---

## ✅ Test 3: Create & Publish Workflow (5 minutes)

### Upload & Process

1. **Logout, login as:** `admin` / `admin123`
2. **Navigate to:** Pipeline
3. **Upload file:** Any PDF from `data/dataset/rbi/kyc/`
   - Example: `KYC09062025.pdf`
4. **Click:** "Initiate Processing Pipeline"
5. **Wait:** ~10-15 seconds for completion
6. **Check:** "Processing Complete" message appears

**PASS:** ✅ Pipeline completes successfully  
**FAIL:** ❌ Errors → Check backend logs

### View Assignment Center

1. **Navigate to:** Assignment Center (sidebar)
2. **Check page loads:**
   - ✅ Shows "Total MAPs" count
   - ✅ Shows department cards
   - ✅ Each card has count > 0
   - ✅ Each card has "Publish" button
   - ✅ Department names visible (Compliance, Cyber Security, etc.)

**PASS:** ✅ Departments with tasks visible  
**FAIL:** ❌ Empty → Check `get_unpublished_assignment_summary()` in `crud.py`

### Publish to Department

1. **Find "Compliance" card**
2. **Note the task count** (e.g., "134 Tasks")
3. **Click "Publish" button**
4. **Wait for response:**
   - ✅ Alert: "Assignments published successfully!"
   - ✅ Button shows "Publishing..." briefly
   - ✅ No errors in console (F12)

5. **Check browser console (F12):**
   - ✅ POST request to `/api/assignment-center/publish`
   - ✅ Response status: 200
   - ✅ Response body: `{"status":"success", "published_count": X}`

**PASS:** ✅ Publish works, alert appears, no errors  
**FAIL:** ❌ Errors → Check `publish_department_assignments()` in `crud.py`

---

## ✅ Test 4: Department Views Tasks (3 minutes)

1. **Logout from admin**
2. **Login as:** `compliance` / `compliance123`
3. **Check Sidebar:**
   - ✅ First item: "My Assignments"
   - ❌ NO "Pipeline" or "Assignment Center"

4. **Click "My Assignments"** (or auto-redirects)
5. **Check page:**
   - ✅ Shows "My Assignments - Compliance Dashboard"
   - ✅ Summary cards: Total | Completed | Remaining
   - ✅ Total > 0 (matching published count)
   - ✅ Completed = 0 (initially)
   - ✅ Task cards below summary

6. **Check task cards:**
   - ✅ Priority badge (Critical/High/Medium/Low) with color
   - ✅ Domain label (e.g., "KYC", "AML")
   - ✅ Requirement text visible
   - ✅ "Mark Completed" button present
   - ✅ Assigned date shown

**PASS:** ✅ All tasks visible, properly formatted  
**FAIL:** ❌ No tasks → Check if published, check `get_published_assignments_for_department()`

---

## ✅ Test 5: Mark Task Completed (2 minutes)

1. **Still on My Assignments page**
2. **Pick first task card**
3. **Click "Mark Completed" button**
4. **Wait for response:**
   - ✅ Alert: "Task marked as completed!"
   - ✅ Button shows "Updating..." briefly
   - ✅ Page refreshes or updates

5. **Check task card:**
   - ✅ Background changes (greenish tint)
   - ✅ Status shows "✓ Completed on [date]"
   - ✅ Button removed or disabled

6. **Check summary cards:**
   - ✅ Total: unchanged
   - ✅ Completed: increased by 1
   - ✅ Remaining: decreased by 1

7. **Mark 2-3 more tasks completed**
8. **Check counts update each time**

**PASS:** ✅ Status updates, counts change, no errors  
**FAIL:** ❌ Errors → Check `mark_assignment_completed()` in `crud.py`

---

## ✅ Test 6: Admin Sees Updates (2 minutes)

1. **Logout from compliance**
2. **Login as:** `admin` / `admin123`
3. **Navigate to:** Executive Dashboard
4. **Scroll down** to find table
5. **Look for:** "Department Assignment Status" section

**Check table shows:**
```
Department     | Assigned | Completed | Remaining | Progress
------------------------------------------------------------
Compliance     |   134    |     3     |    131    |   2%
Cyber Security |    0     |     0     |      0    |   -
Treasury       |    0     |     0     |      0    |   -
...
```

6. **Verify:**
   - ✅ Compliance row present
   - ✅ Assigned = number you published
   - ✅ Completed = number you marked (3-4)
   - ✅ Remaining = Assigned - Completed
   - ✅ Progress bar shows percentage
   - ✅ Other departments show 0 (if not published)

**PASS:** ✅ Real counts from database, updates visible  
**FAIL:** ❌ Wrong counts → Check `get_admin_completion_summary()` in `crud.py`

---

## ✅ Test 7: Complete End-to-End (5 minutes)

**Full workflow in one go:**

1. **Admin:** Upload new circular
2. **Admin:** Pipeline processes
3. **Admin:** Assignment Center → Publish to Cyber Security
4. **Logout**
5. **Login:** `cyber` / `cyber123`
6. **Cyber:** See assigned tasks
7. **Cyber:** Mark 2 tasks completed
8. **Logout**
9. **Admin:** Check dashboard
10. **Verify:** Cyber Security row shows 2 completed

**PASS:** ✅ Complete flow works without errors  
**FAIL:** ❌ Any step fails → Check specific component

---

## 🚨 Common Issues & Fixes

### Issue: Horizontal scroll still appears
**Fix:** Hard refresh browser (Ctrl+Shift+R), clear cache

### Issue: Assignment Center shows "No assignments"
**Fix:** Run pipeline first, or check `get_unpublished_assignment_summary()` logic

### Issue: Publish button does nothing
**Fix:** Check browser console (F12) for errors, check network tab

### Issue: Department sees Pipeline/Assignment Center
**Fix:** Check `user.role` in Sidebar, verify role is `department` not `head_office`

### Issue: Mark Completed fails with enum error
**Fix:** Verify `ComplianceStatus.COMPLETED` enum usage in backend

### Issue: Dashboard shows 0 for all counts
**Fix:** Check `is_published=True` filter, verify assignments published

### Issue: "Demo" button still visible
**Fix:** Hard refresh, verify Topbar.jsx changes applied

---

## 📊 Test Results Template

```
==============================================
MVP FIX TESTING REPORT
==============================================

Date: __________________
Tester: ________________

TEST 1: Layout & Navigation
[ ] Admin sidebar correct
[ ] Department sidebar correct  
[ ] No horizontal scroll
[ ] Demo button removed
Status: PASS / FAIL

TEST 2: Assignment Center
[ ] Visible for admin
[ ] Not visible for department
[ ] Page loads correctly
Status: PASS / FAIL

TEST 3: Publish Workflow
[ ] Pipeline completes
[ ] Assignment Center shows data
[ ] Publish button works
[ ] No errors
Status: PASS / FAIL

TEST 4: Department View
[ ] My Assignments visible
[ ] Tasks displayed
[ ] Proper formatting
Status: PASS / FAIL

TEST 5: Mark Completed
[ ] Button works
[ ] Status updates
[ ] Counts update
Status: PASS / FAIL

TEST 6: Admin Dashboard
[ ] Table visible
[ ] Real counts shown
[ ] Updates reflect
Status: PASS / FAIL

TEST 7: End-to-End
[ ] Complete workflow works
[ ] No errors
Status: PASS / FAIL

==============================================
OVERALL: PASS / FAIL
==============================================

Notes:
_____________________________________________
_____________________________________________
_____________________________________________
```

---

## ✅ Success Criteria

**MVP is ready for demo if:**
- ✅ All 7 tests PASS
- ✅ No horizontal scrolling anywhere
- ✅ Assignment Center visible for admin only
- ✅ Publish creates and shows tasks
- ✅ Department sees only their tasks
- ✅ Mark completed updates counts
- ✅ Admin dashboard shows real data
- ✅ No console errors (F12)

**If all checked → 🎉 MVP is demo-ready!**

---

**Testing complete. Report any failures with details.**
