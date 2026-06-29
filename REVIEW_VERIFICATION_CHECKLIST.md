# STAKEHOLDER REVIEW - VERIFICATION CHECKLIST

**Run these tests before the review to verify all fixes**

---

## Test 1: Pipeline Shows Backend Counts (2 min)

### Steps:
1. Login as admin
2. Navigate to Pipeline
3. Upload test1.pdf
4. Wait for processing
5. Note the numbers in pipeline stages
6. Start new analysis
7. Upload test2.pdf (different file)
8. Note the numbers again

### Expected:
- ✅ Pipeline stages show: "X requirements found", "Y assignments created"
- ✅ X and Y should match backend console logs
- ✅ Different files may show different counts

### Fail Criteria:
- ❌ Always shows same numbers (314, 320, etc.)
- ❌ Shows "pages extracted" instead of requirements

---

## Test 2: Dashboard Mode Clarity (1 min)

### Steps:
1. After pipeline completes, navigate to Dashboard
2. Check header and KPI labels
3. Click "Exit Analysis"
4. Check header and KPI labels again

### Expected:
**During Session:**
- ✅ Header: "Analysis Dashboard"
- ✅ Subtitle: "Document Analysis Preview · [filename]"
- ✅ Status: "ANALYSIS MODE - Preview Only - ● Analysis"
- ✅ KPIs: "Requirements Extracted", "Assignments Generated"

**After Exit:**
- ✅ Header: "Executive Dashboard"
- ✅ Subtitle: "RBI Compliance Intelligence · Real-time Regulatory Analytics"
- ✅ Status: "LAST UPDATED - [date] - ● Live"
- ✅ KPIs: "Published Assignments", "Draft Assignments", "Pending Tasks", "Completed Tasks"

### Fail Criteria:
- ❌ Headers don't change
- ❌ Same KPI labels in both modes

---

## Test 3: Assignment Center Reloads After Exit (2 min)

### Steps:
1. Upload document, complete pipeline
2. Navigate to Assignment Center
3. Note the count (should be 14 or similar)
4. Exit Analysis from Dashboard
5. Go back to Assignment Center
6. Note the count again

### Expected:
- ✅ Assignment Center shows same count both times
- ✅ Console logs: "[ASSIGNMENT_CENTER] Loading summary from backend (session state: false)"
- ✅ No stale data message
- ✅ Count matches database

### Fail Criteria:
- ❌ Count changes after exit
- ❌ Shows "34 Tasks" from previous session
- ❌ Assignment Center doesn't reload

---

## Test 4: Session Isolation (3 min)

### Steps:
1. Upload fileA.pdf, complete pipeline
2. Note stats (X requirements, Y assignments)
3. Navigate to Dashboard (session mode)
4. Exit Analysis
5. Navigate to Pipeline
6. Upload fileB.pdf, complete pipeline
7. Note stats again

### Expected:
- ✅ FileB shows its own stats (may differ from fileA)
- ✅ Dashboard resets to operational mode between uploads
- ✅ No fileA data visible during fileB analysis
- ✅ Console shows: "[PIPELINE] Starting new analysis - clearing previous session"

### Fail Criteria:
- ❌ FileA stats appear during fileB analysis
- ❌ Dashboard still shows fileA info
- ❌ Stale session banner

---

## Test 5: Operational Dashboard Uses Database (2 min)

### Steps:
1. Ensure no active session (Exit Analysis if needed)
2. Navigate to Dashboard
3. Note all KPI values
4. Navigate to Assignment Center
5. Publish Compliance department
6. Return to Dashboard
7. Note KPI values again

### Expected:
- ✅ Published Assignments increases
- ✅ Draft Assignments decreases
- ✅ Departments Impacted increases
- ✅ Department table shows Compliance row
- ✅ No demo JSON values (205, 2941)

### Fail Criteria:
- ❌ Values don't change after publish
- ❌ Shows 205 or 2941 (demo JSON)
- ❌ Department table empty

---

## Test 6: Complete Workflow Consistency (5 min)

### Steps:
1. Login as admin
2. Upload → Pipeline (note: X requirements, Y assignments)
3. Assignment Center (should show Y total)
4. Publish to Compliance (should publish ~5)
5. Dashboard operational mode:
   - Published = ~5
   - Draft = Y - 5
6. Logout, login as compliance
7. My Assignments (should show ~5 tasks)
8. Complete 1 task
9. Logout, login as admin
10. Dashboard: Completed = 1

### Expected:
- ✅ All numbers consistent throughout
- ✅ Y from pipeline = Total in Assignment Center
- ✅ Published + Draft = Y
- ✅ Compliance sees what was published
- ✅ Completed count updates

### Fail Criteria:
- ❌ Numbers don't match
- ❌ Assignment Center shows different total than pipeline
- ❌ Dashboard shows wrong published count

---

## Test 7: Console Logging Verification (during any test)

### Expected Console Logs:

**During Upload:**
```
[PIPELINE] Starting pipeline for file: [filename]
[PIPELINE] File uploaded, document ID: X
[PIPELINE] Visual stages complete, calling process endpoint...
[PIPELINE] Processing complete: {requirements_created: X, assignments_created: Y}
[PIPELINE] Pipeline successfully completed
```

**During Exit:**
```
[SESSION] Clearing analysis session
[PIPELINE] Starting new analysis - clearing previous session
```

**Assignment Center Load:**
```
[ASSIGNMENT_CENTER] Loading summary from backend (session state: true/false)
[ASSIGNMENT_CENTER] Summary loaded: {total_maps: X, departments: [...]}
```

### Fail Criteria:
- ❌ Missing logs
- ❌ Errors in console
- ❌ Wrong values logged

---

## Quick Pass/Fail Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Pipeline Backend Counts | ☐ PASS / ☐ FAIL | |
| 2. Dashboard Mode Clarity | ☐ PASS / ☐ FAIL | |
| 3. Assignment Center Reload | ☐ PASS / ☐ FAIL | |
| 4. Session Isolation | ☐ PASS / ☐ FAIL | |
| 5. Operational Dashboard | ☐ PASS / ☐ FAIL | |
| 6. Complete Workflow | ☐ PASS / ☐ FAIL | |
| 7. Console Logging | ☐ PASS / ☐ FAIL | |

**All Pass?** → ✅ Ready for stakeholder review

---

## Known Limitations (Acceptable for Review)

1. **Department Impact cards in Pipeline show zero**
   - Workaround: Use Assignment Center instead
   - Explain: "Assignments visible in Assignment Center for review"

2. **Analysis preview uses representative structure**
   - Workaround: Stats are accurate, lists are preview
   - Explain: "AI analysis preview before publishing"

3. **Department reports require published assignments**
   - Workaround: Publish first, then view reports
   - Explain: "Reports show operational published tasks"

---

## If Tests Fail

### Pipeline shows hardcoded numbers:
- Check: Did backend response get captured?
- Fix: Verify `setBackendResponse(processResponse.data)` is called
- Check browser console for backend response

### Dashboard doesn't distinguish modes:
- Check: Is session active? (should see banner)
- Fix: Hard refresh browser (Ctrl+Shift+R)
- Check: `isSessionMode` flag value

### Assignment Center shows stale data:
- Check: Console logs for reload trigger
- Fix: Navigate away and back to force reload
- Check: `hasSession` dependency in useEffect

### Session data persists:
- Check: Console for "[SESSION] Clearing analysis session"
- Fix: Click "Exit Analysis" button explicitly
- Check: Session banner disappears

---

**VERIFICATION CHECKLIST COMPLETE**
