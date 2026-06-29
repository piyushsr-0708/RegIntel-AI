# Domain Reconciliation Implementation Plan

**Decision Point:** This plan assumes **Option A** - Accepting that "MAP" = "Assignment" and reconciling terminology.

If stakeholders choose **Option B** (making MAPs real entities), a different architectural plan is required.

---

## Phase 1: Terminology Reconciliation

**Goal:** Replace "MAP" terminology with "Assignment" throughout codebase

**Priority:** CRITICAL  
**Effort:** 3-4 days  
**Risk:** Low (mostly renaming)

### Backend Changes

#### 1.1 Database Migration

**File:** Create new migration

```python
# New migration: rename_maps_to_assignments.py

def upgrade():
    # Rename column in assignment_batches table
    op.alter_column('assignment_batches', 'total_maps', 
                    new_column_name='total_assignments')

def downgrade():
    op.alter_column('assignment_batches', 'total_assignments',
                    new_column_name='total_maps')
```

**Impact:** 1 table, 1 column

#### 1.2 ORM Models

**File:** `backend/models.py`

```python
# Line 82 - CHANGE:
total_assignments = Column(Integer, default=0)  # Was: total_maps
```

**Impact:** 1 file, 1 line

#### 1.3 Schemas

**File:** `backend/schemas.py`

```python
# Line 196 - CHANGE:
published_assignments: int  # Was: published_maps

# Line 272 - CHANGE:
total_assignments: int  # Was: total_maps
```

**Impact:** 1 file, 2 lines

#### 1.4 CRUD Operations

**File:** `backend/crud.py`

**Changes:**
```python
# Line 308 - Rename variable:
published_assignments = db.query(...)  # Was: published_maps

# Line 309 - Rename variable:
unpublished_assignments = total_assignments - published_assignments  # Was: unpublished_maps

# Line 341 - Change response key:
"published_assignments": published_assignments,  # Was: "published_maps"

# Line 344 - Already correct:
"unpublished_assignments": unpublished_assignments,

# Line 525 - Rename variable:
total_assignments = len(assignments)  # Was: total_maps

# Line 531 - Change response key:
"total_assignments": total_assignments,  # Was: "total_maps"

# Line 618 - Rename variable and comment:
# Count assignments
total_assignments = db.query(...)  # Was: total_maps

# Line 623 - Rename variable:
completed_assignments = db.query(...)  # Was: completed_maps

# Line 629 - Rename variable:
verified_assignments = completed_assignments  # Was: verified_maps

# Line 631 - Update calculation:
completion_pct = int((completed_assignments / total_assignments * 100)) if total_assignments > 0 else 0

# Line 632 - Update calculation:
verification_pct = int((verified_assignments / total_assignments * 100)) if total_assignments > 0 else 0

# Line 636 - Update model field:
batch.total_assignments = total_assignments  # Was: batch.total_maps
```

**Impact:** 1 file, ~15 lines

#### 1.5 API Routers

**File:** `backend/routers/assignment_center_router.py`

```python
# Line 31-35 - CHANGE:
total_assignments = sum(dept["task_count"] for dept in summary.values())

return {
    "total_assignments": total_assignments,  # Was: "total_maps"
    "departments": list(summary.values())
}
```

**Impact:** 1 file, 2 lines

**File:** `backend/routers/assignment_batch_router.py`

```python
# Update all comments and documentation:
# Line 29: "and assignments generated from that circular"  # Was: "and MAPs"
# Line 105: "- Department distribution (how many assignments per department)"  # Was: "how many MAPs"
# Line 197: "- total_assignments"  # Was: "- total_maps"
```

**Impact:** 1 file, comments only

### Frontend Changes

#### 1.6 Dashboard Labels

**File:** `frontend/dashboard/src/pages/Dashboard.jsx`

```javascript
// Line ~88 - KPI definitions:
{ 
  label: "Published Assignments",  // Was: "Published MAPs"
  value: m.published_assignments,  // Was: m.published_maps
  ...
},
{ 
  label: "Draft Assignments",  // Was: "Draft MAPs" or "Unpublished MAPs"
  value: m.unpublished_assignments,
  ...
},
// Keep "Pending Tasks", "Completed Tasks" as-is (correct terminology)
```

**Impact:** 1 file, 2 labels

#### 1.7 Assignment Center

**File:** `frontend/dashboard/src/pages/AssignmentCenter.jsx`

```javascript
// Line ~127 - Summary display:
<div>
  Total Assignments Across {summary.departments.length} Departments
  // Was: "Total MAPs Across..."
</div>
```

**Impact:** 1 file, 1 label

#### 1.8 Pipeline Results

**File:** `frontend/dashboard/src/pages/Pipeline.jsx`

**Strategy:** Leave session terminology as "MAPs" since it's analyzing demo data

**Rationale:** Pipeline session is showing analysis of a document, using demo data for visualization. The term "MAP" in this context can mean "mitigation action proposal" from analysis, distinct from database "assignments".

**No changes needed** (or minimal label clarification)

### Testing After Phase 1

1. ✅ Run database migration
2. ✅ Restart backend
3. ✅ Verify API responses use new field names
4. ✅ Verify Dashboard displays "Published Assignments" / "Draft Assignments"
5. ✅ Verify Assignment Center displays "Total Assignments"
6. ✅ Verify counts remain accurate
7. ✅ Check for any broken API integrations

---

## Phase 2: Requirements Single Source

**Goal:** Make database the authoritative source for requirements, enable searching newly created requirements

**Priority:** HIGH  
**Effort:** 2-3 days  
**Risk:** Medium (changes data flow)

### Backend Changes

#### 2.1 Requirements Search API

**File:** `backend/routers/requirement_router.py` (NEW FILE)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..auth import get_current_active_user
from .. import crud, models

router = APIRouter(prefix="/requirements", tags=["Requirements"])

@router.get("/search")
def search_requirements(
    q: Optional[str] = Query(None, description="Search query"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search requirements in database"""
    query = db.query(models.Requirement)
    
    if q:
        query = query.filter(models.Requirement.text.ilike(f"%{q}%"))
    if domain:
        query = query.filter(models.Requirement.domain == domain)
    if classification:
        query = query.filter(models.Requirement.classification == classification)
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "results": results
    }

@router.get("/{requirement_id}")
def get_requirement(
    requirement_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get requirement by ID"""
    return crud.get_requirement_by_id(db, requirement_id)
```

#### 2.2 Register Router

**File:** `backend/main.py`

```python
from .routers import requirement_router

app.include_router(requirement_router.router, prefix="/api")
```

### Frontend Changes

#### 2.3 Requirements Search Page

**File:** `frontend/dashboard/src/pages/Requirements.jsx`

**Major Refactor:**

```javascript
// REMOVE:
import { requirementsTaxonomy } from "../data/demo";

// ADD:
import { useAuth } from '../context/AuthContext';
import { useState, useEffect } from 'react';

export default function Requirements() {
  const { api } = useAuth();
  const [requirements, setRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");
  const [total, setTotal] = useState(0);
  
  // Fetch requirements from API
  useEffect(() => {
    loadRequirements();
  }, [query, domain]);
  
  const loadRequirements = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (domain) params.append('domain', domain);
      
      const response = await api.get(`/requirements/search?${params}`);
      setRequirements(response.data.results);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Failed to load requirements:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Update UI to use requirements state instead of requirementsTaxonomy
  // ... rest of component
}
```

**Impact:** 1 file, major refactor (~100 lines)

#### 2.4 Dashboard Requirements Count

**File:** `backend/crud.py`

```python
# Line 270-278 - REMOVE demo JSON fallback:
# BEFORE:
try:
    json_path = "..."
    with open(json_path, 'r') as f:
        total_reqs = len(json.load(f))
except:
    total_reqs = db.query(func.count(models.Requirement.id)).scalar()

# AFTER:
total_reqs = db.query(func.count(models.Requirement.id)).scalar() or 0
```

**Impact:** 1 file, simpler code

### Testing After Phase 2

1. ✅ Create requirement via pipeline
2. ✅ Search for new requirement in UI
3. ✅ Verify it appears in search results
4. ✅ Verify domain filtering works
5. ✅ Verify full text search works
6. ✅ Check Dashboard requirements count uses database
7. ✅ Verify no demo JSON fallbacks remain

---

## Phase 3: Knowledge Graph Persistence (FUTURE)

**Goal:** Store graph in database, enable historical viewing

**Priority:** MEDIUM (Future Enhancement)  
**Effort:** 5-7 days  
**Risk:** HIGH (new architecture)

### Design

**New Tables:**
```sql
CREATE TABLE graph_nodes (
    id INTEGER PRIMARY KEY,
    graph_id INTEGER REFERENCES knowledge_graphs(id),
    node_id VARCHAR(100),  -- Semantic ID (REQ-XXX, MAP-XXX, etc.)
    node_type VARCHAR(50),  -- circular, requirement, assignment, department
    label VARCHAR(200),
    metadata JSON
);

CREATE TABLE graph_edges (
    id INTEGER PRIMARY KEY,
    graph_id INTEGER REFERENCES knowledge_graphs(id),
    source_node_id VARCHAR(100),
    target_node_id VARCHAR(100),
    edge_type VARCHAR(50),  -- defines, generates, assigned
    label VARCHAR(100)
);

CREATE TABLE knowledge_graphs (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    batch_id INTEGER REFERENCES assignment_batches(id),
    created_at TIMESTAMP,
    name VARCHAR(200)
);
```

### Implementation Steps

1. Create database migrations
2. Implement graph generation during pipeline processing
3. Create API endpoints for graph retrieval
4. Update Graph.jsx to use API instead of session
5. Support viewing historical graphs by document/batch

**Status:** Deferred to Phase 3 (not in current scope)

---

## Phase 4: True MAP Generation (OPTIONAL)

**Goal:** IF stakeholders want MAPs as separate entities with AI-generated content

**Priority:** LOW (Business Decision Required)  
**Effort:** 3-4 weeks  
**Risk:** VERY HIGH (major architecture change)

### Design Concept

**New Table:**
```sql
CREATE TABLE mitigation_action_plans (
    id INTEGER PRIMARY KEY,
    map_id VARCHAR(100) UNIQUE,  -- MAP-XXX
    requirement_id INTEGER REFERENCES requirements(id),
    title VARCHAR(500),
    description TEXT,  -- AI-generated mitigation plan
    impact_score DECIMAL(3,1),
    priority VARCHAR(50),
    estimated_effort VARCHAR(200),
    created_at TIMESTAMP
);

-- Modify assignments table:
ALTER TABLE assignments ADD COLUMN map_id INTEGER REFERENCES mitigation_action_plans(id);
```

### New Relationship

```
Requirement → AI Analysis → MAP (mitigation plan) → Assignment to Department
```

### Implementation

1. Implement AI/rule-based MAP generation logic
2. Create maps table and modify assignments
3. Update pipeline to generate MAPs
4. Update all UIs to distinguish MAPs from Assignments
5. Migration strategy for existing data

**Status:** Requires business decision (not in current scope)

---

## Recommended Implementation Order

### Immediate (This Sprint)

1. ✅ **Phase 1: Terminology Reconciliation** (3-4 days)
   - Eliminates semantic confusion
   - Low risk
   - High value for clarity

### Next Sprint

2. ✅ **Phase 2: Requirements Single Source** (2-3 days)
   - Enables searching new requirements
   - Removes demo data dependency
   - Medium risk, high value

### Future Enhancements

3. ⏸️ **Phase 3: Graph Persistence** (Future)
   - Nice to have
   - Not critical for core functionality
   - Plan when capacity allows

4. ⏸️ **Phase 4: True MAP Generation** (Optional)
   - Requires business decision
   - Major architecture change
   - Only if MAPs need to be distinct entities

---

## Estimated Timeline

| Phase | Duration | Dependencies | Risk |
|-------|----------|--------------|------|
| Phase 1 | 3-4 days | None | Low |
| Phase 2 | 2-3 days | Phase 1 complete | Medium |
| Phase 3 | 5-7 days | Phases 1 & 2 | High |
| Phase 4 | 3-4 weeks | Business decision | Very High |

**Total for Phases 1 & 2:** 5-7 days

---

## Success Criteria

### Phase 1 Success
- ✅ All "MAP" terminology replaced with "Assignment" in code
- ✅ Database column renamed (total_assignments)
- ✅ All API responses use new field names
- ✅ UI labels updated ("Published Assignments", etc.)
- ✅ No breaking changes in functionality
- ✅ All counts remain accurate

### Phase 2 Success
- ✅ Requirements search uses database API
- ✅ Newly created requirements appear in search
- ✅ Demo JSON no longer used for requirements
- ✅ Domain filtering works
- ✅ Full text search works
- ✅ Dashboard requirements count from database

---

## Rollback Plan

### Phase 1 Rollback
```bash
# Revert database migration
alembic downgrade -1

# Revert code changes
git revert <commit-hash>

# Restart services
```

### Phase 2 Rollback
```bash
# Remove new router
git revert <commit-hash>

# Restore demo JSON usage in frontend
git checkout HEAD~1 frontend/dashboard/src/pages/Requirements.jsx

# Restart frontend
```

---

## Documentation Updates Required

1. Update API documentation (Swagger/OpenAPI)
2. Update database schema diagrams
3. Update developer onboarding docs
4. Update user guides (if any reference "MAPs")
5. Update this domain model document

---

## Communication Plan

1. **Announce terminology change** to team before Phase 1
2. **Update API changelog** with deprecated field names
3. **Provide migration guide** for any external API consumers
4. **Demo new requirements search** after Phase 2
5. **Update training materials** if applicable

