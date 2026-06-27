# Pre-Demo Testing Checklist

**Complete this checklist the night before the demo**

---

## ⚙️ Environment Setup

- [ ] **Backend Dependencies Installed**
  ```bash
  cd backend
  pip list | grep -i fastapi  # Should show fastapi, sqlalchemy, etc.
  ```

- [ ] **Frontend Dependencies Installed**
  ```bash
  cd frontend/dashboard
  npm list react  # Should show react version
  ```

- [ ] **Database Exists**
  ```bash
  ls backend/data/compliance.db  # File should exist
  ```

- [ ] **Python Version OK**
  ```bash
  python --version  # Should be 3.9 or higher
  ```

- [ ] **Node Version OK**
  ```bash
  node --version  # Should be 16 or higher
  ```

---

## 🚀 Startup Tests

- [ ] **Backend Starts Successfully**
  ```bash
  cd backend
  uvicorn main:main --reload
  ```
  - No errors in console
  - Shows "Backend is ready!" message
  - Accessible at http://localhost:8000
  - API docs load at http://localhost:8000/api/docs

- [ ] **Frontend Starts Successfully**
  ```bash
  cd frontend/dashboard
  npm run dev
  ```
  - No errors in console
  - Shows Vite dev server message
  - Accessible at http://localhost:5173

- [ ] **Both Running Simultaneously**
  - Backend in Terminal 1
  - Frontend in Terminal 2
  - Both stay running without crashes

---

## 🔐 Authentication Tests

### Test 1: Admin Login
- [ ] Navigate to http://localhost:5173
- [ ] See login page (not error page)
- [ ] Enter: admin / admin123
- [ ] Click Login
- [ ] Redirects to Dashboard (not error)
- [ ] Top-right shows "admin" username
- [ ] Logout button visible

### Test 2: Department Login
- [ ] Logout from admin
- [ ] Enter: compliance / compliance123
- [ ] Click Login
- [ ] Redirects to workspace (or dashboard)
- [ ] Top-right shows "compliance" username
- [ ] Sidebar different from admin

### Test 3: Invalid Login
- [ ] Logout
- [ ] Enter: wrong / wrong
- [ ] Click Login
- [ ] Shows error message
- [ ] Stays on login page

---

## 📤 Pipeline Tests

### Test 4: Upload and Process
- [ ] Login as admin
- [ ] Click **Pipeline** in sidebar
- [ ] See upload interface
- [ ] Drag/drop or select PDF from `data/dataset/rbi/kyc/KYC09062025.pdf`
- [ ] File name appears
- [ ] Click "Initiate Processing Pipeline"
- [ ] Progress bar animates
- [ ] Shows all 9 stages
- [ ] Completes without errors (takes ~10-15 seconds)
- [ ] Shows "Processing Complete" message
- [ ] Displays statistics:
  - Requirements Extracted: >0
  - Departments Impacted: >0
  - Critical MAPs: >0
  - Knowledge Graph: nodes + edges

### Test 5: Pipeline Results
- [ ] After pipeline completes:
- [ ] See "AI Executive Briefing" section
- [ ] See "Department Impact Analysis" cards
- [ ] See "Generated MAPs" list
- [ ] See "Requirement Summary"
- [ ] See "Knowledge Graph Summary"
- [ ] All numbers are non-zero

---

## 📋 Assignment Center Tests

### Test 6: View Assignment Center
- [ ] Still logged in as admin
- [ ] Click **Assignment Center** in sidebar
- [ ] Page loads without errors
- [ ] See total MAPs count (should match pipeline output)
- [ ] See department cards:
  - Compliance department visible
  - Shows task count >0
  - Shows "Publish" button
  - Other departments may show with 0 or >0 tasks

### Test 7: Publish to Department
- [ ] Click **Publish** button next to Compliance
- [ ] Button shows "Publishing..."
- [ ] Alert appears: "Assignments published successfully!"
- [ ] Alert dismisses
- [ ] Page reloads/updates
- [ ] Compliance department still visible

### Test 8: Publish to Multiple Departments
- [ ] If other departments show tasks:
- [ ] Click Publish on another department (e.g., Cyber Security)
- [ ] Should work same as Compliance
- [ ] No errors

---

## 👤 Department Workspace Tests

### Test 9: View My Tasks
- [ ] Logout from admin
- [ ] Login as: compliance / compliance123
- [ ] Sidebar shows "My Assignments" (NOT "Pipeline")
- [ ] Click **My Assignments** or auto-redirects
- [ ] See summary cards:
  - Total Tasks: >0
  - Completed: 0
  - Remaining: >0
- [ ] See task cards below
- [ ] Each task card shows:
  - Priority badge (color-coded)
  - Domain
  - Requirement text
  - "Mark Completed" button

### Test 10: Mark Task Completed
- [ ] Click **Mark Completed** on first task
- [ ] Button shows "Updating..."
- [ ] Alert: "Task marked as completed!"
- [ ] Page reloads/updates
- [ ] Task card background changes (greenish)
- [ ] Shows "✓ Completed on [date]"
- [ ] Summary updates:
  - Completed: 1
  - Remaining: decreased by 1

### Test 11: Complete Multiple Tasks
- [ ] Mark 2-3 more tasks completed
- [ ] Each works independently
- [ ] Summary counts update correctly

### Test 12: Unpublished Department
- [ ] Logout
- [ ] Login as: risk / risk123
- [ ] If no tasks published to Risk:
- [ ] Should see "No Tasks Assigned Yet" message
- [ ] No errors

---

## 📊 Admin Dashboard Tests

### Test 13: View Completion Summary
- [ ] Logout from department user
- [ ] Login as: admin / admin123
- [ ] Navigate to **Executive Dashboard**
- [ ] Scroll down to "Department Assignment Status" table
- [ ] Table should show:
  - Compliance row visible
  - Assigned: >0
  - Completed: matches number completed in Test 10-11
  - Remaining: Assigned - Completed
  - Progress bar: correct percentage
  - Other departments show 0 if not published

### Test 14: Real-Time Update
- [ ] Note current Compliance completion count
- [ ] Logout
- [ ] Login as compliance
- [ ] Mark 1 more task completed
- [ ] Logout
- [ ] Login as admin
- [ ] Go to Dashboard
- [ ] Compliance completion count increased by 1
- [ ] Progress bar updated

---

## 🧭 Navigation Tests

### Test 15: Admin Navigation
- [ ] Login as admin
- [ ] Sidebar shows these items:
  - Executive Dashboard
  - Pipeline
  - Assignment Center ← NEW
  - MAP Management
  - Department Risk
  - Requirement Search
  - Knowledge Graph
- [ ] Click each link:
- [ ] All pages load without 404
- [ ] No console errors

### Test 16: Department Navigation
- [ ] Login as compliance
- [ ] Sidebar shows these items:
  - My Assignments ← NEW (or just "Assignments")
  - Requirement Search
  - Knowledge Graph
- [ ] Does NOT show:
  - Pipeline
  - Upload
  - Assignment Center
  - Department Risk
  - MAP Management
- [ ] Click each available link
- [ ] All pages load

---

## 🔍 Search & Graph Tests

### Test 17: Requirement Search
- [ ] Login as any user
- [ ] Click **Requirement Search**
- [ ] See search interface
- [ ] Type "customer" in search box
- [ ] Results appear
- [ ] Click a result
- [ ] Detail view opens

### Test 18: Knowledge Graph
- [ ] Click **Knowledge Graph**
- [ ] Graph renders (may take a moment)
- [ ] See nodes and edges
- [ ] Can zoom in/out
- [ ] Can drag nodes
- [ ] Search bar works
- [ ] Filter by department works

---

## 🚨 Error Handling Tests

### Test 19: Network Errors
- [ ] Stop backend server
- [ ] Try to mark task completed (frontend still running)
- [ ] Should show error message (not crash)
- [ ] Restart backend
- [ ] Try again - should work

### Test 20: Invalid Actions
- [ ] Login as department user
- [ ] Manually navigate to: http://localhost:5173/assignment-center
- [ ] Should show 403 error or redirect (not crash)

### Test 21: Browser Console
- [ ] Open browser console (F12)
- [ ] Navigate through all pages as admin
- [ ] No red errors in console
- [ ] Repeat as department user
- [ ] No red errors in console

---

## 📱 UI/UX Tests

### Test 22: Visual Consistency
- [ ] All cards have consistent styling
- [ ] Buttons have hover effects
- [ ] Colors match theme (dark blue/green)
- [ ] Text is readable
- [ ] No layout breaking
- [ ] No overlapping elements

### Test 23: Loading States
- [ ] Pipeline shows loading animation
- [ ] Publish button shows "Publishing..."
- [ ] Mark Completed shows "Updating..."
- [ ] Dashboard shows "Loading..." if slow

### Test 24: Empty States
- [ ] Login as unpublished department
- [ ] See "No Tasks Assigned Yet" message
- [ ] Message is clear and helpful

---

## 🔄 Full Workflow Test (Most Important!)

### Test 25: Complete Demo Flow
- [ ] **Step 1:** Login as admin
- [ ] **Step 2:** Upload RBI circular
- [ ] **Step 3:** Pipeline completes successfully
- [ ] **Step 4:** Navigate to Assignment Center
- [ ] **Step 5:** See department distribution
- [ ] **Step 6:** Publish to Compliance
- [ ] **Step 7:** Logout
- [ ] **Step 8:** Login as compliance
- [ ] **Step 9:** See assigned tasks
- [ ] **Step 10:** Mark task completed
- [ ] **Step 11:** Logout
- [ ] **Step 12:** Login as admin
- [ ] **Step 13:** Dashboard shows updated count

**This is THE demo flow. If this works end-to-end, demo is ready!**

---

## 📸 Screenshot Checklist (Backup)

Take screenshots of:
- [ ] Login page
- [ ] Admin dashboard
- [ ] Pipeline page (processing)
- [ ] Pipeline results
- [ ] Assignment Center
- [ ] Department workspace with tasks
- [ ] Completed task
- [ ] Admin completion summary table
- [ ] Knowledge graph

**Save in folder: `demo_screenshots/`**

---

## 🎥 Video Recording (Optional)

- [ ] Record complete workflow using OBS/screen recorder
- [ ] Save as: `demo_recording.mp4`
- [ ] Test playback
- [ ] Upload to Google Drive/Dropbox as backup

---

## ✅ Final Checks

- [ ] All tests above passed
- [ ] No red flags or concerns
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] Database has seed data
- [ ] Complete workflow works end-to-end
- [ ] Screenshots taken
- [ ] Know default credentials by heart
- [ ] Can explain workflow clearly
- [ ] Comfortable with troubleshooting

---

## 🚨 If Any Test Fails

1. **Document the failure** - What broke? What error?
2. **Check console logs** - Backend terminal + Browser console
3. **Check database** - Delete and recreate if corrupted
4. **Reinstall dependencies** - npm install / pip install
5. **Check this implementation report** - Follow setup exactly
6. **Test again** - Repeat failed test

---

## 📝 Test Results

**Date Tested:** ______________  
**Tested By:** ______________  
**Backend Version:** ______________  
**Frontend Version:** ______________  

**Tests Passed:** _____ / 25  
**Tests Failed:** _____  
**Critical Issues:** _____  

**Overall Status:** 
- [ ] ✅ READY FOR DEMO
- [ ] ⚠️ MINOR ISSUES (document below)
- [ ] ❌ NOT READY (fix issues)

**Notes:**
```
(Add any notes, concerns, or issues here)
```

---

**Checklist Complete. Demo Ready! 🚀**
