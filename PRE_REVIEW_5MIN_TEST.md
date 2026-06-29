# 5-MINUTE PRE-REVIEW TEST

**Run this immediately before stakeholder review**

---

## Test 1: Pipeline Backend Counts (90 seconds)

1. Login: admin / admin123
2. Pipeline → Upload test.pdf
3. Wait for "Analysis Complete"
4. Look at pipeline stages

**✅ PASS IF:** Shows "X requirements found" and "Y assignments created" (not 314, 320)  
**❌ FAIL IF:** Shows hardcoded "314 pages", "320 requirements"

---

## Test 2: Dashboard Mode Labels (60 seconds)

1. After pipeline, go to Dashboard
2. Check header

**✅ PASS IF:**  
- Header says "Analysis Dashboard"
- Subtitle says "Document Analysis Preview · [filename]"
- Status says "ANALYSIS MODE - Preview Only"
- KPIs say "Requirements Extracted", "Assignments Generated"

3. Click "Exit Analysis"
4. Check header again

**✅ PASS IF:**  
- Header says "Executive Dashboard"
- Status says "LAST UPDATED - [date] - ● Live"
- KPIs say "Published Assignments", "Draft Assignments"

**❌ FAIL IF:** Same labels in both modes

---

## Test 3: Assignment Center Reload (60 seconds)

1. Upload document (if not already done)
2. Go to Assignment Center → note count
3. Go to Dashboard → Exit Analysis
4. Go to Assignment Center again

**✅ PASS IF:**  
- Count is same both times
- Page reloads (check console)

**❌ FAIL IF:** Shows different count or "34 Tasks"

---

## Test 4: Complete Workflow (90 seconds)

1. Assignment Center → Publish Compliance
2. Dashboard → Check "Published Assignments" increased
3. Logout → Login as compliance/compliance123
4. My Assignments → Check shows tasks
5. Mark one complete
6. Logout → Login as admin
7. Dashboard → Check "Completed Tasks" = 1

**✅ PASS IF:** All steps show correct numbers  
**❌ FAIL IF:** Any step shows zero or wrong count

---

## Test 5: Console Clean (30 seconds)

Open browser console (F12)

**✅ PASS IF:**  
- No red errors
- Logs show "[PIPELINE]", "[ASSIGNMENT_CENTER]", "[SESSION]"

**❌ FAIL IF:** Red errors or stack traces

---

## PASS/FAIL

All 5 tests pass? → ✅ **START REVIEW**  
Any test fails? → ❌ **INVESTIGATE FIRST**

---

## QUICK FIXES

**Pipeline shows 314/320:** Check backend response captured  
**Dashboard same labels:** Hard refresh (Ctrl+Shift+R)  
**Assignment Center stale:** Navigate away and back  
**Workflow broken:** Restart backend  
**Console errors:** Check backend running on port 8000

---

**TOTAL TIME: 5 MINUTES**
