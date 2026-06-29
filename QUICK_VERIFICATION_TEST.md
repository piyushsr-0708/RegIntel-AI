# QUICK VERIFICATION TEST
**Run this 3-minute test before the demo**

---

## Prerequisites

1. Backend running: `cd backend && python -m uvicorn main:app --reload --port 8000`
2. Frontend running: `cd frontend/dashboard && npm run dev`
3. Browser open: `http://localhost:5173`

---

## Test 1: Assignment Center Renders (30 seconds)

### Steps:
1. Login as `admin` / `admin123`
2. Click "Assignment Center" in navigation

### Expected Result:
- ✅ Page renders (not blank!)
- ✅ Shows either "No Assignments to Review" OR department list
- ✅ No console errors

### Fail Criteria:
- ❌ Blank white page
- ❌ Console error: "useAnalysisSession is not defined"

---

## Test 2: Pipeline Shows Correct Counts (1 minute)

### Steps:
1. From dashboard, click "Pipeline"
2. Upload any PDF file
3. Click "Start Processing"
4. Watch pipeline stages
5. Note stage 2 and stage 3 outputs

### Expected Result:
- ✅ Stage 2: "X requirements found" (some number)
- ✅ Stage 3: "Y Assignments created" (some number)
- ✅ X and Y are different numbers (not duplicates)

### Fail Criteria:
- ❌ Stage 2 and 3 show same text
- ❌ Shows "0 requirements" or "0 Assignments"
- ❌ Stage 3 says "requirements found" instead of "Assignments created"

---

## Test 3: Complete Workflow (90 seconds)

### Steps:
1. After pipeline completes, click "Assignment Center"
2. Note the total number shown (e.g., "14 Total MAPs")
3. Click "Publish" on first department
4. Wait for success message
5. Check dashboard

### Expected Result:
- ✅ Assignment Center shows correct total
- ✅ Publish succeeds without errors
- ✅ Dashboard shows published count > 0
- ✅ No blank pages at any step

### Fail Criteria:
- ❌ Assignment Center shows 0
- ❌ Publish fails
- ❌ Dashboard doesn't update

---

## Quick Check Results

| Test | Status | Notes |
|------|--------|-------|
| 1. Assignment Center Renders | ☐ PASS / ☐ FAIL | |
| 2. Pipeline Counts Correct | ☐ PASS / ☐ FAIL | |
| 3. Workflow Complete | ☐ PASS / ☐ FAIL | |

**All Pass?** → ✅ Ready for demo!

**Any Fail?** → Check console errors and refer to HOTFIX_REPORT.md

---

## If Tests Fail

### Assignment Center Blank:
- Check browser console for error
- Verify import in AssignmentCenter.jsx line 3
- Hard refresh: Ctrl+Shift+R

### Pipeline Shows Wrong Text:
- Check Pipeline.jsx line 547-548
- Should see `requirements_created` on 548, `assignments_created` on 549
- Clear browser cache

### Workflow Broken:
- Check backend is running: `http://localhost:8000/api/health`
- Check frontend is running: `http://localhost:5173`
- Try logging out and back in

---

**Total Test Time:** 3 minutes

