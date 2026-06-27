"""
Admin router - HEAD_OFFICE operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime
from ..database import get_db
from ..auth import require_head_office
from ..models import User
from .. import crud, schemas

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def get_admin_dashboard(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard summary
    """
    summary = crud.get_dashboard_summary(db)
    return summary


@router.post("/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "RBI_Circular",
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Upload RBI circular or regulatory document
    
    Saves file to uploads/ directory and creates database record
    """
    # Create uploads directory if not exists
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create database record
    document = crud.create_document(
        db=db,
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        document_type=document_type,
        uploaded_by=current_user.id
    )
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="upload",
        entity_type="document",
        entity_id=document.id,
        details=f"Uploaded document: {file.filename}"
    )
    
    return document


@router.post("/process-document/{document_id}")
async def process_document(
    document_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Process uploaded document - simulates pipeline for MVP demo
    Creates requirements and assignments for Assignment Center
    """
    # Get document
    document = crud.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get all departments for assignment
    departments = crud.get_all_departments(db)
    if not departments:
        raise HTTPException(status_code=500, detail="No departments found")
    
    # Simulate pipeline processing - create sample requirements
    # In real system, this would call actual AI pipeline
    sample_requirements = [
        # KYC/AML/Compliance requirements
        {"domain": "KYC", "text": "Banks must implement enhanced customer due diligence procedures for high-risk customers", "classification": "Mandatory", "priority": "Critical"},
        {"domain": "AML", "text": "Suspicious transaction monitoring systems must be updated to detect new patterns", "classification": "Mandatory", "priority": "High"},
        {"domain": "Compliance", "text": "Annual compliance audit reports must be submitted to RBI within 90 days", "classification": "Mandatory", "priority": "High"},
        {"domain": "KYC", "text": "Customer identification documents must be verified within 24 hours of account opening", "classification": "Mandatory", "priority": "Critical"},
        {"domain": "AML", "text": "Cash transaction reports exceeding threshold limits must be filed within prescribed timeframe", "classification": "Mandatory", "priority": "High"},
        # Cyber Security requirements
        {"domain": "Cybersecurity", "text": "Multi-factor authentication must be implemented for all digital banking channels", "classification": "Mandatory", "priority": "Critical"},
        {"domain": "Cybersecurity", "text": "Security incident response team must be available 24x7", "classification": "Mandatory", "priority": "High"},
        {"domain": "Cyber", "text": "Regular penetration testing of all internet-facing systems is required", "classification": "Mandatory", "priority": "Medium"},
        # Risk Management requirements
        {"domain": "Risk", "text": "Credit risk assessment models must be validated annually", "classification": "Mandatory", "priority": "High"},
        {"domain": "Risk Management", "text": "Operational risk events must be reported to board within 48 hours", "classification": "Mandatory", "priority": "Critical"},
        # Treasury requirements
        {"domain": "Treasury", "text": "Daily liquidity coverage ratio must meet minimum regulatory threshold", "classification": "Mandatory", "priority": "High"},
        {"domain": "Treasury", "text": "Interest rate risk measurement must be performed quarterly", "classification": "Recommended", "priority": "Medium"},
        # Operations requirements
        {"domain": "Operations", "text": "Business continuity plan must be tested semi-annually", "classification": "Mandatory", "priority": "Medium"},
        {"domain": "Operations", "text": "Customer complaints must be resolved within specified timelines", "classification": "Mandatory", "priority": "High"},
    ]
    
    # Department mapping
    dept_mapping = {
        'KYC': 'Compliance',
        'AML': 'Compliance',
        'Compliance': 'Compliance',
        'Cybersecurity': 'Cyber Security',
        'Cyber': 'Cyber Security',
        'Risk': 'Risk Management',
        'Risk Management': 'Risk Management',
        'Treasury': 'Treasury',
        'Operations': 'Operations'
    }
    
    created_count = 0
    assignment_count = 0
    
    # Create requirements and assignments
    for idx, req_data in enumerate(sample_requirements):
        # Create requirement
        req_id = f"REQ_{document.original_filename[:10].upper()}_{idx:04d}"
        
        # Check if requirement already exists
        existing_req = crud.get_requirement_by_requirement_id(db, req_id)
        if existing_req:
            continue
        
        requirement = crud.create_requirement(db, schemas.RequirementCreate(
            requirement_id=req_id,
            document_id=document_id,
            text=req_data["text"],
            classification=req_data["classification"],
            domain=req_data["domain"],
            priority=req_data["priority"],
            source_reference=document.original_filename
        ))
        created_count += 1
        
        # Determine department and create assignment
        dept_name = dept_mapping.get(req_data["domain"], "Compliance")
        department = next((d for d in departments if d.name == dept_name), departments[0])
        
        if department:
            # Create unpublished assignment
            assignment = crud.create_assignment(
                db=db,
                requirement_id=requirement.id,
                department_id=department.id,
                assigned_by=current_user.id
            )
            assignment_count += 1
    
    # Mark document as processed
    crud.mark_document_processed(db, document_id)
    
    # Create audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="process_document",
        entity_type="document",
        entity_id=document_id,
        details=f"Processed document: {document.original_filename}, created {created_count} requirements and {assignment_count} assignments"
    )
    
    return {
        "status": "success",
        "document_id": document_id,
        "requirements_created": created_count,
        "assignments_created": assignment_count,
        "message": f"Document processed successfully. Created {created_count} requirements and {assignment_count} assignments."
    }


@router.get("/documents", response_model=List[schemas.DocumentResponse])
def get_all_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get all uploaded documents
    """
    documents = crud.get_all_documents(db, skip=skip, limit=limit)
    return documents


@router.get("/requirements", response_model=List[schemas.RequirementResponse])
def get_all_requirements(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get all extracted requirements
    """
    requirements = crud.get_all_requirements(db, skip=skip, limit=limit)
    return requirements


@router.get("/requirements/unassigned", response_model=List[schemas.RequirementResponse])
def get_unassigned_requirements(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get requirements that haven't been assigned to any department
    """
    requirements = crud.get_unassigned_requirements(db)
    return requirements


@router.post("/assignments", response_model=schemas.AssignmentResponse)
def create_assignment(
    assignment: schemas.AssignmentCreate,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Assign requirement to department
    """
    # Verify requirement exists
    requirement = crud.get_requirement_by_id(db, assignment.requirement_id)
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # Verify department exists
    department = crud.get_department_by_id(db, assignment.department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Create assignment
    db_assignment = crud.create_assignment(
        db=db,
        requirement_id=assignment.requirement_id,
        department_id=assignment.department_id,
        assigned_by=current_user.id
    )
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="assign_requirement",
        entity_type="assignment",
        entity_id=db_assignment.id,
        details=f"Assigned requirement {requirement.requirement_id} to {department.name}"
    )
    
    return db_assignment


@router.post("/assignments/bulk", response_model=List[schemas.AssignmentResponse])
def create_bulk_assignments(
    bulk_assignment: schemas.AssignmentBulkCreate,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Assign multiple requirements to a department at once
    """
    # Verify department exists
    department = crud.get_department_by_id(db, bulk_assignment.department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    assignments = []
    for req_id in bulk_assignment.requirement_ids:
        # Verify requirement exists
        requirement = crud.get_requirement_by_id(db, req_id)
        if not requirement:
            continue  # Skip invalid requirements
        
        # Create assignment
        db_assignment = crud.create_assignment(
            db=db,
            requirement_id=req_id,
            department_id=bulk_assignment.department_id,
            assigned_by=current_user.id
        )
        assignments.append(db_assignment)
    
    # Audit log
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="bulk_assign",
        entity_type="assignment",
        details=f"Bulk assigned {len(assignments)} requirements to {department.name}"
    )
    
    return assignments


@router.get("/assignments", response_model=List[schemas.AssignmentResponse])
def get_all_assignments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get all assignments across all departments
    """
    assignments = crud.get_all_assignments(db, skip=skip, limit=limit)
    return assignments


@router.get("/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get all departments
    """
    departments = crud.get_all_departments(db)
    return departments


@router.get("/audit-logs", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get audit logs
    """
    logs = crud.get_audit_logs(db, skip=skip, limit=limit)
    return logs
