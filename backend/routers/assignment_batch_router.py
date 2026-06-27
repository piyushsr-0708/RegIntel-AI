"""
Assignment Batch Router - Phase 2.1
Manages Assignment Batches (Compliance Campaigns)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth import require_head_office, get_current_active_user
from ..models import User
from .. import crud, schemas

router = APIRouter(prefix="/assignment-batches", tags=["Assignment Batches"])


@router.post("/create", response_model=schemas.AssignmentBatchResponse)
def create_assignment_batch(
    batch: schemas.AssignmentBatchCreate,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Create a new Assignment Batch
    
    HEAD_OFFICE role required.
    
    This is typically called after uploading a circular document.
    The batch serves as the central workflow object for all requirements
    and MAPs generated from that circular.
    """
    # Create batch
    db_batch = crud.create_assignment_batch(
        db=db,
        batch_name=batch.batch_name,
        circular_name=batch.circular_name,
        uploaded_by=current_user.id
    )
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_batch",
        entity_type="assignment_batch",
        entity_id=db_batch.id,
        details=f"Created assignment batch: {batch.batch_name}"
    )
    
    return db_batch


@router.get("", response_model=List[schemas.AssignmentBatchResponse])
def get_assignment_batches(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get all Assignment Batches
    
    HEAD_OFFICE role required.
    
    Returns list of batches ordered by most recent first.
    """
    batches = crud.get_all_assignment_batches(db, skip=skip, limit=limit)
    return batches


@router.get("/{batch_id}", response_model=schemas.AssignmentBatchResponse)
def get_assignment_batch(
    batch_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get Assignment Batch by ID
    
    HEAD_OFFICE role required.
    
    Returns complete batch information including metrics.
    """
    batch = crud.get_assignment_batch_by_id(db, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment batch not found"
        )
    
    return batch


@router.get("/{batch_id}/summary", response_model=schemas.AssignmentBatchSummary)
def get_assignment_batch_summary(
    batch_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get Assignment Batch Summary with Distribution Data
    
    HEAD_OFFICE role required.
    
    Returns batch information plus:
    - Department distribution (how many MAPs per department)
    - Priority distribution (how many requirements per priority)
    - Uploader name
    """
    batch = crud.get_assignment_batch_by_id(db, batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment batch not found"
        )
    
    # Get distribution data
    dept_distribution = crud.get_batch_department_distribution(db, batch_id)
    priority_distribution = crud.get_batch_priority_distribution(db, batch_id)
    
    # Get uploader name
    uploader = crud.get_user_by_id(db, batch.uploaded_by)
    uploader_name = uploader.full_name or uploader.username if uploader else "Unknown"
    
    # Build response
    response = schemas.AssignmentBatchSummary(
        id=batch.id,
        batch_name=batch.batch_name,
        circular_name=batch.circular_name,
        uploaded_by=batch.uploaded_by,
        uploaded_at=batch.uploaded_at,
        status=batch.status,
        total_requirements=batch.total_requirements,
        total_maps=batch.total_maps,
        completion_percentage=batch.completion_percentage,
        verification_percentage=batch.verification_percentage,
        department_distribution=dept_distribution,
        priority_distribution=priority_distribution,
        uploader_name=uploader_name
    )
    
    return response


@router.patch("/{batch_id}/status", response_model=schemas.AssignmentBatchResponse)
def update_assignment_batch_status(
    batch_id: int,
    status_update: schemas.AssignmentBatchStatusUpdate,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Update Assignment Batch Status
    
    HEAD_OFFICE role required.
    
    Valid transitions:
    - draft → pending_approval → published → in_progress → completed → closed
    """
    batch = crud.update_assignment_batch_status(
        db=db,
        batch_id=batch_id,
        new_status=status_update.status.value
    )
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment batch not found"
        )
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update_batch_status",
        entity_type="assignment_batch",
        entity_id=batch_id,
        details=f"Updated batch status to: {status_update.status.value}"
    )
    
    return batch


@router.post("/{batch_id}/refresh-metrics", response_model=schemas.AssignmentBatchResponse)
def refresh_batch_metrics(
    batch_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Refresh Assignment Batch Metrics
    
    HEAD_OFFICE role required.
    
    Recalculates:
    - total_requirements
    - total_maps
    - completion_percentage
    - verification_percentage
    
    Call this after processing completes or when assignments change.
    """
    batch = crud.update_assignment_batch_metrics(db=db, batch_id=batch_id)
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment batch not found"
        )
    
    return batch
