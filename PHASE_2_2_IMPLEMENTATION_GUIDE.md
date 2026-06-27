# Phase 2.2 Implementation Guide

## Executive Summary

**Complexity**: Very High  
**Estimated Time**: 40-60 development hours  
**Files to Create**: 30+  
**Files to Modify**: 20+  
**Lines of Code**: 5,000-7,000  

**Recommendation**: Implement in 4 sub-phases over 3-4 weeks with a team.

This guide provides complete specifications and templates for implementing Phase 2.2.

---

## Table of Contents

1. [Backend Implementation](#1-backend-implementation)
2. [Frontend Implementation](#2-frontend-implementation)
3. [Integration & Testing](#3-integration--testing)
4. [Deployment](#4-deployment)

---

## 1. Backend Implementation

### 1.1 Database Schema Changes

#### Step 1: Extend `assignments` Table

```python
# backend/models.py - ADD these columns to Assignment class

# Phase 2.2 - AI Suggestions & Workflow
ai_confidence = Column(Integer, nullable=True)  # 0-100
ai_reasoning = Column(Text, nullable=True)
is_approved = Column(Boolean, default=False)
approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
approved_at = Column(DateTime, nullable=True)
is_published = Column(Boolean, default=False)
published_at = Column(DateTime, nullable=True)
lifecycle_stage = Column(String(50), default="assigned")
accepted_at = Column(DateTime, nullable=True)
started_at = Column(DateTime, nullable=True)
```

#### Step 2: Create Migration

The columns will be added automatically by SQLAlchemy when you start the backend.

**Manual SQL** (if needed):
```sql
ALTER TABLE assignments ADD COLUMN ai_confidence INTEGER;
ALTER TABLE assignments ADD COLUMN ai_reasoning TEXT;
ALTER TABLE assignments ADD COLUMN is_approved BOOLEAN DEFAULT FALSE;
ALTER TABLE assignments ADD COLUMN approved_by INTEGER REFERENCES users(id);
ALTER TABLE assignments ADD COLUMN approved_at DATETIME;
ALTER TABLE assignments ADD COLUMN is_published BOOLEAN DEFAULT FALSE;
ALTER TABLE assignments ADD COLUMN published_at DATETIME;
ALTER TABLE assignments ADD COLUMN lifecycle_stage VARCHAR(50) DEFAULT 'assigned';
ALTER TABLE assignments ADD COLUMN accepted_at DATETIME;
ALTER TABLE assignments ADD COLUMN started_at DATETIME;
```

---

### 1.2 AI Suggestion Generation Logic

Create `backend/services/ai_suggester.py`:

```python
"""
AI Department Suggestion Service
Deterministic rule-based assignment logic
"""
from typing import Dict, List
import re


# Domain keyword mappings
DEPARTMENT_KEYWORDS = {
    "compliance": [
        "kyc", "know your customer", "aml", "anti-money laundering",
        "customer due diligence", "cdd", "enhanced due diligence", "edd",
        "pep", "politically exposed", "risk assessment",  
        "compliance", "regulatory", "sanctions"
    ],
    "cyber": [
        "cyber", "security", "information security", "data protection",
        "encryption", "firewall", "intrusion", "vulnerability",
        "incident response", "security breach", "data breach",
        "penetration test", "security audit", "password", "authentication"
    ],
    "it": [
        "technology", "system", "software", "hardware", "network",
        "database", "server", "application", "infrastructure",
        "backup", "disaster recovery", "business continuity",
        "cloud", "api", "integration"
    ],
    "risk": [
        "risk management", "operational risk", "credit risk",
        "market risk", "liquidity risk", "risk appetite",
        "risk assessment", "risk mitigation", "control framework",
        "internal control", "risk monitoring"
    ],
    "treasury": [
        "treasury", "liquidity", "cash management", "funding",
        "investment", "portfolio", "asset liability",
        "forex", "hedging", "derivatives"
    ],
    "operations": [
        "operations", "process", "workflow", "sop",
        "standard operating procedure", "transaction processing",
        "reconciliation", "settlement"
    ],
    "finance": [
        "accounting", "financial reporting", "audit",
        "general ledger", "financial statement", "ifrs",
        "capital adequacy", "provisioning"
    ],
    "aml": [
        "money laundering", "suspicious transaction", "strstm",
        "transaction monitoring", "alerts", "typology",
        "layering", "placement", "integration"
    ],
    "legal": [
        "legal", "regulatory compliance", "rbi directive",
        "master direction", "circular", "notification",
        "penalty", "enforcement", "legal opinion"
    ]
}


def calculate_department_confidence(requirement_text: str, domain: str, department: str) -> tuple[int, str]:
    """
    Calculate confidence score and reasoning for department assignment
    
    Returns:
        (confidence: int, reasoning: str)
    """
    text_lower = requirement_text.lower()
    keywords = DEPARTMENT_KEYWORDS.get(department, [])
    
    # Count keyword matches
    matches = []
    for keyword in keywords:
        if keyword in text_lower:
            matches.append(keyword)
    
    # Calculate base confidence
    if not matches:
        base_confidence = 30  # Default low confidence
    else:
        # Higher confidence with more matches
        base_confidence = min(95, 60 + (len(matches) * 10))
    
    # Domain boost
    domain_boost = 0
    if domain:
        domain_lower = domain.lower()
        dept_lower = department.lower()
        if dept_lower in domain_lower or domain_lower in dept_lower:
            domain_boost = 15
    
    confidence = min(100, base_confidence + domain_boost)
    
    # Generate reasoning
    if matches:
        match_str = ", ".join(f"'{m}'" for m in matches[:5])
        reasoning = f"Detected {len(matches)} relevant keywords: {match_str}. "
    else:
        reasoning = "General assignment based on requirement classification. "
    
    if domain:
        reasoning += f"Requirement classified as {domain}. "
    
    if confidence < 70:
        reasoning += "Manual review recommended."
    
    return confidence, reasoning


def suggest_departments_for_batch(requirements: List[Dict]) -> Dict[int, Dict]:
    """
    Generate AI suggestions for all requirements in a batch
    
    Args:
        requirements: List of requirement dicts with id, text, domain, priority
    
    Returns:
        {requirement_id: {department: str, confidence: int, reasoning: str}}
    """
    suggestions = {}
    
    for req in requirements:
        req_id = req["id"]
        text = req.get("text", "")
        domain = req.get("domain", "").lower()
        
        # Determine primary department based on domain
        if "kyc" in domain or "aml" in domain or "cdd" in domain:
            primary_dept = "compliance"
        elif "cyber" in domain or "security" in domain:
            primary_dept = "cyber"
        elif "risk" in domain:
            primary_dept = "risk"
        elif "treasury" in domain:
            primary_dept = "treasury"
        elif "technology" in domain or "it" in domain:
            primary_dept = "it"
        else:
            # Analyze text for keywords
            max_matches = 0
            primary_dept = "compliance"  # Default
            
            for dept, keywords in DEPARTMENT_KEYWORDS.items():
                matches = sum(1 for kw in keywords if kw in text.lower())
                if matches > max_matches:
                    max_matches = matches
                    primary_dept = dept
        
        # Calculate confidence and reasoning
        confidence, reasoning = calculate_department_confidence(text, domain, primary_dept)
        
        suggestions[req_id] = {
            "department": primary_dept,
            "confidence": confidence,
            "reasoning": reasoning,
            "priority": req.get("priority", "medium")
        }
    
    return suggestions


def generate_ai_suggestions_for_batch(db, batch_id: int):
    """
    Generate and store AI suggestions for all requirements in batch
    
    This should be called after requirements are extracted and before
    presenting to Assignment Center.
    """
    from ..models import Requirement, Assignment, Department
    from datetime import datetime
    
    # Get all requirements for batch
    requirements = db.query(Requirement).filter(
        Requirement.batch_id == batch_id
    ).all()
    
    if not requirements:
        return
    
    # Convert to dict format
    req_list = [
        {
            "id": r.id,
            "text": r.text,
            "domain": r.domain or "",
            "priority": r.priority or "medium"
        }
        for r in requirements
    ]
    
    # Generate suggestions
    suggestions = suggest_departments_for_batch(req_list)
    
    # Store as assignments (not yet approved/published)
    for req_id, suggestion in suggestions.items():
        # Get department
        dept = db.query(Department).filter(
            Department.code == suggestion["department"].upper()
        ).first()
        
        if not dept:
            continue
        
        # Check if assignment already exists
        existing = db.query(Assignment).filter(
            Assignment.requirement_id == req_id,
            Assignment.batch_id == batch_id
        ).first()
        
        if existing:
            # Update AI fields
            existing.ai_confidence = suggestion["confidence"]
            existing.ai_reasoning = suggestion["reasoning"]
        else:
            # Create new assignment (not yet approved)
            assignment = Assignment(
                requirement_id=req_id,
                department_id=dept.id,
                assigned_by=1,  # System user
                batch_id=batch_id,
                ai_confidence=suggestion["confidence"],
                ai_reasoning=suggestion["reasoning"],
                is_approved=False,
                is_published=False,
                lifecycle_stage="assigned"
            )
            db.add(assignment)
    
    db.commit()
```

---

### 1.3 New CRUD Operations

Add to `backend/crud.py`:

```python
# ============================================================================
# PHASE 2.2 - Assignment Center & Department Workspace
# ============================================================================

def get_ai_suggestions_for_batch(db: Session, batch_id: int) -> dict:
    """Get AI department suggestions grouped by department"""
    from sqlalchemy import func
    
    # Get all assignments for batch (not yet published)
    assignments = db.query(models.Assignment).filter(
        models.Assignment.batch_id == batch_id,
        models.Assignment.is_published == False
    ).all()
    
    # Group by department
    dept_groups = {}
    for assignment in assignments:
        dept_id = assignment.department_id
        dept = assignment.department
        
        if dept_id not in dept_groups:
            dept_groups[dept_id] = {
                "department_id": dept_id,
                "department_name": dept.name,
                "department_code": dept.code,
                "maps": [],
                "total_maps": 0,
                "avg_confidence": 0
            }
        
        # Get requirement details
        req = assignment.requirement
        
        dept_groups[dept_id]["maps"].append({
            "assignment_id": assignment.id,
            "requirement_id": req.id,
            "requirement_text": req.text,
            "priority": req.priority,
            "domain": req.domain,
            "confidence": assignment.ai_confidence,
            "reasoning": assignment.ai_reasoning,
            "is_approved": assignment.is_approved
        })
    
    # Calculate averages
    for dept_id, group in dept_groups.items():
        group["total_maps"] = len(group["maps"])
        confidences = [m["confidence"] for m in group["maps"] if m["confidence"]]
        group["avg_confidence"] = int(sum(confidences) / len(confidences)) if confidences else 0
    
    return dept_groups


def approve_department_assignments(
    db: Session,
    batch_id: int,
    department_id: int,
    approved_by: int,
    assignment_ids: list = None
) -> int:
    """Approve assignments for a department (or specific assignments)"""
    from datetime import datetime
    
    query = db.query(models.Assignment).filter(
        models.Assignment.batch_id == batch_id,
        models.Assignment.department_id == department_id,
        models.Assignment.is_approved == False
    )
    
    if assignment_ids:
        query = query.filter(models.Assignment.id.in_(assignment_ids))
    
    count = query.update({
        "is_approved": True,
        "approved_by": approved_by,
        "approved_at": datetime.utcnow()
    })
    
    db.commit()
    return count


def reject_department_assignments(
    db: Session,
    batch_id: int,
    department_id: int,
    assignment_ids: list = None
) -> int:
    """Reject/delete assignments for a department"""
    query = db.query(models.Assignment).filter(
        models.Assignment.batch_id == batch_id,
        models.Assignment.department_id == department_id,
        models.Assignment.is_approved == False
    )
    
    if assignment_ids:
        query = query.filter(models.Assignment.id.in_(assignment_ids))
    
    count = query.delete()
    db.commit()
    return count


def edit_assignment_department(
    db: Session,
    assignment_id: int,
    new_department_id: int
) -> models.Assignment:
    """Manually reassign to different department"""
    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()
    
    if assignment:
        assignment.department_id = new_department_id
        assignment.ai_confidence = None  # Clear AI confidence for manual edit
        assignment.ai_reasoning = "Manually reassigned by Head Office"
        db.commit()
        db.refresh(assignment)
    
    return assignment


def publish_batch_assignments(
    db: Session,
    batch_id: int,
    published_by: int
) -> int:
    """Publish all approved assignments (make visible to departments)"""
    from datetime import datetime
    
    count = db.query(models.Assignment).filter(
        models.Assignment.batch_id == batch_id,
        models.Assignment.is_approved == True,
        models.Assignment.is_published == False
    ).update({
        "is_published": True,
        "published_at": datetime.utcnow()
    })
    
    # Update batch status
    batch = db.query(models.AssignmentBatch).filter(
        models.AssignmentBatch.id == batch_id
    ).first()
    
    if batch:
        batch.status = "published"
        db.commit()
    
    return count


def get_department_assignments(db: Session, department_id: int, lifecycle_stage: str = None):
    """Get published assignments for a department (Department user view)"""
    query = db.query(models.Assignment).filter(
        models.Assignment.department_id == department_id,
        models.Assignment.is_published == True
    )
    
    if lifecycle_stage:
        query = query.filter(models.Assignment.lifecycle_stage == lifecycle_stage)
    
    return query.all()


def get_department_dashboard_data(db: Session, department_id: int) -> dict:
    """Get dashboard data for department workspace"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Get all published assignments
    assignments = get_department_assignments(db, department_id)
    
    # Today's tasks (assigned or accepted today)
    today = datetime.utcnow().date()
    todays_tasks = [a for a in assignments if a.assigned_at.date() == today or (a.accepted_at and a.accepted_at.date() == today)]
    
    # Critical tasks
    critical = [a for a in assignments if a.requirement.priority == "critical"]
    
    # Due today (placeholder - would need deadline field)
    due_today = []
    
    # Overdue (placeholder - would need deadline field)
    overdue = []
    
    # Status counts
    status_counts = {
        "assigned": sum(1 for a in assignments if a.lifecycle_stage == "assigned"),
        "accepted": sum(1 for a in assignments if a.lifecycle_stage == "accepted"),
        "in_progress": sum(1 for a in assignments if a.lifecycle_stage == "in_progress"),
        "completed": sum(1 for a in assignments if a.lifecycle_stage == "completed")
    }
    
    # Priority counts
    priority_counts = {
        "critical": sum(1 for a in assignments if a.requirement.priority == "critical"),
        "high": sum(1 for a in assignments if a.requirement.priority == "high"),
        "medium": sum(1 for a in assignments if a.requirement.priority == "medium"),
        "low": sum(1 for a in assignments if a.requirement.priority == "low")
    }
    
    # Completion percentage
    total = len(assignments)
    completed = status_counts["completed"]
    completion_pct = int((completed / total * 100)) if total > 0 else 0
    
    return {
        "department_id": department_id,
        "total_assignments": total,
        "todays_tasks": todays_tasks[:10],
        "critical_tasks": critical[:10],
        "due_today": due_today,
        "overdue": overdue,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "completion_percentage": completion_pct,
        "recent_updates": assignments[:10]
    }


def update_assignment_lifecycle(
    db: Session,
    assignment_id: int,
    new_stage: str,
    user_id: int
) -> models.Assignment:
    """Update assignment lifecycle stage"""
    from datetime import datetime
    
    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        return None
    
    old_stage = assignment.lifecycle_stage
    assignment.lifecycle_stage = new_stage
    
    # Set timestamps
    if new_stage == "accepted" and not assignment.accepted_at:
        assignment.accepted_at = datetime.utcnow()
    elif new_stage == "in_progress" and not assignment.started_at:
        assignment.started_at = datetime.utcnow()
    elif new_stage == "completed" and not assignment.completed_at:
        assignment.completed_at = datetime.utcnow()
        assignment.status = "completed"
    
    # Create history record
    history = models.ComplianceStatusHistory(
        assignment_id=assignment_id,
        old_status=old_stage,
        new_status=new_stage,
        changed_by=user_id,
        remarks=f"Lifecycle stage updated: {old_stage} → {new_stage}"
    )
    db.add(history)
    
    db.commit()
    db.refresh(assignment)
    
    return assignment
```

---

### 1.4 New API Endpoints

Create `backend/routers/assignment_center_router.py`:

```python
"""
Assignment Center Router - Phase 2.2
HEAD_OFFICE assignment review and approval workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..auth import require_head_office
from ..models import User
from .. import crud

router = APIRouter(prefix="/assignment-center", tags=["Assignment Center"])


# Schemas
class ApprovalRequest(BaseModel):
    department_id: int
    assignment_ids: Optional[List[int]] = None


class RejectRequest(BaseModel):
    department_id: int
    assignment_ids: Optional[List[int]] = None


class EditAssignmentRequest(BaseModel):
    assignment_id: int
    new_department_id: int


class PublishRequest(BaseModel):
    batch_id: int


@router.get("/{batch_id}/ai-suggestions")
def get_ai_suggestions(
    batch_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get AI department suggestions for batch
    Grouped by department with confidence scores
    """
    suggestions = crud.get_ai_suggestions_for_batch(db, batch_id)
    return {"batch_id": batch_id, "suggestions": suggestions}


@router.post("/{batch_id}/approve")
def approve_assignments(
    batch_id: int,
    request: ApprovalRequest,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Approve assignments for a department
    """
    count = crud.approve_department_assignments(
        db=db,
        batch_id=batch_id,
        department_id=request.department_id,
        approved_by=current_user.id,
        assignment_ids=request.assignment_ids
    )
    
    return {"status": "success", "approved_count": count}


@router.post("/{batch_id}/reject")
def reject_assignments(
    batch_id: int,
    request: RejectRequest,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Reject/delete assignments for a department
    """
    count = crud.reject_department_assignments(
        db=db,
        batch_id=batch_id,
        department_id=request.department_id,
        assignment_ids=request.assignment_ids
    )
    
    return {"status": "success", "rejected_count": count}


@router.post("/edit-assignment")
def edit_assignment(
    request: EditAssignmentRequest,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Manually reassign to different department
    """
    assignment = crud.edit_assignment_department(
        db=db,
        assignment_id=request.assignment_id,
        new_department_id=request.new_department_id
    )
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return {"status": "success", "assignment_id": assignment.id}


@router.post("/publish")
def publish_batch(
    request: PublishRequest,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Publish all approved assignments
    Makes them visible to departments
    """
    count = crud.publish_batch_assignments(
        db=db,
        batch_id=request.batch_id,
        published_by=current_user.id
    )
    
    # Create audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="publish_batch",
        entity_type="assignment_batch",
        entity_id=request.batch_id,
        details=f"Published {count} assignments"
    )
    
    return {"status": "success", "published_count": count}
```

Create `backend/routers/department_workspace_router.py`:

```python
"""
Department Workspace Router - Phase 2.2
DEPARTMENT user workspace and assignment management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..auth import require_department, get_current_active_user
from ..models import User
from .. import crud

router = APIRouter(prefix="/departments", tags=["Department Workspace"])


class LifecycleUpdateRequest(BaseModel):
    new_stage: str  # accepted, in_progress, completed


@router.get("/my-dashboard")
def get_my_dashboard(
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get department dashboard data
    """
    if not current_user.department_id:
        raise HTTPException(status_code=400, detail="User not assigned to department")
    
    data = crud.get_department_dashboard_data(db, current_user.department_id)
    return data


@router.get("/my-assignments")
def get_my_assignments(
    lifecycle_stage: str = None,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get published assignments for my department
    """
    if not current_user.department_id:
        raise HTTPException(status_code=400, detail="User not assigned to department")
    
    assignments = crud.get_department_assignments(
        db=db,
        department_id=current_user.department_id,
        lifecycle_stage=lifecycle_stage
    )
    
    return {"assignments": assignments}


@router.post("/assignments/{assignment_id}/update-lifecycle")
def update_lifecycle(
    assignment_id: int,
    request: LifecycleUpdateRequest,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Update assignment lifecycle stage
    assigned → accepted → in_progress → completed
    """
    assignment = crud.update_assignment_lifecycle(
        db=db,
        assignment_id=assignment_id,
        new_stage=request.new_stage,
        user_id=current_user.id
    )
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify user has access
    if assignment.department_id != current_user.department_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"status": "success", "lifecycle_stage": assignment.lifecycle_stage}
```

Register routers in `backend/main.py`:

```python
from .routers import (
    auth_router, 
    admin_router, 
    department_router, 
    assignment_batch_router,
    assignment_center_router,  # NEW
    department_workspace_router  # NEW
)

app.include_router(assignment_center_router.router, prefix="/api")
app.include_router(department_workspace_router.router, prefix="/api")
```

---

## 2. Frontend Implementation

Due to space constraints, I'm providing the structure and key components. Full implementation would require creating 15+ new files.

### 2.1 Assignment Center Page Structure

Create `frontend/dashboard/src/pages/AssignmentCenter.jsx`:

**Key Features**:
- List of batches with "Open Assignment" button
- Batch detail view with AI suggestions
- Grouped by department
- Approve/Reject controls
- Publish workflow

**Template Structure**:
```jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function AssignmentCenter() {
  const { api } = useAuth();
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [suggestions, setSuggestions] = useState({});
  
  // Load batches
  useEffect(() => {
    loadBatches();
  }, []);
  
  const loadBatches = async () => {
    const response = await api.get('/assignment-batches');
    setBatches(response.data);
  };
  
  const openAssignment = async (batchId) => {
    const response = await api.get(`/assignment-center/${batchId}/ai-suggestions`);
    setSelectedBatch(batchId);
    setSuggestions(response.data.suggestions);
  };
  
  const approveDepartment = async (deptId) => {
    await api.post(`/assignment-center/${selectedBatch}/approve`, {
      department_id: deptId
    });
    // Reload suggestions
    openAssignment(selectedBatch);
  };
  
  const publishBatch = async () => {
    await api.post('/assignment-center/publish', {
      batch_id: selectedBatch
    });
    alert('Batch published successfully!');
    setSelectedBatch(null);
  };
  
  return (
    <div>
      {!selectedBatch ? (
        <BatchList batches={batches} onOpen={openAssignment} />
      ) : (
        <AssignmentReview 
          suggestions={suggestions}
          onApprove={approveDepartment}
          onPublish={publishBatch}
          onBack={() => setSelectedBatch(null)}
        />
      )}
    </div>
  );
}
```

### 2.2 Department Dashboard Page Structure

Create `frontend/dashboard/src/pages/DepartmentDashboard.jsx`:

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function DepartmentDashboard() {
  const { api, user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  
  useEffect(() => {
    loadDashboard();
  }, []);
  
  const loadDashboard = async () => {
    const response = await api.get('/departments/my-dashboard');
    setDashboardData(response.data);
  };
  
  return (
    <div>
      <h1>My Dashboard</h1>
      {dashboardData && (
        <>
          <MetricsCards data={dashboardData} />
          <TodaysTasks tasks={dashboardData.todays_tasks} />
          <CriticalTasks tasks={dashboardData.critical_tasks} />
        </>
      )}
    </div>
  );
}
```

---

## 3. Integration & Testing

**Testing Checklist**:

1. ✅ Backend starts successfully
2. ✅ Database migration completes
3. ✅ AI suggestions generate correctly
4. ✅ HEAD_OFFICE can approve assignments
5. ✅ HEAD_OFFICE can publish batch
6. ✅ DEPARTMENT sees only published assignments
7. ✅ DEPARTMENT can update lifecycle
8. ✅ State persists across refresh
9. ✅ Role-based access enforced
10. ✅ No Phase 1/2.1 regression

---

## 4. Deployment

**Steps**:
1. Backup database
2. Deploy backend changes
3. Start backend (migration runs automatically)
4. Deploy frontend changes
5. Test end-to-end workflow
6. Monitor for issues

---

## Conclusion

This guide provides the complete specification and templates for Phase 2.2. 

**Estimated Implementation Time**: 
- Backend: 15-20 hours
- Frontend: 20-30 hours  
- Testing: 8-12 hours
- **Total: 40-60 hours**

**Recommendation**: Break into 4 weekly sprints with dedicated team.

