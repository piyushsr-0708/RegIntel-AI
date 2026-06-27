"""
SQLAlchemy ORM Models
Defines database schema for users, departments, requirements, assignments, etc.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class UserRole(str, enum.Enum):
    """User roles enum"""
    HEAD_OFFICE = "head_office"
    DEPARTMENT = "department"


class ComplianceStatus(str, enum.Enum):
    """Compliance status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    department = relationship("Department", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")


class Department(Base):
    """Department model"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # e.g., "COMP", "RISK"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="department")
    assignments = relationship("Assignment", back_populates="department")


class BatchStatus(str, enum.Enum):
    """Assignment Batch status enum"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class AssignmentBatch(Base):
    """Assignment Batch - Central workflow object for compliance campaigns"""
    __tablename__ = "assignment_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String(200), nullable=False)
    circular_name = Column(String(200), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(BatchStatus), default=BatchStatus.DRAFT, nullable=False)
    total_requirements = Column(Integer, default=0)
    total_maps = Column(Integer, default=0)
    completion_percentage = Column(Integer, default=0)
    verification_percentage = Column(Integer, default=0)
    
    # Relationships
    documents = relationship("Document", back_populates="batch")
    requirements = relationship("Requirement", back_populates="batch")
    assignments = relationship("Assignment", back_populates="batch")


class Document(Base):
    """Uploaded regulatory documents (RBI circulars)"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    document_type = Column(String(100), nullable=True)  # e.g., "RBI_Circular"
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    batch_id = Column(Integer, ForeignKey("assignment_batches.id"), nullable=True)
    
    # Relationships
    requirements = relationship("Requirement", back_populates="document")
    batch = relationship("AssignmentBatch", back_populates="documents")


class Requirement(Base):
    """Extracted requirements from documents"""
    __tablename__ = "requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(100), unique=True, index=True, nullable=False)  # e.g., "REQ_41YC0107_0022"
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    text = Column(Text, nullable=False)
    classification = Column(String(50), nullable=True)  # Mandatory, Recommended, Informational
    domain = Column(String(100), nullable=True)  # AML, KYC, Cybersecurity, etc.
    priority = Column(String(50), nullable=True)  # High, Medium, Low
    deadline = Column(String(200), nullable=True)  # Extracted deadline text
    source_reference = Column(String(200), nullable=True)  # Circular reference
    created_at = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(Integer, ForeignKey("assignment_batches.id"), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="requirements")
    assignments = relationship("Assignment", back_populates="requirement")
    batch = relationship("AssignmentBatch", back_populates="requirements")


class AssignmentLifecycle(str, enum.Enum):
    """Assignment lifecycle stages - Phase 2.2"""
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Assignment(Base):
    """Assignment of requirements to departments"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(ComplianceStatus), default=ComplianceStatus.PENDING)
    remarks = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    batch_id = Column(Integer, ForeignKey("assignment_batches.id"), nullable=True)
    
    # MVP Demo - Simple workflow
    is_published = Column(Boolean, default=False)  # Published to department
    
    # Relationships
    requirement = relationship("Requirement", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    status_history = relationship("ComplianceStatusHistory", back_populates="assignment")
    batch = relationship("AssignmentBatch", back_populates="assignments")


class ComplianceStatusHistory(Base):
    """Track status change history"""
    __tablename__ = "compliance_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    old_status = Column(SQLEnum(ComplianceStatus), nullable=True)
    new_status = Column(SQLEnum(ComplianceStatus), nullable=False)
    remarks = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="status_history")


class AuditLog(Base):
    """Audit log for tracking all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)  # e.g., "login", "upload", "assign"
    entity_type = Column(String(100), nullable=True)  # e.g., "document", "assignment"
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with additional details
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
