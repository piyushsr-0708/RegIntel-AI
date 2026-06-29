# ANALYSISRESULT VERIFICATION SCRIPT

## Quick 3-Minute Verification

### Prerequisites
```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend/dashboard
npm run dev
```

---

### Test: Upload → Verify Consistency

1. **Open Browser:** http://localhost:5173
2. **Login:** admin / admin123
3. **Navigate to Pipeline**
4. **Upload:** Any PDF file
5. **Click:** "Start Processing"
6. **Wait:** For all 9 stages to complete

---

### Verification Points

#### ✅ Pipeline Results Page
- Look for: "X requirements found"
- Look for: "Y Assignments created"
- Look for: "Z departments impacted"
- **Write down these numbers:** X=___ Y=___ Z=___

#### ✅ Browser Console
- Look for: `[ANALYSIS_RESULT] Built AnalysisResult`
- Look for: `fromBackend: true`
- If you see `fromBackend: false` → Backend endpoint failed, using demo fallback

#### ✅ Navigate to Dashboard
- Verify: "Requirements Extracted: X" (same as Pipeline)
- Verify: "Assignments Generated: Y" (same as Pipeline)  
- Verify: "Departments Impacted: Z" (same as Pipeline)
- **ALL NUMBERS MUST MATCH PIPELINE**

#### ✅ Navigate to Assignment Center
- Verify: "Y Total MAPs Across Z Departments"
- **MUST MATCH Pipeline Y and Z**

---

### Success Criteria

**PASS if:**
- All pages show SAME numbers
- Console shows `fromBackend: true`
- No console errors

**FAIL if:**
- Pipeline shows 180, Dashboard shows 85 → Old demo code still active
- Console shows `fromBackend: false` → Backend endpoint not working
- Pages show different numbers → Inconsistency bug

---

### Expected Output (Example)

```
Pipeline: 14 requirements found, 14 Assignments created, 5 departments impacted
Dashboard: Requirements Extracted: 14, Assignments Generated: 14, Departments: 5
Assignment Center: 14 Total MAPs Across 5 Departments
Console: [ANALYSIS_RESULT] Built AnalysisResult: { fromBackend: true, ... }
```

**Status:** ✅ PASS - All numbers consistent!

---

### Troubleshooting

**Issue: Console shows "[ANALYSIS_RESULT] Failed to fetch backend analysis"**
- **Cause:** Backend endpoint not responding
- **Check:** Is backend running on port 8000?
- **Check:** Open http://localhost:8000/api/docs
- **Check:** Look for GET /admin/document-analysis/{document_id}
- **Fix:** Restart backend

**Issue: Pages show old demo numbers (180, 85, etc.)**
- **Cause:** Frontend not updated or browser cache
- **Fix:** Hard refresh browser (Ctrl+Shift+R)
- **Fix:** Clear browser cache
- **Fix:** Try incognito mode

**Issue: Console shows fromBackend: false**
- **Cause:** Backend endpoint failed, fell back to demo
- **Check:** Backend console for errors
- **Check:** Network tab for failed API calls
- **Fix:** Check backend logs for error details

---

## Quick Backend Endpoint Test

Open http://localhost:8000/api/docs

1. Find: `GET /admin/document-analysis/{document_id}`
2. Click: "Try it out"
3. Enter: document_id = 1
4. Click: "Execute"
5. Verify: Response shows counts, assignments, etc.

**If endpoint missing:** Backend changes not applied

---

## Rollback Instructions (If Needed)

If verification fails and demo tomorrow, revert:

### Frontend Rollback
```javascript
// In Pipeline.jsx line ~313, change:
createSession(file, uploadedDocumentId, api, elapsedTimes, totalElapsed);

// Back to:
createSession(file, null, elapsedTimes, totalElapsed);
```

### Backend Rollback
Not needed - new endpoint doesn't break anything

**Rollback Time:** 30 seconds
