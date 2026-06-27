"""
Department Workspace Router - MVP Demo
Simple workflow: View assigned tasks → Mark completed
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import require_department
from ..models import User
from .. import crud, schemas

router = APIRouter(prefix="/departments/workspace", tags=["Department Workspace"])


@router.get("/my-tasks")
def get_my_tasks(
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Get published assignments for my department
    Simple task list
    """
    if not current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not assigned to department"
        )
    
    assignments = crud.get_published_assignments_for_department(
        db, current_user.department_id
    )
    
    # Format response
    tasks = []
    for assignment in assignments:
        req = assignment.requirement
        tasks.append({
            "assignment_id": assignment.id,
            "requirement_id": req.id,
            "requirement_text": req.text,
            "priority": req.priority or "medium",
            "domain": req.domain or "general",
            "status": assignment.status.value if hasattr(assignment.status, 'value') else str(assignment.status),
            "assigned_at": assignment.assigned_at.isoformat(),
            "completed_at": assignment.completed_at.isoformat() if assignment.completed_at else None
        })
    
    return {
        "department_name": current_user.department.name,
        "total_tasks": len(tasks),
        "completed_count": sum(1 for t in tasks if t["status"] == "completed"),
        "tasks": tasks
    }


@router.post("/tasks/{assignment_id}/complete")
def mark_task_completed(
    assignment_id: int,
    current_user: User = Depends(require_department),
    db: Session = Depends(get_db)
):
    """
    Mark task as completed
    Simple status update: ASSIGNED → COMPLETED
    """
    # Get assignment
    assignment = crud.get_assignment_by_id(db, assignment_id)
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify user has access (same department)
    if assignment.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Mark completed
    assignment = crud.mark_assignment_completed(db, assignment_id, current_user.id)
    
    return {
        "status": "success",
        "assignment_id": assignment_id,
        "new_status": "completed"
    }
