# Stabilization Implementation Plan

## Confirmed Root Causes & Fixes

### ISSUE 1: Pipeline Exit Lifecycle ✓ CONFIRMED
**Root Cause:** Assignment Center doesn't handle empty API response
**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`
**Fix:** Trust backend API, show proper empty state

### ISSUE 2: Confidence Score ✓ CONFIRMED  
**Root Cause:** Demo data has mixed formats (0.91 vs 91)
**File:** `frontend/dashboard/src/pages/MapDetail.jsx`
**Fix:** Defensive normalization (confidence > 1 ? /100 : value)

### ISSUE 3: Graph Full Text ✓ CONFIRMED
**Root Cause:** Graph uses semantic IDs, backend expects integers
**File:** `frontend/dashboard/src/pages/Graph.jsx`
**Fix:** Use session.analysis data directly (no API call needed)

### ISSUE 4: Dashboard Metrics ✓ VERIFIED
**Status:** NO ISSUES - Already fixed in previous work

### ISSUE 5: Count Mismatch ✓ CONFIRMED
**Root Cause:** Assignment Center correctly counts tasks per department
- Dashboard "205 Draft Assignments" = total assignment records
- Assignment Center "34 MAPs" = sum of task_count across departments
**Both are CORRECT** - Different entities being counted
**Fix:** Improve wording only (no calculation changes)

### ISSUE 6: Demo Fallbacks ✓ CONFIRMED
**Root Cause:** Assignment Center falls back to demo
**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`  
**Fix:** Remove demo import and fallback logic

## Implementation

### Fix 1: Assignment Center Empty State

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`

```javascript
// REMOVE:
import demo data

// CHANGE:
if (!summary || !summary.departments || summary.departments.length === 0) {
  return (
    <div style={{ textAlign: 'center', padding: 60 }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
      <div style={{ fontSize: 18, fontWeight: 600, color: '#cbd5e1', marginBottom: 8 }}>
        No Assignments to Review
      </div>
      <div style={{ fontSize: 14, color: '#64748b' }}>
        {hasSession 
          ? 'Complete the pipeline to generate department assignments'
          : 'Run the pipeline to generate department assignments'
        }
      </div>
    </div>
  );
}
```

### Fix 2: Confidence Score Normalization

**File:** `frontend/dashboard/src/pages/MapDetail.jsx`

```javascript
// Line 117 - CHANGE:
// OLD:
{(data.department.confidence * 100).toFixed(0)}%

// NEW:
{(() => {
  const conf = data.department.confidence > 1 
    ? data.department.confidence / 100 
    : data.department.confidence;
  return (conf * 100).toFixed(0);
})()}%
```

### Fix 3: Graph Full Text Retrieval

**File:** `frontend/dashboard/src/pages/Graph.jsx`

```javascript
// CHANGE handleViewNodeFullText function:

const handleViewNodeFullText = () => {
  if (!sel || !sel.id || !hasSession || !session?.analysis) return;
  
  setLoadingFullText(true);
  try {
    if (sel.type === "requirement") {
      // Find requirement in session data
      const requirement = session.analysis.requirements.find(
        r => r.req_id === sel.id
      );
      if (requirement) {
        setSelectedNodeData(requirement);
        setShowFullText(true);
      } else {
        alert('Requirement details not available');
      }
    } else if (sel.type === "map") {
      // Find MAP in session data
      const map = session.analysis.maps.find(
        m => m.map_id === sel.id
      );
      if (map) {
        // Get requirement for this MAP
        const requirement = session.analysis.requirements.find(
          r => {
            // Find by matching requirement in mapDetails
            const detail = mapDetails[map.map_id];
            return detail?.source_requirement?.req_id === r.req_id;
          }
        );
        
        setSelectedNodeData({
          ...map,
          requirement: requirement || { text: map.title }
        });
        setShowFullText(true);
      } else {
        alert('MAP details not available');
      }
    }
  } catch (error) {
    console.error('Failed to load node details:', error);
    alert('Failed to load full text');
  } finally {
    setLoadingFullText(false);
  }
};
```

### Fix 4: Improve Count Wording

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`

```javascript
// Line ~95 - CHANGE summary text:
// OLD:
<div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
  Total MAPs Across {summary.departments.length} Departments
</div>

// NEW:
<div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
  Total Tasks Across {summary.departments.length} Departments
</div>
```

## Files to Modify (Final List)

1. `frontend/dashboard/src/pages/AssignmentCenter.jsx` - Fixes 1, 4, 6
2. `frontend/dashboard/src/pages/MapDetail.jsx` - Fix 2
3. `frontend/dashboard/src/pages/Graph.jsx` - Fix 3

## No Changes Needed

- Backend files (all working correctly)
- Database schema
- API endpoints
- Dashboard.jsx (already fixed)
- Other pages

## Testing Checklist

After implementation:

1. Exit analysis session → Assignment Center should show "No assignments"
2. View MAP detail → Confidence never exceeds 100%
3. Click Graph nodes → Full text displays from session data
4. Dashboard vs Assignment Center → Wording clarifies different metrics
5. No demo.js fallbacks in Assignment Center

