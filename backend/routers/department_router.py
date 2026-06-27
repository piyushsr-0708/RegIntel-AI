"""
Department router - DEPARTMENT user operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..auth import require_department
from ..models import User
from .. import crud, schemas

router = APIRouter(prefix="/department", tags=["Department"])


@router.get("/dashboard")
def get_department_dashboard(
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get department-specific dashboard
    """
    dashboard = crud.get_department_dashboard(db, current_user.department_id)
    
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return dashboard


@router.get("/assignments", response_model=List[schemas.AssignmentDetail])
def get_my_assignments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get assignments for current user's department
    
    Args:
        status_filter: Optional filter by status (pending, in_progress, completed)
    """
    assignments = crud.get_assignments_by_department(
        db,
        current_user.department_id,
        status=status_filter
    )
    
    # Enrich with requirement and department details
    result = []
    for assignment in assignments:
        requirement = crud.get_requirement_by_id(db, assignment.requirement_id)
        department = crud.get_department_by_id(db, assignment.department_id)
        
        if requirement and department:
            result.append({
                "id": assignment.id,
                "requirement_id": assignment.requirement_id,
                "department_id": assignment.department_id,
                "assigned_by": assignment.assigned_by,
                "assigned_at": assignment.assigned_at,
                "status": assignment.status,
                "remarks": assignment.remarks,
                "updated_at": assignment.updated_at,
                "completed_at": assignment.completed_at,
                "requirement": requirement,
                "department_name": department.name
            })
    
    return result


@router.put("/assignments/{assignment_id}", response_model=schemas.AssignmentResponse)
def update_assignment(
    assignment_id: int,
    update: schemas.AssignmentUpdate,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Update assignment status and remarks
    
    Department users can only update assignments for their own department
    """
    # Get assignment
    assignment = crud.get_assignment_by_id(db, assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Verify assignment belongs to user's department
    if assignment.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update assignments for your own department"
        )
    
    # Update status
    updated_assignment = crud.update_assignment_status(
        db=db,
        assignment_id=assignment_id,
        new_status=update.status.value,
        remarks=update.remarks,
        changed_by=current_user.id
    )
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update_status",
        entity_type="assignment",
        entity_id=assignment_id,
        details=f"Updated status to {update.status.value}"
    )
    
    return updated_assignment


@router.get("/assignments/{assignment_id}/history", response_model=List[schemas.StatusHistoryResponse])
def get_assignment_history(
    assignment_id: int,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get status change history for an assignment
    """
    # Get assignment
    assignment = crud.get_assignment_by_id(db, assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Verify assignment belongs to user's department
    if assignment.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view history for your own department"
        )
    
    # Get history
    from ..models import ComplianceStatusHistory
    history = db.query(ComplianceStatusHistory).filter(
        ComplianceStatusHistory.assignment_id == assignment_id
    ).order_by(ComplianceStatusHistory.changed_at.desc()).all()
    
    return history


@router.get("/requirements/{requirement_id}", response_model=schemas.RequirementResponse)
def get_requirement_detail(
    requirement_id: int,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific requirement
    
    Department users can only access requirements assigned to their department
    """
    # Verify requirement is assigned to user's department
    assignment = db.query(crud.models.Assignment).filter(
        crud.models.Assignment.requirement_id == requirement_id,
        crud.models.Assignment.department_id == current_user.department_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This requirement is not assigned to your department"
        )
    
    # Get requirement details
    requirement = crud.get_requirement_by_id(db, requirement_id)
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    return requirement
