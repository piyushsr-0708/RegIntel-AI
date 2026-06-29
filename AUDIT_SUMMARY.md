# Executive Dashboard Audit - Summary

**Status:** ✅ Code Analysis Complete  
**Database Execution:** Pending (requires virtual environment setup)

---

## KEY FINDINGS

### ✅ CONSISTENT METRICS

1. **Published (36) + Unpublished (34) = Total (70)** ✓
2. **Dept Assigned (36) - Completed (12) = Remaining (24)** ✓
3. **Departments Impacted (4)** - Correctly counts distinct departments with published assignments

---

### 🔴 CRITICAL INCONSISTENCIES

#### 1. Pending Tasks (58) ≠ Department Remaining (24)

**Problem:** These appear related but count different things.

| Metric | Counts | Filter |
|--------|--------|--------|
| Pending Tasks (58) | All assignments with `status='pending'` | Includes unpublished |
| Dept Remaining (24) | Published non-completed assignments | Only `is_published=True` |

**Root Cause:** Different filter logic
- Pending = `status='pending'` (pub + unpub)
- Remaining = `is_published=True AND status!='completed'` (pub only, includes in_progress)

**Impact:** Users expect these to match but they don't.

**Fix:** Apply consistent `is_published=True` filter to operational metrics.

---

#### 2. Completed Tasks Filter Mismatch

**Dashboard KPI:** Counts ALL completed (published + unpublished)  
**Department Table:** Counts ONLY published completed

**Currently they match (both = 12)** but this is coincidental.

**Risk:** Could diverge if unpublished assignments are marked completed.

**Fix:** Add `is_published=True` filter to dashboard KPI query.

---

#### 3. Upcoming Deadlines (55) - Hybrid Logic

**Counts:**
1. Assignments with `due_date` within 30 days
2. Assignments WITHOUT `due_date` but priority = Critical/High

**Problem:** Mixes real deadlines with implicit urgency.

**Impact:** "55 Upcoming Deadlines" doesn't mean 55 actual deadlines.

**Fix:** Split into two metrics or clarify label.

---

#### 4. Terminology: "Unpublished MAPs"

**Current:** "Unpublished MAPs"  
**Reality:** Unpublished Assignments (not MAPs)

**Confusion:** Users think these are draft documents or unpublished analysis results.

**Truth:** These are Assignment records in the database where `is_published=False`.

**Fix:** Rename to "Draft Assignments" or "Pending Review".

---

## BACKEND FUNCTION MAPPING

| Dashboard Metric | Backend Function | Database Query |
|------------------|------------------|----------------|
| Published MAPs | `get_dashboard_summary()` | `COUNT(*) WHERE is_published=True` |
| Unpublished MAPs | `get_dashboard_summary()` | `total_assignments - published` |
| Pending Tasks | `get_dashboard_summary()` | `COUNT(*) WHERE status='pending'` |
| Completed Tasks | `get_dashboard_summary()` | `COUNT(*) WHERE status='completed'` |
| Critical Priority | `get_dashboard_summary()` | Priority from Assignment or Requirement |
| High Priority | `get_dashboard_summary()` | Priority from Assignment or Requirement |
| Departments Impacted | `get_dashboard_summary()` | `COUNT(DISTINCT dept) WHERE is_published=True` |
| Upcoming Deadlines | `get_dashboard_summary()` | Hybrid: due_date OR high/critical priority |
| Dept Table | `get_admin_completion_summary()` | `WHERE is_published=True` per department |

---

## RECOMMENDED FIXES

### Priority 1: Consistency

```python
# Current (inconsistent)
pending = db.query(Assignment).filter(
    Assignment.status == "pending"
).count()

# Proposed (consistent)
pending = db.query(Assignment).filter(
    Assignment.is_published == True,
    Assignment.status == "pending"
).count()
```

Apply `is_published=True` filter to:
- Pending Tasks
- Completed Tasks
- Critical Priority
- High Priority

### Priority 2: Terminology

```javascript
// Current
{ label: "Unpublished MAPs", ... }

// Proposed
{ label: "Draft Assignments", sub: "Awaiting review" }
```

### Priority 3: Deadline Logic

```python
# Current (hybrid)
if a.due_date and a.due_date <= upcoming_limit:
    count += 1
elif priority in ["Critical", "High"]:
    count += 1  # No actual deadline!

# Proposed (clear)
actual_deadlines = db.query(Assignment).filter(
    Assignment.due_date != None,
    Assignment.due_date <= upcoming_limit
).count()

urgent_tasks = db.query(Assignment).filter(
    Assignment.due_date == None,
    Assignment.priority.in_(["Critical", "High"])
).count()

# Show both separately or clearly label as "Urgent Tasks"
```

---

## SQL VERIFICATION QUERIES

Run these to confirm the audit findings:

```sql
-- 1. Published + Unpublished = Total
SELECT 
    SUM(CASE WHEN is_published = 1 THEN 1 ELSE 0 END) as published,
    SUM(CASE WHEN is_published = 0 THEN 1 ELSE 0 END) as unpublished,
    COUNT(*) as total
FROM assignments;
-- Expected: 36 + 34 = 70

-- 2. Pending (all) vs Pending (published only)
SELECT 
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_all,
    SUM(CASE WHEN status = 'pending' AND is_published = 1 THEN 1 ELSE 0 END) as pending_published
FROM assignments;
-- Shows difference between 58 and actual published pending

-- 3. Completed (all) vs Completed (published only)
SELECT 
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_all,
    SUM(CASE WHEN status = 'completed' AND is_published = 1 THEN 1 ELSE 0 END) as completed_published
FROM assignments;
-- Verify if they match (currently 12 = 12)

-- 4. Department breakdown
SELECT 
    department_id,
    COUNT(*) as total,
    SUM(CASE WHEN is_published = 1 THEN 1 ELSE 0 END) as published,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
FROM assignments
GROUP BY department_id;
-- Should show 4 departments with published > 0

-- 5. Priority distribution
SELECT 
    COALESCE(a.priority, r.priority, 'Medium') as priority,
    COUNT(*) as count
FROM assignments a
LEFT JOIN requirements r ON a.requirement_id = r.id
GROUP BY priority;
-- Should sum to 70
```

---

## CANONICAL DEFINITIONS (PROPOSED)

| Metric | Count | Filter |
|--------|-------|--------|
| **Total Assignments** | 70 | None |
| **Published** | 36 | `is_published=True` |
| **Draft** | 34 | `is_published=False` |
| **Active Tasks** | 24 | `is_published=True AND status!='completed'` |
| **Completed Tasks** | 12 | `is_published=True AND status='completed'` |
| **Critical** | 20 | `priority='Critical'` (published only) |
| **High** | 35 | `priority='High'` (published only) |
| **Departments** | 4 | `COUNT(DISTINCT dept) WHERE is_published=True` |
| **Deadlines** | ? | `due_date <= now+30 days` (actual only) |

---

## NEXT STEPS

1. ✅ **Audit Complete** - All metrics traced to source
2. ⏳ **Database Verification** - Execute SQL queries on live database
3. ⏳ **API Response Capture** - Get actual JSON from endpoints
4. ⏳ **Fix Implementation** - Apply consistency changes
5. ⏳ **Documentation** - Update code comments with definitions

---

**See `EXECUTIVE_DASHBOARD_CONSISTENCY_AUDIT.md` for full detailed analysis.**
