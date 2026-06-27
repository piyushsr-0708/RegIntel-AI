"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    HEAD_OFFICE = "head_office"
    DEPARTMENT = "department"


class ComplianceStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class BatchStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRole


class UserCreate(UserBase):
    password: str
    department_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    department_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    role: UserRole
    department_id: Optional[int]
    department_name: Optional[str]


# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    filename: str
    document_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    original_filename: str
    file_size: Optional[int]
    uploaded_by: int
    uploaded_at: datetime
    processed: bool
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Requirement Schemas
class RequirementBase(BaseModel):
    requirement_id: str
    text: str
    classification: Optional[str] = None
    domain: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[str] = None
    source_reference: Optional[str] = None


class RequirementCreate(RequirementBase):
    document_id: int


class RequirementResponse(RequirementBase):
    id: int
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Assignment Schemas
class AssignmentBase(BaseModel):
    requirement_id: int
    department_id: int


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentBulkCreate(BaseModel):
    requirement_ids: List[int]
    department_id: int


class AssignmentUpdate(BaseModel):
    status: ComplianceStatus
    remarks: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: int
    requirement_id: int
    department_id: int
    assigned_by: int
    assigned_at: datetime
    status: ComplianceStatus
    remarks: Optional[str]
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AssignmentDetail(AssignmentResponse):
    requirement: RequirementResponse
    department_name: str


# Dashboard Schemas
class DashboardSummary(BaseModel):
    total_documents: int
    total_requirements: int
    total_assignments: int
    pending_count: int
    in_progress_count: int
    completed_count: int
    completion_percentage: float


class DepartmentDashboard(BaseModel):
    department_id: int
    department_name: str
    total_assigned: int
    pending: int
    in_progress: int
    completed: int
    completion_percentage: float
    recent_assignments: List[AssignmentDetail]


# Audit Log Schemas
class AuditLogBase(BaseModel):
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    user_id: int
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Status History Schema
class StatusHistoryResponse(BaseModel):
    id: int
    assignment_id: int
    old_status: Optional[ComplianceStatus]
    new_status: ComplianceStatus
    remarks: Optional[str]
    changed_by: int
    changed_at: datetime
    
    class Config:
        from_attributes = True


# Assignment Batch Schemas
class AssignmentBatchBase(BaseModel):
    batch_name: str
    circular_name: str


class AssignmentBatchCreate(AssignmentBatchBase):
    pass


class AssignmentBatchResponse(AssignmentBatchBase):
    id: int
    uploaded_by: int
    uploaded_at: datetime
    status: BatchStatus
    total_requirements: int
    total_maps: int
    completion_percentage: int
    verification_percentage: int
    
    class Config:
        from_attributes = True


class AssignmentBatchSummary(AssignmentBatchResponse):
    """Extended summary with department distribution"""
    department_distribution: Optional[dict] = None
    priority_distribution: Optional[dict] = None
    uploader_name: Optional[str] = None


class AssignmentBatchStatusUpdate(BaseModel):
    status: BatchStatus
