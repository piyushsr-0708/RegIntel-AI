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
from ..auth import require_head_office, get_current_active_user
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
    
    # DIAGNOSTIC: Log document details
    print(f"[PROCESS] ========== PROCESSING DOCUMENT_ID={document_id} ==========")
    print(f"[PROCESS] original_filename: {document.original_filename}")
    print(f"[PROCESS] filename prefix (first 10 chars): {document.original_filename[:10].upper()}")
    
    # Create requirements and assignments
    for idx, req_data in enumerate(sample_requirements):
        # Create requirement with document_id in requirement_id to ensure uniqueness across documents
        req_id = f"REQ_DOC{document_id}_{idx:04d}"
        
        print(f"[PROCESS] --- Requirement {idx} ---")
        print(f"[PROCESS] Generated req_id: {req_id}")
        
        # Check if requirement already exists FOR THIS DOCUMENT
        # This prevents duplicate requirements within the same document during reprocessing
        existing_req = crud.get_requirement_by_requirement_id(db, req_id)
        
        if existing_req:
            print(f"[PROCESS] ⚠️  DUPLICATE FOUND: {req_id} already exists!")
            print(f"[PROCESS]     Existing requirement.id: {existing_req.id}")
            print(f"[PROCESS]     Existing requirement.document_id: {existing_req.document_id}")
            print(f"[PROCESS]     SKIPPING creation for this requirement")
            continue
        else:
            print(f"[PROCESS] ✓ No duplicate found, creating requirement: {req_id}")
        
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
        
        print(f"[PROCESS] ✓ Requirement created: {req_id} (id={requirement.id}, document_id={requirement.document_id})")
        
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
            print(f"[PROCESS] ✓ Assignment created: id={assignment.id}, requirement_id={assignment.requirement_id}, dept={department.name}")
    
    print(f"[PROCESS] ========== PROCESSING COMPLETE ==========")
    print(f"[PROCESS] FINAL created_count: {created_count}")
    print(f"[PROCESS] FINAL assignment_count: {assignment_count}")
    print(f"[PROCESS] ==========================================")
    
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


@router.get("/requirements/by-semantic-id/{semantic_id}", response_model=schemas.RequirementResponse)
def get_requirement_by_semantic_id(
    semantic_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get requirement by semantic requirement_id (e.g., REQ_CIRCULAR_0001)
    """
    requirement = crud.get_requirement_by_requirement_id(db, semantic_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement


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


@router.get("/assignments/{assignment_id}", response_model=schemas.AssignmentDetail)
def get_assignment_detail(
    assignment_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific assignment including requirement text
    """
    assignment = crud.get_assignment_by_id(db, assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Get requirement details
    requirement = crud.get_requirement_by_id(db, assignment.requirement_id)
    
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated requirement not found"
        )
    
    # Get department name
    department = crud.get_department_by_id(db, assignment.department_id)
    department_name = department.name if department else "Unknown"
    
    # Build AssignmentDetail response
    return schemas.AssignmentDetail(
        id=assignment.id,
        requirement_id=assignment.requirement_id,
        department_id=assignment.department_id,
        assigned_by=assignment.assigned_by,
        assigned_at=assignment.assigned_at,
        status=assignment.status,
        remarks=assignment.remarks,
        updated_at=assignment.updated_at,
        completed_at=assignment.completed_at,
        requirement=requirement,
        department_name=department_name
    )


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


@router.get("/document-analysis/{document_id}")
def get_document_analysis(
    document_id: int,
    current_user: User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Get complete analysis data for a processed document
    Returns requirements, assignments, and aggregated stats
    """
    print(f"[BACKEND] ========== GET DOCUMENT ANALYSIS START ==========")
    print(f"[BACKEND] document_id: {document_id}")
    
    # Get document
    document = crud.get_document_by_id(db, document_id)
    if not document:
        print(f"[BACKEND] ERROR: Document not found for id={document_id}")
        raise HTTPException(status_code=404, detail="Document not found")
    
    print(f"[BACKEND] Document found: {document.original_filename}")
    
    # Get requirements for this document
    requirements = crud.get_requirements_by_document(db, document_id)
    print(f"[BACKEND] Requirements fetched: {len(requirements)} rows")
    
    # Get assignments for this document (via requirements)
    requirement_ids = [r.id for r in requirements]
    print(f"[BACKEND] Requirement IDs: {requirement_ids}")
    
    assignments = crud.get_assignments_by_requirements(db, requirement_ids)
    print(f"[BACKEND] Assignments fetched: {len(assignments)} rows")
    
    # Build assignment details with requirement and department info
    assignment_details = []
    for assignment in assignments:
        requirement = next((r for r in requirements if r.id == assignment.requirement_id), None)
        department = crud.get_department_by_id(db, assignment.department_id)
        
        if requirement and department:
            assignment_details.append({
                "id": assignment.id,
                "requirement_id": requirement.requirement_id,
                "requirement_text": requirement.text,
                "department": department.name,
                "department_id": department.id,
                "priority": requirement.priority or "Medium",
                "domain": requirement.domain or "General",
                "classification": requirement.classification or "Mandatory",
                "is_published": assignment.is_published,
                "status": assignment.status.value if assignment.status else "pending"
            })
    
    print(f"[BACKEND] Assignment details built: {len(assignment_details)} items")
    
    # Aggregate stats
    from collections import Counter
    priority_counts = Counter([a["priority"] for a in assignment_details])
    department_counts = Counter([a["department"] for a in assignment_details])
    
    print(f"[BACKEND] Priority counts: {dict(priority_counts)}")
    print(f"[BACKEND] Department counts: {dict(department_counts)}")
    
    # Build department summary
    department_summary = []
    for dept_name, total in department_counts.items():
        dept_assignments = [a for a in assignment_details if a["department"] == dept_name]
        dept_id = dept_assignments[0]["department_id"] if dept_assignments else 0
        
        department_summary.append({
            "department_id": dept_id,
            "department_name": dept_name,
            "total_assignments": total,
            "critical": sum(1 for a in dept_assignments if a["priority"] == "Critical"),
            "high": sum(1 for a in dept_assignments if a["priority"] == "High"),
            "medium": sum(1 for a in dept_assignments if a["priority"] == "Medium"),
            "low": sum(1 for a in dept_assignments if a["priority"] == "Low")
        })
    
    print(f"[BACKEND] Department summary built: {len(department_summary)} departments")
    
    response_data = {
        "document": {
            "id": document.id,
            "filename": document.original_filename,
            "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
            "processed_at": document.processed_at.isoformat() if document.processed_at else None
        },
        "counts": {
            "requirements_extracted": len(requirements),
            "assignments_generated": len(assignments),
            "departments_affected": len(department_counts),
            "critical_priority": priority_counts.get("Critical", 0),
            "high_priority": priority_counts.get("High", 0),
            "medium_priority": priority_counts.get("Medium", 0),
            "low_priority": priority_counts.get("Low", 0)
        },
        "assignments": assignment_details,
        "department_summary": department_summary,
        "priority_distribution": {
            "Critical": priority_counts.get("Critical", 0),
            "High": priority_counts.get("High", 0),
            "Medium": priority_counts.get("Medium", 0),
            "Low": priority_counts.get("Low", 0)
        }
    }
    
    print(f"[BACKEND] Response prepared with:")
    print(f"[BACKEND]   - requirements_extracted: {response_data['counts']['requirements_extracted']}")
    print(f"[BACKEND]   - assignments_generated: {response_data['counts']['assignments_generated']}")
    print(f"[BACKEND]   - departments_affected: {response_data['counts']['departments_affected']}")
    print(f"[BACKEND] ========== GET DOCUMENT ANALYSIS COMPLETE ==========")
    
    return response_data
