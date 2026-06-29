# CRASH ROOT CAUSE REPORT

## Executive Summary

**Location:** `frontend/dashboard/src/pages/Pipeline.jsx` line 94  
**Error:** `TypeError: Cannot read properties of undefined (reading 'overallRisk')`  
**Root Cause:** `buildAnalysisResult()` does NOT create the `aiBriefing` field that Pipeline.jsx expects  
**Impact:** Pipeline Results page crashes immediately after successful backend fetch

---

## The Crash

### Line 94 - The Failing Statement

```javascript
// Pipeline.jsx line 94
<div style={{ fontSize: 13, color: a.aiBriefing.overallRisk === "CRITICAL" ? "#ef4444" : "#fbbf24", fontWeight: 800 }}>
  {a.aiBriefing.overallRisk} RISK
</div>
```

**Attempting to Access:** `a.aiBriefing.overallRisk`

**Error Message:** `Cannot read properties of undefined (reading 'overallRisk')`

**This means:** `a.aiBriefing` is `undefined`

---

## Variable Trace

### The Variable Name: `a`

**Definition:** `Pipeline.jsx` line 35
```javascript
function AnalysisResults({ session }) {
  const navigate = useNavigate();
  const a = session.analysis;  // <-- 'a' is session.analysis
  const s = a.stats;
  const totalTime = session.processing.totalElapsed;
```

**Chain:**
```
a = session.analysis
session = passed from AnalysisSessionProvider
session.analysis = built by buildAnalysisResult() or generateDocumentAnalysis()
```

---

## Expected Object Shape

### What Pipeline.jsx Expects

Pipeline.jsx accesses these fields on `a.aiBriefing`:

**Line 94:** `a.aiBriefing.overallRisk`  
**Line 98:** `a.aiBriefing.businessImpact`  
**Line 102:** `a.aiBriefing.estimatedEffort`  
**Line 102:** `a.aiBriefing.expectedCompletion`  
**Line 109:** `a.aiBriefing.immediateActions`  
**Line 113:** `a.aiBriefing.executiveRecommendation`

**Expected Structure:**
```javascript
{
  analysis: {
    aiBriefing: {
      overallRisk: "CRITICAL" | "HIGH" | "MEDIUM",
      businessImpact: string,
      estimatedEffort: string,
      expectedCompletion: string,
      immediateActions: string,
      executiveRecommendation: string,
      departmentsToNotify: string  // Not displayed but in legacy
    },
    stats: { ... },
    maps: [ ... ],
    // ... other fields
  }
}
```

---

## Where It Is Created

### Legacy Function: `generateDocumentAnalysis()` ✅ HAS aiBriefing

**Location:** `frontend/dashboard/src/context/AnalysisSession.jsx` line ~272

```javascript
function generateDocumentAnalysis(fileName) {
  // ... builds analysis from demo data ...
  
  // Generate AI Executive Briefing
  const aiBriefing = {
    overallRisk: docMapEntries.filter(m => m.priority === "Critical").length > 5 ? "CRITICAL" : ...,
    businessImpact: `This circular introduces material changes affecting operations...`,
    immediateActions: `Immediate remediation is required on ${...} critical regulatory obligations...`,
    departmentsToNotify: docDepartments.slice(0, 3).map(d => d.department).join(", "),
    estimatedEffort: `${docMapEntries.length * 8.5} person-hours...`,
    expectedCompletion: `Projected 45-60 days baseline...`,
    executiveRecommendation: `Assemble an executive steering committee...`
  };

  return {
    fileName,
    requirements: docRequirements,
    maps: docMapEntries,
    departments: docDepartments,
    stats: { ... },
    aiBriefing  // <-- INCLUDES aiBriefing
  };
}
```

**Result:** ✅ Contains `aiBriefing` field

---

### New Function: `buildAnalysisResult()` ❌ MISSING aiBriefing

**Location:** `frontend/dashboard/src/context/AnalysisSession.jsx` line ~11

```javascript
async function buildAnalysisResult(documentId, api) {
  try {
    const response = await api.get(`/admin/document-analysis/${documentId}`);
    const data = response.data;
    
    // Build AnalysisResult object
    const analysisResult = {
      document: data.document,
      counts: data.counts,
      assignments: data.assignments,
      departmentSummary: data.department_summary,
      priorityDistribution: data.priority_distribution,
      
      dashboardSummary: { ... },
      graphData: { ... },
      requirements: [ ... ],
      maps: data.assignments,
      departments: [ ... ],
      stats: {
        totalRequirements: data.counts.requirements_extracted,
        totalMaps: data.counts.assignments_generated,
        criticalMaps: data.counts.critical_priority,
        highMaps: data.counts.high_priority,
        departmentsImpacted: data.counts.departments_affected,
        graphNodes: ...,
        graphEdges: ...,
        crossReferences: 0
      },
      
      fromBackend: true
    };
    
    return analysisResult;
    
  } catch (error) {
    return null;
  }
}
```

**Result:** ❌ Does NOT contain `aiBriefing` field

---

## Why It Became Undefined

### Execution Flow

1. **Upload Success:** Backend returns document_id
2. **Processing Success:** Backend creates requirements and assignments
3. **Pipeline Complete:** `createSession()` is called
4. **Session Creation:** `buildAnalysisResult(documentId, api)` is called
5. **Backend Fetch Success:** `GET /admin/document-analysis/{id}` returns 200
6. **AnalysisResult Built:** Object is created WITHOUT `aiBriefing` field
7. **Session Set:** `session.analysis = analysisResult` (missing aiBriefing)
8. **Navigation:** User sees Pipeline Results page
9. **Render Attempt:** `AnalysisResults` component renders
10. **Crash:** Line 94 tries to access `a.aiBriefing.overallRisk` → **UNDEFINED**

### Why `aiBriefing` Is Undefined

**Direct Cause:** `buildAnalysisResult()` does not create an `aiBriefing` field

**Design Decision:** The new function was designed to use ONLY backend data, but:
- Backend does NOT provide AI briefing text
- Backend only provides counts and assignments
- AI briefing requires narrative text generation
- Legacy function generates this text from demo data

---

## Field Comparison

### Fields in BOTH Functions

| Field | Legacy | New | Status |
|-------|--------|-----|--------|
| `requirements` | ✅ | ✅ | Present |
| `maps` | ✅ | ✅ | Present |
| `departments` | ✅ | ✅ | Present |
| `stats` | ✅ | ✅ | Present |

### Field ONLY in Legacy

| Field | Legacy | New | Used By |
|-------|--------|-----|---------|
| `aiBriefing` | ✅ | ❌ | Pipeline.jsx line 94+ |
| `fileName` | ✅ | ❌ | Not used in crash |
| `selectedSources` | ✅ | ❌ | Not used in crash |
| `mapIds` | ✅ | ❌ | Not used in crash |
| `domains` | ✅ | ❌ | Pipeline.jsx line 161 |
| `scopedGraph` | ✅ | ❌ | Not used (uses graphData) |

### Fields ONLY in New

| Field | Legacy | New | Used By |
|-------|--------|-----|---------|
| `document` | ❌ | ✅ | Not used yet |
| `counts` | ❌ | ✅ | Not used yet |
| `assignments` | ❌ | ✅ | Not used yet |
| `dashboardSummary` | ❌ | ✅ | Not used yet |
| `priorityDistribution` | ❌ | ✅ | Not used yet |

---

## Additional Missing Fields

While investigating, I found Pipeline.jsx also uses:

### Line 161: `a.domains`
```javascript
{a.domains.slice(0, 8).map(([domain, count]) => (
```

**Status:** ❌ NOT in `buildAnalysisResult()`  
**Format in Legacy:** `domains` is array of `[domainName, count]` tuples

---

## Backend Data Structure

The backend endpoint returns:

```json
{
  "document": { "id": 1, "filename": "...", ... },
  "counts": {
    "requirements_extracted": 14,
    "assignments_generated": 14,
    "departments_affected": 5,
    "critical_priority": 2,
    "high_priority": 6,
    "medium_priority": 4,
    "low_priority": 2
  },
  "assignments": [ ... ],
  "department_summary": [ ... ],
  "priority_distribution": { ... }
}
```

**Notable:** Backend does NOT provide:
- AI-generated executive briefing text
- Domain breakdown
- Business impact narrative
- Executive recommendations

These are narrative/analytical fields that require text generation logic.

---

## Summary: Why AnalysisResult Removed the Field

**It didn't "remove" it - it was never added.**

`buildAnalysisResult()` was designed to build ONLY from backend API data. The backend does NOT provide:
- `aiBriefing` object with narrative text
- `domains` array with domain breakdown

The legacy `generateDocumentAnalysis()` generates these fields by:
1. Analyzing demo data
2. Computing statistics
3. Creating narrative text templates
4. Building briefing from heuristics

**Design Gap:** Task 4 implementation focused on backend data mapping but did not:
1. Identify all fields Pipeline.jsx consumes
2. Provide fallback/generation logic for narrative fields
3. Test the render before committing changes

---

## Impact Analysis

### Pages That Will Crash

**Confirmed Crashes:**
1. Pipeline Results page (line 94 - aiBriefing)
2. Pipeline Results page (line 161 - domains)

**Potential Crashes:**
Other pages that reference `session.analysis.aiBriefing`:
- Executive report download (AnalysisSession.jsx line 371-373)

**Still Work:**
Pages that only use `stats`, `maps`, `departments` should work.

---

## Root Cause Statement

**The regression occurs because:**

1. `buildAnalysisResult()` was designed to use ONLY backend data
2. Backend does not provide narrative fields (`aiBriefing`, `domains`)
3. `buildAnalysisResult()` does not generate or synthesize these fields
4. Pipeline.jsx expects these fields to exist (legacy assumption)
5. When backend path is used, `aiBriefing` is undefined
6. React crashes when trying to read `undefined.overallRisk`

**This is a contract violation between:**
- Data provider: `buildAnalysisResult()` 
- Data consumer: `AnalysisResults` component

The provider changed its output shape without updating the consumer.

---

## Next Steps (DO NOT IMPLEMENT)

To fix this crash, one of these approaches is needed:

**Option A: Generate Missing Fields in buildAnalysisResult()**
- Add logic to create `aiBriefing` from backend data
- Add logic to create `domains` array from assignments
- Match legacy structure

**Option B: Update Pipeline.jsx to Handle Missing Fields**
- Add conditional rendering: `{a.aiBriefing && ...}`
- Provide default values
- Graceful degradation

**Option C: Hybrid Approach**
- Use backend data for counts/stats
- Generate narrative fields from backend data
- Maintain compatibility with both paths

**Option D: Always Use Demo aiBriefing**
- Import demo aiBriefing
- Use as fallback when building from backend
- Quick fix but not ideal

---

## Recommended Fix (Analysis Only)

**Best approach:** Option A - Generate missing fields

**Why:**
- Maintains component contract
- Single source of truth
- No conditional rendering complexity
- Future-proof

**What needs to be added to buildAnalysisResult():**

```javascript
// Generate aiBriefing from backend data
aiBriefing: {
  overallRisk: data.counts.critical_priority > 5 ? "CRITICAL" : 
               data.counts.critical_priority > 0 ? "HIGH" : "MEDIUM",
  businessImpact: `Analysis complete...`,
  immediateActions: `${data.counts.critical_priority} critical items require attention...`,
  estimatedEffort: `${data.counts.assignments_generated * 8.5} person-hours...`,
  expectedCompletion: `Estimated ${Math.ceil(data.counts.assignments_generated / 10)} weeks...`,
  executiveRecommendation: `Prioritize ${data.counts.critical_priority} critical assignments...`,
  departmentsToNotify: data.department_summary.slice(0, 3).map(d => d.department_name).join(", ")
},

// Generate domains from assignments
domains: Object.entries(
  data.assignments.reduce((acc, a) => {
    acc[a.domain] = (acc[a.domain] || 0) + 1;
    return acc;
  }, {})
).sort((a, b) => b[1] - a[1])
```

But DO NOT implement yet - waiting for user approval.

---

## Conclusion

**First Failing Statement:** `Pipeline.jsx` line 94  
**Variable:** `a.aiBriefing` (undefined)  
**Root Cause:** `buildAnalysisResult()` does not create `aiBriefing` field  
**Why:** Backend-only design did not account for narrative fields  
**Impact:** Immediate crash on Pipeline Results page  
**Additional Missing Field:** `domains` (line 161)

The application successfully fetches data from backend but crashes during render because the new data structure is incompatible with existing UI expectations.
