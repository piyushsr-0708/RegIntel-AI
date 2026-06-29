"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from . import models, schemas
from .security import get_password_hash


# User CRUD
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        department_id=user.department_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_login(db: Session, user_id: int):
    """Update user's last login timestamp"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


# Department CRUD
def get_department_by_id(db: Session, dept_id: int) -> Optional[models.Department]:
    """Get department by ID"""
    return db.query(models.Department).filter(models.Department.id == dept_id).first()


def get_department_by_code(db: Session, code: str) -> Optional[models.Department]:
    """Get department by code"""
    return db.query(models.Department).filter(models.Department.code == code).first()


def get_all_departments(db: Session) -> List[models.Department]:
    """Get all departments"""
    return db.query(models.Department).all()


def create_department(db: Session, dept: schemas.DepartmentCreate) -> models.Department:
    """Create new department"""
    db_dept = models.Department(
        name=dept.name,
        code=dept.code,
        description=dept.description
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept


# Document CRUD
def create_document(
    db: Session, 
    filename: str,
    original_filename: str,
    file_path: str,
    file_size: int,
    document_type: str,
    uploaded_by: int
) -> models.Document:
    """Create document record"""
    db_doc = models.Document(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        document_type=document_type,
        uploaded_by=uploaded_by
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


def get_document_by_id(db: Session, doc_id: int) -> Optional[models.Document]:
    """Get document by ID"""
    return db.query(models.Document).filter(models.Document.id == doc_id).first()


def get_all_documents(db: Session, skip: int = 0, limit: int = 100) -> List[models.Document]:
    """Get all documents with pagination"""
    return db.query(models.Document).offset(skip).limit(limit).all()


def get_document_by_id(db: Session, doc_id: int) -> Optional[models.Document]:
    """Get document by ID"""
    return db.query(models.Document).filter(models.Document.id == doc_id).first()


def mark_document_processed(db: Session, doc_id: int):
    """Mark document as processed"""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if doc:
        doc.processed = True
        doc.processed_at = datetime.utcnow()
        db.commit()


# Requirement CRUD
def create_requirement(db: Session, req: schemas.RequirementCreate) -> models.Requirement:
    """Create requirement record"""
    db_req = models.Requirement(**req.dict())
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req


def get_requirement_by_id(db: Session, req_id: int) -> Optional[models.Requirement]:
    """Get requirement by ID"""
    return db.query(models.Requirement).filter(models.Requirement.id == req_id).first()


def get_requirement_by_requirement_id(db: Session, requirement_id: str) -> Optional[models.Requirement]:
    """Get requirement by requirement_id string"""
    return db.query(models.Requirement).filter(models.Requirement.requirement_id == requirement_id).first()


def get_all_requirements(db: Session, skip: int = 0, limit: int = 100) -> List[models.Requirement]:
    """Get all requirements with pagination"""
    return db.query(models.Requirement).offset(skip).limit(limit).all()


def get_requirements_by_document(db: Session, document_id: int) -> List[models.Requirement]:
    """Get all requirements for a specific document"""
    return db.query(models.Requirement).filter(
        models.Requirement.document_id == document_id
    ).all()


def get_assignments_by_requirements(db: Session, requirement_ids: List[int]) -> List[models.Assignment]:
    """Get all assignments for a list of requirement IDs"""
    return db.query(models.Assignment).filter(
        models.Assignment.requirement_id.in_(requirement_ids)
    ).all()


def get_unassigned_requirements(db: Session) -> List[models.Requirement]:
    """Get requirements that haven't been assigned to any department"""
    assigned_req_ids = db.query(models.Assignment.requirement_id).distinct()
    return db.query(models.Requirement).filter(
        ~models.Requirement.id.in_(assigned_req_ids)
    ).all()


# Assignment CRUD
def create_assignment(
    db: Session,
    requirement_id: int,
    department_id: int,
    assigned_by: int
) -> models.Assignment:
    """Create assignment"""
    db_assignment = models.Assignment(
        requirement_id=requirement_id,
        department_id=department_id,
        assigned_by=assigned_by
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def get_assignment_by_id(db: Session, assignment_id: int) -> Optional[models.Assignment]:
    """Get assignment by ID"""
    return db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()


def get_assignments_by_department(
    db: Session,
    department_id: int,
    status: Optional[str] = None
) -> List[models.Assignment]:
    """Get assignments for a department, optionally filtered by status"""
    query = db.query(models.Assignment).filter(models.Assignment.department_id == department_id)
    if status:
        query = query.filter(models.Assignment.status == status)
    return query.all()


def get_all_assignments(db: Session, skip: int = 0, limit: int = 100) -> List[models.Assignment]:
    """Get all assignments with pagination"""
    return db.query(models.Assignment).offset(skip).limit(limit).all()


def update_assignment_status(
    db: Session,
    assignment_id: int,
    new_status: str,
    remarks: Optional[str],
    changed_by: int
) -> models.Assignment:
    """Update assignment status and create history record"""
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        return None
    
    old_status = assignment.status
    
    # Update assignment
    assignment.status = new_status
    assignment.remarks = remarks
    assignment.updated_at = datetime.utcnow()
    
    if new_status == "completed":
        assignment.completed_at = datetime.utcnow()
    
    # Create history record
    history = models.ComplianceStatusHistory(
        assignment_id=assignment_id,
        old_status=old_status,
        new_status=new_status,
        remarks=remarks,
        changed_by=changed_by
    )
    db.add(history)
    
    db.commit()
    db.refresh(assignment)
    return assignment


# Audit Log CRUD
def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """Create audit log entry"""
    log = models.AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()


def get_audit_logs(
    db: Session,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.AuditLog]:
    """Get audit logs with optional user filter"""
    query = db.query(models.AuditLog)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()


# Dashboard Statistics
def get_dashboard_summary(db: Session) -> dict:
    """Get overall dashboard summary statistics"""
    total_docs = db.query(func.count(models.Document.id)).scalar()
    total_reqs = db.query(func.count(models.Requirement.id)).scalar()
    total_assignments = db.query(func.count(models.Assignment.id)).scalar()
    
    # Operational metrics - only published assignments
    pending = db.query(func.count(models.Assignment.id)).filter(
        models.Assignment.status == "pending",
        models.Assignment.is_published == True
    ).scalar() or 0
    
    in_progress = db.query(func.count(models.Assignment.id)).filter(
        models.Assignment.status == "in_progress",
        models.Assignment.is_published == True
    ).scalar() or 0
    
    completed = db.query(func.count(models.Assignment.id)).filter(
        models.Assignment.status == "completed",
        models.Assignment.is_published == True
    ).scalar() or 0
    
    completion_pct = (completed / total_assignments * 100) if total_assignments > 0 else 0.0
    
    # New operational metrics
    published_maps = db.query(func.count(models.Assignment.id)).filter(models.Assignment.is_published == True).scalar() or 0
    unpublished_maps = total_assignments - published_maps
    
    departments_impacted = db.query(func.count(func.distinct(models.Assignment.department_id))).filter(models.Assignment.is_published == True).scalar() or 0
    
    # Priority logic: aggregate priority from Assignment, fallback to Requirement - only published
    from datetime import timedelta
    now = datetime.utcnow()
    upcoming_limit = now + timedelta(days=30)
    
    assignments = db.query(models.Assignment, models.Requirement).filter(
        models.Assignment.is_published == True
    ).outerjoin(models.Requirement).all()
    priority_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    upcoming_deadlines = 0
    
    for a, r in assignments:
        p = a.priority if a.priority else (r.priority if r else "Medium")
        if p in priority_dist:
            priority_dist[p] += 1
            
        # Only count assignments with actual due_date within 30 days
        if a.due_date and a.due_date <= upcoming_limit:
            upcoming_deadlines += 1
            
    return {
        "total_documents": total_docs or 0,
        "total_requirements": total_reqs or 0,
        "total_assignments": total_assignments or 0,
        "pending_count": pending or 0,
        "in_progress_count": in_progress or 0,
        "completed_count": completed or 0,
        "completion_percentage": round(completion_pct, 2),
        "published_maps": published_maps,
        "pending_assignments": pending or 0,
        "completed_assignments": completed or 0,
        "unpublished_assignments": unpublished_maps,
        "critical_assignments": priority_dist["Critical"],
        "high_assignments": priority_dist["High"],
        "departments_impacted": departments_impacted,
        "upcoming_deadlines": upcoming_deadlines,
        "priority_distribution": priority_dist
    }


def get_department_dashboard(db: Session, department_id: int) -> dict:
    """Get dashboard summary for specific department"""
    department = get_department_by_id(db, department_id)
    if not department:
        return None
    
    assignments = get_assignments_by_department(db, department_id)
    total = len(assignments)
    
    pending = sum(1 for a in assignments if a.status == "pending")
    in_progress = sum(1 for a in assignments if a.status == "in_progress")
    completed = sum(1 for a in assignments if a.status == "completed")
    
    completion_pct = (completed / total * 100) if total > 0 else 0.0
    
    # Get recent assignments (last 10)
    recent = db.query(models.Assignment).filter(
        models.Assignment.department_id == department_id
    ).order_by(models.Assignment.assigned_at.desc()).limit(10).all()
    
    return {
        "department_id": department_id,
        "department_name": department.name,
        "total_assigned": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "completion_percentage": round(completion_pct, 2),
        "recent_assignments": recent
    }


# ============================================================================
# MVP DEMO - Simple Assignment Workflow
# ============================================================================

def get_unpublished_assignment_summary(db: Session) -> dict:
    """
    Get summary of unpublished assignments grouped by department
    """
    # Initialize all departments first to ensure 0-count departments are included
    departments = get_all_departments(db)
    dept_summary = {}
    for dept in departments:
        dept_summary[dept.id] = {
            "department_id": dept.id,
            "department_name": dept.name,
            "department_code": dept.code,
            "task_count": 0,
            "requirements": []
        }
        
    # Get unpublished assignments
    assignments = db.query(models.Assignment).filter(
        models.Assignment.is_published == False
    ).all()
    
    # Group by department
    for assignment in assignments:
        dept_id = assignment.department_id
        if dept_id in dept_summary:
            dept_summary[dept_id]["task_count"] += 1
            dept_summary[dept_id]["requirements"].append({
                "assignment_id": assignment.id,
                "requirement_id": assignment.requirement.id,
                "requirement_text": assignment.requirement.text,
                "priority": assignment.requirement.priority,
                "domain": assignment.requirement.domain
            })
    
    return dept_summary


def publish_department_assignments(db: Session, department_id: int) -> int:
    """Publish assignments for a specific department"""
    count = db.query(models.Assignment).filter(
        models.Assignment.department_id == department_id,
        models.Assignment.is_published == False
    ).update({"is_published": True})
    
    db.commit()
    return count


def get_published_assignments_for_department(db: Session, department_id: int):
    """Get published assignments for department (department user view)"""
    return db.query(models.Assignment).filter(
        models.Assignment.department_id == department_id,
        models.Assignment.is_published == True
    ).all()


def mark_assignment_completed(db: Session, assignment_id: int, user_id: int):
    """Mark assignment as completed"""
    assignment = db.query(models.Assignment).filter(
        models.Assignment.id == assignment_id
    ).first()
    
    if assignment:
        old_status = assignment.status
        assignment.status = models.ComplianceStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        
        # Create status history
        history = models.ComplianceStatusHistory(
            assignment_id=assignment_id,
            old_status=old_status,
            new_status=models.ComplianceStatus.COMPLETED,
            changed_by=user_id,
            remarks="Marked as completed"
        )
        db.add(history)
        
        db.commit()
        db.refresh(assignment)
    
    return assignment


def get_admin_completion_summary(db: Session) -> list:
    """Get completion summary for all departments (admin view)"""
    departments = get_all_departments(db)
    summary = []
    
    for dept in departments:
        assignments = db.query(models.Assignment).filter(
            models.Assignment.department_id == dept.id,
            models.Assignment.is_published == True
        ).all()
        
        total = len(assignments)
        completed = sum(1 for a in assignments if a.status == models.ComplianceStatus.COMPLETED)
        remaining = total - completed
        
        summary.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "assigned": total,
            "completed": completed,
            "remaining": remaining
        })
    
    return summary


def get_department_risk_summary(db: Session) -> list:
    """
    Compute per-department risk from live Assignment data.
    Risk score = Critical*40 + High*20 + Medium*5 + Low*1
    Normalized to 0-100 across all departments.
    """
    PRIORITY_WEIGHTS = {"Critical": 40, "High": 20, "Medium": 5, "Low": 1}
    departments = get_all_departments(db)
    raw = []

    for dept in departments:
        assignments = db.query(models.Assignment).filter(
            models.Assignment.department_id == dept.id
        ).all()

        priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for a in assignments:
            p = a.priority
            if not p:
                req = db.query(models.Requirement).filter(
                    models.Requirement.id == a.requirement_id
                ).first()
                p = req.priority if req and req.priority else "Medium"
            if p in priority_counts:
                priority_counts[p] += 1

        raw_score = sum(priority_counts[k] * PRIORITY_WEIGHTS[k] for k in priority_counts)
        total_maps = len(assignments)
        completed = sum(1 for a in assignments if a.status == models.ComplianceStatus.COMPLETED)

        raw.append({
            "department_id": dept.id,
            "department": dept.name,
            "total_maps": total_maps,
            "critical_count": priority_counts["Critical"],
            "high_count": priority_counts["High"],
            "medium_count": priority_counts["Medium"],
            "low_count": priority_counts["Low"],
            "completed": completed,
            "raw_score": raw_score,
        })

    # Normalize to 0-100
    max_raw = max((d["raw_score"] for d in raw), default=1) or 1
    for d in raw:
        d["risk_score"] = round(d["raw_score"] / max_raw * 100, 1)
        del d["raw_score"]

    # Sort by risk_score descending
    raw.sort(key=lambda d: d["risk_score"], reverse=True)
    return raw


# Assignment Batch CRUD
def create_assignment_batch(
    db: Session,
    batch_name: str,
    circular_name: str,
    uploaded_by: int
) -> models.AssignmentBatch:
    """Create a new assignment batch"""
    batch = models.AssignmentBatch(
        batch_name=batch_name,
        circular_name=circular_name,
        uploaded_by=uploaded_by,
        status="draft"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def get_assignment_batch_by_id(db: Session, batch_id: int) -> Optional[models.AssignmentBatch]:
    """Get assignment batch by ID"""
    return db.query(models.AssignmentBatch).filter(models.AssignmentBatch.id == batch_id).first()


def get_all_assignment_batches(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.AssignmentBatch]:
    """Get all assignment batches with pagination"""
    return db.query(models.AssignmentBatch).order_by(
        models.AssignmentBatch.uploaded_at.desc()
    ).offset(skip).limit(limit).all()


def update_assignment_batch_status(
    db: Session,
    batch_id: int,
    new_status: str
) -> Optional[models.AssignmentBatch]:
    """Update assignment batch status"""
    batch = db.query(models.AssignmentBatch).filter(models.AssignmentBatch.id == batch_id).first()
    if not batch:
        return None
    
    batch.status = new_status
    db.commit()
    db.refresh(batch)
    return batch


def update_assignment_batch_metrics(
    db: Session,
    batch_id: int
) -> Optional[models.AssignmentBatch]:
    """Calculate and update batch metrics (requirements, MAPs, completion %)"""
    batch = db.query(models.AssignmentBatch).filter(models.AssignmentBatch.id == batch_id).first()
    if not batch:
        return None
    
    # Count requirements
    total_reqs = db.query(func.count(models.Requirement.id)).filter(
        models.Requirement.batch_id == batch_id
    ).scalar() or 0
    
    # Count assignments (MAPs)
    total_maps = db.query(func.count(models.Assignment.id)).filter(
        models.Assignment.batch_id == batch_id
    ).scalar() or 0
    
    # Calculate completion
    completed_maps = db.query(func.count(models.Assignment.id)).filter(
        models.Assignment.batch_id == batch_id,
        models.Assignment.status == "completed"
    ).scalar() or 0
    
    # Calculate verification (Phase 2.2 feature - for now same as completion)
    verified_maps = completed_maps
    
    completion_pct = int((completed_maps / total_maps * 100)) if total_maps > 0 else 0
    verification_pct = int((verified_maps / total_maps * 100)) if total_maps > 0 else 0
    
    # Update batch
    batch.total_requirements = total_reqs
    batch.total_maps = total_maps
    batch.completion_percentage = completion_pct
    batch.verification_percentage = verification_pct
    
    db.commit()
    db.refresh(batch)
    return batch


def get_batch_department_distribution(db: Session, batch_id: int) -> dict:
    """Get department distribution for a batch"""
    assignments = db.query(models.Assignment).filter(
        models.Assignment.batch_id == batch_id
    ).all()
    
    dept_counts = {}
    for assignment in assignments:
        dept = assignment.department
        if dept:
            dept_name = dept.name
            dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
    
    return dept_counts


def get_batch_priority_distribution(db: Session, batch_id: int) -> dict:
    """Get priority distribution for a batch"""
    requirements = db.query(models.Requirement).filter(
        models.Requirement.batch_id == batch_id
    ).all()
    
    priority_counts = {}
    for req in requirements:
        priority = req.priority or "unknown"
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    return priority_counts
