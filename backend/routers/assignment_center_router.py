"""
Assignment Center Router - MVP Demo
Simple workflow: Review assignments → Publish → Department sees tasks
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..auth import require_head_office
from ..models import User
from .. import crud

router = APIRouter(prefix="/assignment-center", tags=["Assignment Center"])


class PublishRequest(BaseModel):
    department_id: int


@router.get("/summary")
def get_assignment_summary(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get unpublished assignments grouped by department
    Shows after pipeline completes
    """
    summary = crud.get_unpublished_assignment_summary(db)
    
    # Get total MAPs
    total_maps = sum(dept["task_count"] for dept in summary.values())
    
    return {
        "total_maps": total_maps,
        "departments": list(summary.values())
    }


@router.post("/publish")
def publish_assignments(
    request: PublishRequest,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Publish assignments for a specific department
    Makes them visible to department users
    """
    count = crud.publish_department_assignments(db, request.department_id)
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="publish_assignments",
        entity_type="department",
        entity_id=request.department_id,
        details=f"Published {count} assignments"
    )
    
    return {"status": "success", "published_count": count}


@router.get("/admin-summary")
def get_admin_summary(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get completion summary for admin dashboard
    Shows: Department | Assigned | Completed | Remaining
    """
    summary = crud.get_admin_completion_summary(db)
    return {"departments": summary}
