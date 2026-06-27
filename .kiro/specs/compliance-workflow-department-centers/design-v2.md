# Technical Design Document - V2 (Revised)

## Document Information
- **Feature**: Compliance Workflow & Department Action Centers (Phase 2)
- **Spec ID**: compliance-workflow-department-centers
- **Version**: 2.0 (Revised for Enterprise Scalability)
- **Date**: June 26, 2026
- **Status**: Draft - Ready for Review

## Revision Summary

This design revision introduces **Assignment Batch (Compliance Campaign)** as the central workflow entity, improving scalability, realism, and enterprise workflow management.

### Key Improvements
1. **Assignment Batch Model**: Groups all work from a single RBI circular into one manageable campaign
2. **Batch-Centric Workflow**: Status tracking, reporting, and dashboards organized by batch
3. **Grouped Department Approval**: Review and approve entire department workloads at once
4. **Operational Department Dashboard**: Focus on today's tasks, critical items, and due dates
5. **Contextual Explainability Graph**: MAP-centered view showing circular → requirement → MAP → department relationships
6. **Extended MAP Lifecycle**: 6-stage lifecycle with completion evidence submission
7. **Dynamic Pipeline Metrics**: Real metrics from actual document processing (not placeholders)
8. **Enhanced Notifications**: Comprehensive workflow notifications for all key events
9. **AI Confidence Display**: Transparent AI reasoning with mandatory review flags
10. **Complete Audit Timeline**: Full batch lifecycle visibility

## Table of Contents
1. [Core Concepts](#1-core-concepts)
2. [Assignment Batch Architecture](#2-assignment-batch-architecture)
3. [Database Design](#3-database-design)
4. [Backend API Design](#4-backend-api-design)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Component Specifications](#6-component-specifications)
7. [Notification System](#7-notification-system)
8. [Reporting Architecture](#8-reporting-architecture)
9. [Security & Performance](#9-security--performance)
10. [Migration Strategy](#10-migration-strategy)

---

## 1. Core Concepts

### 1.1 Assignment Batch (Compliance Campaign)

**Definition**: An Assignment Batch represents all compliance work derived from a single RBI circular upload. It is the primary workflow object that groups requirements, MAPs, department assignments, and tracks overall campaign progress.

**Key Characteristics:**
- **One Batch per Circular**: Each uploaded RBI circular creates exactly one Assignment Batch
- **Workflow Container**: All requirements, MAPs, notifications, and reports belong to the batch
- **Lifecycle Management**: Batch progresses through stages: Draft → Pending Approval → Published → In Progress → Completed → Closed
- **Progress Tracking**: Aggregates completion and verification metrics across all departments
- **Central Dashboard Object**: Replaces individual MAP tracking as the primary workflow unit

### 1.2 Workflow Hierarchy

```
Assignment Batch (Compliance Campaign)
    ↓
├── Document (RBI Circular PDF)
    ↓
├── Requirements (Extracted compliance items)
    ↓
├── MAPs (Mitigation Action Plans)
    ↓
└── Department Assignments (Grouped by department)
        ↓
    └── Completion Evidence
```

### 1.3 Batch Lifecycle States

| State | Description | Trigger | Next State |
|-------|-------------|---------|------------|
| **Draft** | Circular uploaded, AI processing | Upload complete | Pending Approval |
| **Pending Approval** | Awaiting Head Office review | AI processing done | Published |
| **Published** | Approved, visible to departments | Head Office approves | In Progress |
| **In Progress** | Departments executing | First dept starts work | Completed |
| **Completed** | All MAPs completed | All MAPs verified | Closed |
| **Closed** | Archive, no further changes | Manual close | - |

### 1.4 Extended MAP Lifecycle

**6-Stage Lifecycle:**

```
Assigned → Accepted → In Progress → Completed → Verified → Closed
```

| Stage | Actor | Description | Evidence Required |
|-------|-------|-------------|-------------------|
| **Assigned** | System | MAP assigned to department | - |
| **Accepted** | Department | Department acknowledges | - |
| **In Progress** | Department | Work started | Progress notes |
| **Completed** | Department | Work finished | Completion evidence |
| **Verified** | Head Office | Validated by HO | Verification notes |
| **Closed** | System | Batch closure | - |

---

## 2. Assignment Batch Architecture

### 2.1 Batch-Centric Data Model

```
┌──────────────────────────────────────────────────────────┐
│              ASSIGNMENT BATCH (Campaign)                  │
├──────────────────────────────────────────────────────────┤
│ - id                                                      │
│ - batch_name (e.g., "RBI Cyber Security 2024-01")       │
│ - circular_name (e.g., "RBI/2024/01")                   │
│ - uploaded_by → users.id                                 │
│ - uploaded_at                                            │
│ - status (Draft/Pending/Published/InProgress/Completed)  │
│ - total_requirements                                     │
│ - total_maps                                             │
│ - completion_percentage (0-100)                          │
│ - verification_percentage (0-100)                        │
│ - ai_processing_started_at                               │
│ - ai_processing_completed_at                             │
│ - published_at                                           │
│ - closed_at                                              │
└──────────────────────────────────────────────────────────┘
                      │
                      │ 1:N
                      ▼
       ┌──────────────────────────────┐
       │      REQUIREMENTS            │
       │ + batch_id (FK)              │
       │ + document_id (FK)           │
       └──────────────────────────────┘
                      │
                      │ 1:N
                      ▼
       ┌──────────────────────────────┐
       │         MAPS                 │
       │ + batch_id (FK)              │
       │ + requirement_id (FK)        │
       │ + lifecycle_stage            │
       └──────────────────────────────┘
                      │
                      │ 1:N
                      ▼
       ┌──────────────────────────────┐
       │  DEPARTMENT_ASSIGNMENTS      │
       │ + batch_id (FK)              │
       │ + map_id (FK)                │
       │ + department_id (FK)         │
       │ + confidence_score           │
       │ + ai_reasoning               │
       └──────────────────────────────┘
                      │
                      │ 1:N
                      ▼
       ┌──────────────────────────────┐
       │  COMPLETION_EVIDENCE         │
       │ + assignment_id (FK)         │
       │ + evidence_type              │
       │ + completion_notes           │
       │ + evidence_document_path     │
       │ + implementation_ref         │
       └──────────────────────────────┘
```

### 2.2 Grouped Department Approval

Instead of approving individual MAPs, Head Office approves **department workload groups**:

```
Assignment Center View:
┌─────────────────────────────────────────────────────┐
│ Batch: RBI Cyber Security 2024-01                   │
│ Total: 45 MAPs across 5 departments                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📦 Compliance Department                         │ │
│ │ 18 MAPs | Avg Confidence: 89%                   │ │
│ │ [Approve All] [Reject All] [Review Details]    │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📦 Cyber Security Department                     │ │
│ │ 12 MAPs | Avg Confidence: 76% ⚠️ Low            │ │
│ │ [Approve All] [Reject All] [Review Details]    │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📦 IT Department                                 │ │
│ │ 8 MAPs | Avg Confidence: 92%                    │ │
│ │ [Approve All] [Reject All] [Review Details]    │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Approval Actions:**
- **Approve All**: Publishes all MAPs for that department
- **Reject All**: Marks all MAPs as rejected, removes from department view
- **Review Details**: Drill down to individual MAP review with reassignment option

### 2.3 Batch Status Calculation

```python
# Batch status logic

def calculate_batch_status(batch_id: int) -> str:
    """Calculate current batch status based on MAP states"""
    
    maps = get_maps_by_batch(batch_id)
    
    if all(map.lifecycle_stage == 'assigned' for map in maps):
        return 'pending_approval'
    
    if any(map.lifecycle_stage in ['accepted', 'in_progress'] for map in maps):
        return 'in_progress'
    
    if all(map.lifecycle_stage in ['verified', 'closed'] for map in maps):
        return 'completed'
    
    return 'published'

def calculate_completion_percentage(batch_id: int) -> float:
    """Calculate batch completion percentage"""
    maps = get_maps_by_batch(batch_id)
    if not maps:
        return 0.0
    
    completed = sum(1 for m in maps if m.lifecycle_stage in ['completed', 'verified', 'closed'])
    return (completed / len(maps)) * 100

def calculate_verification_percentage(batch_id: int) -> float:
    """Calculate batch verification percentage"""
    maps = get_maps_by_batch(batch_id)
    if not maps:
        return 0.0
    
    verified = sum(1 for m in maps if m.lifecycle_stage in ['verified', 'closed'])
    return (verified / len(maps)) * 100
```

---

## 3. Database Design

### 3.1 New Tables

#### 3.1.1 assignment_batches Table

```sql
CREATE TABLE assignment_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_name VARCHAR(200) NOT NULL,
    circular_name VARCHAR(200) NOT NULL,
    uploaded_by INTEGER NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    total_requirements INTEGER DEFAULT 0,
    total_maps INTEGER DEFAULT 0,
    completion_percentage FLOAT DEFAULT 0.0,
    verification_percentage FLOAT DEFAULT 0.0,
    ai_processing_started_at DATETIME,
    ai_processing_completed_at DATETIME,
    published_at DATETIME,
    closed_at DATETIME,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

CREATE INDEX idx_assignment_batches_status ON assignment_batches(status);
CREATE INDEX idx_assignment_batches_uploaded_by ON assignment_batches(uploaded_by);
```

**Columns:**
- `batch_name`: User-friendly name (e.g., "RBI Cyber Security Directive 2024-01")
- `circular_name`: Official circular identifier (e.g., "RBI/2024/01/CS")
- `status`: One of: draft, pending_approval, published, in_progress, completed, closed
- `total_requirements`: Count of extracted requirements
- `total_maps`: Count of generated MAPs
- `completion_percentage`: (Completed + Verified + Closed MAPs) / Total MAPs * 100
- `verification_percentage`: (Verified + Closed MAPs) / Total MAPs * 100

#### 3.1.2 completion_evidence Table

```sql
CREATE TABLE completion_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    completion_notes TEXT NOT NULL,
    evidence_document_path VARCHAR(500),
    evidence_screenshot_path VARCHAR(500),
    implementation_reference VARCHAR(200),
    implementation_date DATE,
    submitted_by INTEGER NOT NULL,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (submitted_by) REFERENCES users(id)
);

CREATE INDEX idx_completion_evidence_assignment ON completion_evidence(assignment_id);
```

**Purpose**: Stores evidence submitted by departments when marking MAPs as completed.


#### 3.1.3 notifications Table

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    user_id INTEGER,
    department_id INTEGER,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT FALSE,
    acknowledged_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES assignment_batches(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_dept ON notifications(department_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
```

**Notification Types:**
- `batch_published`: New batch published to department
- `map_assigned`: New MAP assigned
- `map_completed`: Department completed MAP
- `map_verified`: Head Office verified MAP
- `map_overdue`: MAP past deadline
- `verification_requested`: Department requests verification

#### 3.1.4 batch_audit_timeline Table

```sql
CREATE TABLE batch_audit_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT NOT NULL,
    actor_id INTEGER,
    actor_role VARCHAR(50),
    metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES assignment_batches(id),
    FOREIGN KEY (actor_id) REFERENCES users(id)
);

CREATE INDEX idx_batch_audit_batch ON batch_audit_timeline(batch_id);
```

**Event Types:**
- `circular_uploaded`, `ai_processing_started`, `ai_processing_completed`
- `batch_pending_approval`, `batch_published`, `batch_in_progress`
- `batch_completed`, `batch_closed`


### 3.2 Extended Existing Tables

#### 3.2.1 documents Table Extensions

```sql
ALTER TABLE documents ADD COLUMN batch_id INTEGER;
ALTER TABLE documents ADD COLUMN page_count INTEGER;
ALTER TABLE documents ADD COLUMN extracted_text_size INTEGER;
ALTER TABLE documents ADD COLUMN processing_duration_seconds INTEGER;

CREATE INDEX idx_documents_batch ON documents(batch_id);
```

**Purpose**: Link documents to batches and store dynamic pipeline metrics.

#### 3.2.2 requirements Table Extensions

```sql
ALTER TABLE requirements ADD COLUMN batch_id INTEGER NOT NULL;
ALTER TABLE requirements ADD COLUMN ai_confidence_score FLOAT;
ALTER TABLE requirements ADD COLUMN ai_reasoning TEXT;
ALTER TABLE requirements ADD COLUMN chunk_count INTEGER;

CREATE INDEX idx_requirements_batch ON requirements(batch_id);
```

**Purpose**: 
- Link requirements to batches
- Store AI confidence and reasoning for transparency
- Track chunk count for processing metrics

#### 3.2.3 assignments Table Extensions

```sql
-- Rename to 'maps' to reflect actual entity
-- Keep assignments table but add lifecycle tracking

ALTER TABLE assignments ADD COLUMN batch_id INTEGER NOT NULL;
ALTER TABLE assignments ADD COLUMN lifecycle_stage VARCHAR(50) DEFAULT 'assigned';
ALTER TABLE assignments ADD COLUMN ai_confidence_score FLOAT;
ALTER TABLE assignments ADD COLUMN ai_reasoning TEXT;
ALTER TABLE assignments ADD COLUMN map_title VARCHAR(300);
ALTER TABLE assignments ADD COLUMN map_description TEXT;
ALTER TABLE assignments ADD COLUMN accepted_at DATETIME;
ALTER TABLE assignments ADD COLUMN started_at DATETIME;
ALTER TABLE assignments ADD COLUMN completed_at DATETIME;
ALTER TABLE assignments ADD COLUMN verified_at DATETIME;
ALTER TABLE assignments ADD COLUMN verified_by INTEGER;
ALTER TABLE assignments ADD COLUMN closed_at DATETIME;
ALTER TABLE assignments ADD COLUMN deadline DATE;

CREATE INDEX idx_assignments_batch ON assignments(batch_id);
CREATE INDEX idx_assignments_lifecycle ON assignments(lifecycle_stage);
```

**Lifecycle Stages:**
- `assigned`: MAP assigned to department (initial)
- `accepted`: Department acknowledged assignment
- `in_progress`: Department actively working
- `completed`: Department finished, submitted evidence
- `verified`: Head Office validated completion
- `closed`: Batch closed, archival state


### 3.3 Database Migration Strategy

**Migration File**: `migrations/002_add_batch_architecture.sql`

```sql
-- Step 1: Create new tables
-- (assignment_batches, completion_evidence, notifications, batch_audit_timeline)

-- Step 2: Add columns to existing tables
-- (documents, requirements, assignments extensions)

-- Step 3: Create default batch for existing data
INSERT INTO assignment_batches (
    batch_name, 
    circular_name, 
    uploaded_by, 
    uploaded_at, 
    status
) VALUES (
    'Legacy Data Batch',
    'LEGACY/2024/00',
    1,  -- admin user
    CURRENT_TIMESTAMP,
    'published'
);

-- Step 4: Update existing records with legacy batch_id
UPDATE documents SET batch_id = (SELECT id FROM assignment_batches WHERE circular_name = 'LEGACY/2024/00');
UPDATE requirements SET batch_id = (SELECT id FROM assignment_batches WHERE circular_name = 'LEGACY/2024/00');
UPDATE assignments SET batch_id = (SELECT id FROM assignment_batches WHERE circular_name = 'LEGACY/2024/00');

-- Step 5: Update total counts
UPDATE assignment_batches 
SET 
    total_requirements = (SELECT COUNT(*) FROM requirements WHERE batch_id = assignment_batches.id),
    total_maps = (SELECT COUNT(*) FROM assignments WHERE batch_id = assignment_batches.id);
```

---

## 4. Backend API Design

### 4.1 Assignment Batch Endpoints

#### 4.1.1 Create Assignment Batch

**Endpoint**: `POST /api/batches`

**Request Body**:
```json
{
    "circular_file": "multipart/form-data",
    "batch_name": "RBI Cyber Security 2024-01",
    "circular_name": "RBI/2024/01/CS"
}
```

**Response**:
```json
{
    "id": 1,
    "batch_name": "RBI Cyber Security 2024-01",
    "circular_name": "RBI/2024/01/CS",
    "status": "draft",
    "uploaded_at": "2024-06-26T10:00:00Z"
}
```

**Process**:
1. Upload circular PDF
2. Create assignment_batches record
3. Create documents record with batch_id
4. Trigger AI processing pipeline
5. Return batch ID immediately


#### 4.1.2 Get Assignment Batches

**Endpoint**: `GET /api/batches`

**Query Parameters**:
- `status`: Filter by status (optional)
- `limit`: Max results (default: 50)
- `offset`: Pagination offset (default: 0)

**Response**:
```json
{
    "total": 12,
    "batches": [
        {
            "id": 1,
            "batch_name": "RBI Cyber Security 2024-01",
            "circular_name": "RBI/2024/01/CS",
            "status": "in_progress",
            "total_requirements": 45,
            "total_maps": 67,
            "completion_percentage": 32.5,
            "verification_percentage": 12.0,
            "uploaded_at": "2024-06-26T10:00:00Z",
            "published_at": "2024-06-26T14:30:00Z"
        }
    ]
}
```

#### 4.1.3 Get Batch Details

**Endpoint**: `GET /api/batches/{batch_id}`

**Response**:
```json
{
    "id": 1,
    "batch_name": "RBI Cyber Security 2024-01",
    "circular_name": "RBI/2024/01/CS",
    "status": "in_progress",
    "total_requirements": 45,
    "total_maps": 67,
    "completion_percentage": 32.5,
    "verification_percentage": 12.0,
    "uploaded_by": {
        "id": 1,
        "username": "admin",
        "full_name": "System Administrator"
    },
    "uploaded_at": "2024-06-26T10:00:00Z",
    "ai_processing_started_at": "2024-06-26T10:00:05Z",
    "ai_processing_completed_at": "2024-06-26T10:05:32Z",
    "published_at": "2024-06-26T14:30:00Z",
    "department_summary": [
        {
            "department_id": 1,
            "department_name": "Compliance",
            "total_maps": 18,
            "completed_maps": 6,
            "verified_maps": 2,
            "avg_confidence": 89.3
        }
    ],
    "audit_timeline": [
        {
            "event_type": "circular_uploaded",
            "event_description": "RBI Circular uploaded",
            "actor_name": "admin",
            "created_at": "2024-06-26T10:00:00Z"
        }
    ]
}
```


#### 4.1.4 Get Batch Assignments for Approval (Grouped)

**Endpoint**: `GET /api/batches/{batch_id}/assignments/grouped`

**Response**:
```json
{
    "batch_id": 1,
    "batch_name": "RBI Cyber Security 2024-01",
    "status": "pending_approval",
    "departments": [
        {
            "department_id": 1,
            "department_name": "Compliance",
            "total_maps": 18,
            "avg_confidence": 89.3,
            "confidence_warning": false,
            "maps": [
                {
                    "id": 101,
                    "map_title": "Update AML Risk Assessment Process",
                    "requirement_id": "REQ_001",
                    "requirement_text": "Banks shall establish...",
                    "ai_confidence_score": 92.5,
                    "ai_reasoning": "Strong domain match: requirement mentions 'AML risk assessment' and compliance department handles all AML processes.",
                    "priority": "high",
                    "suggested_deadline": "2024-07-26"
                }
            ]
        },
        {
            "department_id": 2,
            "department_name": "Cyber Security",
            "total_maps": 12,
            "avg_confidence": 76.2,
            "confidence_warning": true,
            "maps": [...]
        }
    ]
}
```

**Purpose**: Powers the Assignment Center grouped approval view.

#### 4.1.5 Approve Department Assignments (Bulk)

**Endpoint**: `POST /api/batches/{batch_id}/assignments/approve`

**Request Body**:
```json
{
    "department_id": 1,
    "action": "approve_all",  // or "reject_all"
    "map_ids": [101, 102, 103]  // optional, for selective approval
}
```

**Response**:
```json
{
    "status": "success",
    "approved_count": 18,
    "rejected_count": 0,
    "batch_status": "published",
    "notifications_sent": 3
}
```

**Process**:
1. Update lifecycle_stage to 'assigned' for approved MAPs
2. Update batch status if all departments approved
3. Create notifications for target department
4. Record event in batch_audit_timeline


#### 4.1.6 Reassign MAPs

**Endpoint**: `POST /api/batches/{batch_id}/assignments/reassign`

**Request Body**:
```json
{
    "map_ids": [101, 102],
    "from_department_id": 1,
    "to_department_id": 3,
    "reason": "Better fit for IT department capabilities"
}
```

**Response**:
```json
{
    "status": "success",
    "reassigned_count": 2,
    "notifications_sent": 2
}
```

### 4.2 MAP Lifecycle Endpoints

#### 4.2.1 Update MAP Status

**Endpoint**: `PATCH /api/maps/{map_id}/status`

**Request Body**:
```json
{
    "lifecycle_stage": "accepted",  // or "in_progress", "completed"
    "notes": "Department has acknowledged and assigned to team lead"
}
```

**Response**:
```json
{
    "id": 101,
    "lifecycle_stage": "accepted",
    "accepted_at": "2024-06-26T15:00:00Z",
    "updated_by": "user@dept.com"
}
```

**Validation Rules**:
- Department users can transition: assigned → accepted → in_progress → completed
- Head Office users can transition: completed → verified → closed
- Cannot skip stages
- Completed stage requires evidence submission

#### 4.2.2 Submit Completion Evidence

**Endpoint**: `POST /api/maps/{map_id}/evidence`

**Request Body** (multipart/form-data):
```json
{
    "completion_notes": "Implemented new AML screening process...",
    "implementation_reference": "PROJ-2024-001",
    "implementation_date": "2024-06-25",
    "evidence_document": "file upload",
    "evidence_screenshot": "file upload"
}
```

**Response**:
```json
{
    "id": 1,
    "assignment_id": 101,
    "completion_notes": "Implemented new AML screening process...",
    "evidence_document_path": "/uploads/evidence/doc_123.pdf",
    "submitted_at": "2024-06-26T16:00:00Z"
}
```


#### 4.2.3 Verify MAP Completion

**Endpoint**: `POST /api/maps/{map_id}/verify`

**Request Body**:
```json
{
    "verification_notes": "Reviewed implementation, meets compliance requirements",
    "approved": true
}
```

**Response**:
```json
{
    "id": 101,
    "lifecycle_stage": "verified",
    "verified_at": "2024-06-27T10:00:00Z",
    "verified_by": 1
}
```

**Access**: HEAD_OFFICE role only

### 4.3 Department Dashboard Endpoints

#### 4.3.1 Get Department Dashboard Data

**Endpoint**: `GET /api/departments/{dept_id}/dashboard`

**Response**:
```json
{
    "department_id": 1,
    "department_name": "Compliance",
    "overview": {
        "total_maps": 42,
        "assigned": 8,
        "accepted": 5,
        "in_progress": 15,
        "completed": 10,
        "verified": 4,
        "overdue": 3,
        "completion_percentage": 33.3
    },
    "todays_tasks": [
        {
            "map_id": 105,
            "map_title": "Update Risk Assessment",
            "priority": "critical",
            "deadline": "2024-06-27",
            "lifecycle_stage": "in_progress"
        }
    ],
    "critical_tasks": [
        {
            "map_id": 107,
            "map_title": "Implement Transaction Monitoring",
            "priority": "critical",
            "deadline": "2024-06-28",
            "lifecycle_stage": "assigned"
        }
    ],
    "due_today": [],
    "overdue_tasks": [
        {
            "map_id": 108,
            "map_title": "Customer Due Diligence Update",
            "priority": "high",
            "deadline": "2024-06-25",
            "days_overdue": 2,
            "lifecycle_stage": "in_progress"
        }
    ],
    "pending_verification": [
        {
            "map_id": 110,
            "map_title": "Enhanced KYC Process",
            "completed_at": "2024-06-24T14:00:00Z",
            "days_waiting": 3
        }
    ],
    "completed_today": []
}
```


#### 4.3.2 Get Department MAPs

**Endpoint**: `GET /api/departments/{dept_id}/maps`

**Query Parameters**:
- `lifecycle_stage`: Filter by stage (optional)
- `priority`: Filter by priority (optional)
- `batch_id`: Filter by batch (optional)
- `search`: Text search (optional)
- `sort`: Sort field (deadline, priority, created_at)
- `limit`, `offset`: Pagination

**Response**:
```json
{
    "total": 42,
    "maps": [
        {
            "id": 101,
            "map_title": "Update AML Risk Assessment Process",
            "map_description": "Enhance risk assessment methodology...",
            "requirement_id": "REQ_001",
            "requirement_text": "Banks shall establish...",
            "batch_id": 1,
            "batch_name": "RBI Cyber Security 2024-01",
            "circular_name": "RBI/2024/01/CS",
            "lifecycle_stage": "in_progress",
            "priority": "high",
            "deadline": "2024-07-26",
            "assigned_at": "2024-06-26T14:30:00Z",
            "ai_confidence_score": 92.5,
            "ai_reasoning": "Strong domain match...",
            "has_evidence": false
        }
    ]
}
```

### 4.4 Notification Endpoints

#### 4.4.1 Get Notifications

**Endpoint**: `GET /api/notifications`

**Query Parameters**:
- `is_read`: Filter by read status (optional)
- `limit`: Max results (default: 20)

**Response**:
```json
{
    "unread_count": 5,
    "notifications": [
        {
            "id": 1,
            "notification_type": "batch_published",
            "title": "New Compliance Batch Assigned",
            "message": "You have been assigned 18 new MAPs from RBI Cyber Security 2024-01",
            "priority": "high",
            "batch_id": 1,
            "is_read": false,
            "created_at": "2024-06-26T14:30:00Z"
        }
    ]
}
```

#### 4.4.2 Mark Notification as Read

**Endpoint**: `PATCH /api/notifications/{notification_id}/read`

**Response**:
```json
{
    "id": 1,
    "is_read": true,
    "acknowledged_at": "2024-06-26T15:00:00Z"
}
```


### 4.5 Pipeline Metrics Endpoints

#### 4.5.1 Get Dynamic Pipeline Metrics

**Endpoint**: `GET /api/batches/{batch_id}/metrics`

**Response**:
```json
{
    "batch_id": 1,
    "batch_name": "RBI Cyber Security 2024-01",
    "processing_metrics": {
        "document": {
            "page_count": 45,
            "file_size_mb": 2.3,
            "extracted_text_size_kb": 156
        },
        "extraction": {
            "total_chunks": 189,
            "total_requirements": 67,
            "processing_duration_seconds": 327
        },
        "classification": {
            "mandatory": 42,
            "recommended": 18,
            "informational": 7
        },
        "assignment": {
            "total_maps": 67,
            "departments_involved": 5,
            "avg_confidence_score": 84.6,
            "high_confidence_count": 52,
            "low_confidence_count": 8
        },
        "graph": {
            "total_nodes": 142,
            "total_edges": 267,
            "circular_nodes": 1,
            "requirement_nodes": 67,
            "map_nodes": 67,
            "department_nodes": 5
        }
    }
}
```

**Purpose**: Replace static placeholder metrics with real values derived from document processing.

---

## 5. Frontend Architecture

### 5.1 New Pages and Routes

#### 5.1.1 Route Structure

```
HEAD_OFFICE Routes:
├── /dashboard (Executive Dashboard - existing)
├── /batches (Batch List View - NEW)
├── /batches/:batchId (Batch Detail View - NEW)
├── /batches/:batchId/approve (Assignment Center - NEW)
├── /pipeline (Regulatory Intelligence Pipeline - existing)
├── /knowledge-graph (Global Knowledge Graph - existing)
└── /profile (User Profile)

DEPARTMENT Routes:
├── / (Department Dashboard - NEW)
├── /my-maps (Assigned MAPs List - NEW)
├── /my-maps/:mapId (MAP Detail View - NEW)
├── /my-graph (Department Knowledge Graph - NEW)
└── /profile (User Profile)
```


### 5.2 Component Hierarchy

```
App
├── AuthProvider (context)
├── NotificationProvider (context - NEW)
│   ├── usePolling hook (5-second interval)
│   └── NotificationBadge component
├── Router
│   ├── ProtectedRoute (role-based)
│   │   ├── HEAD_OFFICE Layout
│   │   │   ├── Topbar (with NotificationBadge)
│   │   │   ├── Sidebar
│   │   │   └── Content
│   │   │       ├── ExecutiveDashboard (existing)
│   │   │       ├── BatchListPage (NEW)
│   │   │       ├── BatchDetailPage (NEW)
│   │   │       ├── AssignmentCenterPage (NEW)
│   │   │       ├── PipelinePage (existing, enhanced metrics)
│   │   │       └── GlobalKnowledgeGraph (existing)
│   │   │
│   │   └── DEPARTMENT Layout
│   │       ├── Topbar (with NotificationBadge)
│   │       ├── Sidebar (limited menu)
│   │       └── Content
│   │           ├── DepartmentDashboard (NEW)
│   │           ├── MyMapsPage (NEW)
│   │           ├── MapDetailPage (NEW)
│   │           └── DepartmentKnowledgeGraph (NEW)
│   │
│   └── Login (public)
```

### 5.3 State Management

#### 5.3.1 NotificationContext

```javascript
// NotificationContext.jsx
import { createContext, useState, useEffect } from 'react';

export const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);

    // Polling mechanism
    useEffect(() => {
        const fetchNotifications = async () => {
            const response = await api.get('/api/notifications?is_read=false');
            setNotifications(response.data.notifications);
            setUnreadCount(response.data.unread_count);
        };

        fetchNotifications(); // Initial fetch
        const interval = setInterval(fetchNotifications, 5000); // Poll every 5 seconds

        return () => clearInterval(interval);
    }, []);

    const markAsRead = async (notificationId) => {
        await api.patch(`/api/notifications/${notificationId}/read`);
        setNotifications(prev => 
            prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
    };

    return (
        <NotificationContext.Provider value={{ notifications, unreadCount, markAsRead }}>
            {children}
        </NotificationContext.Provider>
    );
};
```


#### 5.3.2 Dashboard Polling Hook

```javascript
// useDashboardPolling.js
import { useState, useEffect } from 'react';
import api from '../services/api';

export const useDashboardPolling = (endpoint, interval = 5000) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(endpoint);
                setData(response.data);
                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchData(); // Initial fetch
        const intervalId = setInterval(fetchData, interval);

        return () => clearInterval(intervalId);
    }, [endpoint, interval]);

    return { data, loading, error };
};
```

---

## 6. Component Specifications

### 6.1 Assignment Center (Grouped Approval View)

**Component**: `AssignmentCenterPage.jsx`

**Purpose**: Allow Head Office to review and approve AI-suggested department assignments in bulk.

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ Assignment Center - Batch: RBI Cyber Security 2024-01     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Batch Status: Pending Approval                            │
│ Total: 67 MAPs across 5 departments                       │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ 📦 Compliance Department                                │ │
│ │ 18 MAPs | Avg Confidence: 89.3% ✓                      │ │
│ │                                                         │ │
│ │ [Approve All 18] [Reject All] [Review Details ▼]      │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ 📦 Cyber Security Department                            │ │
│ │ 12 MAPs | Avg Confidence: 76.2% ⚠️ Review Recommended │ │
│ │                                                         │ │
│ │ [Approve All 12] [Reject All] [Review Details ▼]      │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ 📦 IT Department                                        │ │
│ │ 8 MAPs | Avg Confidence: 92.1% ✓                       │ │
│ │                                                         │ │
│ │ [Approve All 8] [Reject All] [Review Details ▼]       │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```


**Review Details Modal**:
```
┌────────────────────────────────────────────────────────────┐
│ Compliance Department - 18 MAPs                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ MAP #1: Update AML Risk Assessment Process                │
│ ├─ Requirement: Banks shall establish...                  │
│ ├─ AI Confidence: 92.5% ✓                                 │
│ ├─ Reasoning: Strong domain match: requirement mentions   │
│ │   'AML risk assessment' and compliance dept handles...  │
│ ├─ Priority: High                                         │
│ └─ Actions: [✓ Approve] [✗ Reject] [↻ Reassign to...]   │
│                                                            │
│ MAP #2: Implement Transaction Monitoring                  │
│ ├─ Requirement: Enhanced transaction monitoring...        │
│ ├─ AI Confidence: 87.3% ✓                                 │
│ ├─ Reasoning: Compliance department owns AML monitoring   │
│ ├─ Priority: Critical                                     │
│ └─ Actions: [✓ Approve] [✗ Reject] [↻ Reassign to...]   │
│                                                            │
│ [Close] [Approve Selected] [Approve All]                  │
└────────────────────────────────────────────────────────────┘
```

**Props**:
```typescript
interface AssignmentCenterPageProps {
    batchId: number;
}
```

**State**:
```typescript
{
    batch: AssignmentBatch | null;
    departmentGroups: DepartmentGroup[];
    loading: boolean;
    selectedDepartment: number | null;
    expandedDepartments: number[];
}
```

**API Calls**:
- `GET /api/batches/{batchId}/assignments/grouped` (on mount)
- `POST /api/batches/{batchId}/assignments/approve` (on approve)
- `POST /api/batches/{batchId}/assignments/reassign` (on reassign)

### 6.2 Department Dashboard (Operational Focus)

**Component**: `DepartmentDashboard.jsx`

**Purpose**: Provide department users with an operational view of their daily work.

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ Compliance Department Dashboard                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌─────────────┬─────────────┬─────────────┬──────────────┐│
│ │ Total MAPs  │ In Progress │ Completed   │ Overdue      ││
│ │     42      │      15     │     14      │      3       ││
│ └─────────────┴─────────────┴─────────────┴──────────────┘│
│                                                            │
│ ┌──────────────────────── TODAY'S TASKS ─────────────────┐│
│ │ 🔴 Update Risk Assessment (Critical, Due Today)        ││
│ │ 🟡 Customer Due Diligence Review (High, Due Tomorrow)  ││
│ │ 🟢 Policy Documentation Update (Medium, Due in 5 days) ││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ ┌────────────────────── CRITICAL TASKS ──────────────────┐│
│ │ 🔴 Implement Transaction Monitoring (Due in 2 days)    ││
│ │ 🔴 KYC Process Enhancement (Due in 3 days)             ││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ ┌───────────────────────── OVERDUE ──────────────────────┐│
│ │ ⚠️ Customer DD Update (2 days overdue)                 ││
│ │ ⚠️ Policy Review (1 day overdue)                       ││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ ┌──────────────── PENDING VERIFICATION ──────────────────┐│
│ │ Enhanced KYC Process (Waiting 3 days)                  ││
│ │ AML Screening Update (Waiting 1 day)                   ││
│ └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```


**Props**: None (uses AuthContext for department ID)

**State**:
```typescript
{
    dashboardData: DepartmentDashboardData | null;
    loading: boolean;
    lastUpdated: Date;
}
```

**API Calls**:
- `GET /api/departments/{deptId}/dashboard` (polled every 5 seconds)

**Features**:
- Auto-refresh with polling
- Click on task → navigate to MAP detail
- Color-coded priority indicators
- Days overdue/waiting calculations
- Real-time completion percentage

### 6.3 Contextual Explainability Graph

**Component**: `ContextualGraph.jsx`

**Purpose**: Display MAP-centered graph showing relationships: Circular → Requirement → MAP → Department.

**View Mode**: Focused on selected MAP

**Graph Structure**:
```
        [RBI Circular]
              │
              ▼
       [Requirement #42]
              │
              ▼
    ┌─────[MAP #101]─────┐
    │  (SELECTED/CENTER)  │
    └─────────────────────┘
              │
              ▼
    [Compliance Department]
              │
         ┌────┴────┐
         ▼         ▼
  [Related Req #43] [Related Req #44]
```

**Props**:
```typescript
interface ContextualGraphProps {
    mapId: number;
    departmentId?: number; // For department-scoped view
}
```

**Graph Data API**:
```
GET /api/maps/{mapId}/context-graph
```

**Response**:
```json
{
    "center_map": {
        "id": 101,
        "title": "Update AML Risk Assessment",
        "lifecycle_stage": "in_progress"
    },
    "circular": {
        "id": 1,
        "name": "RBI/2024/01/CS",
        "batch_name": "RBI Cyber Security 2024-01"
    },
    "requirement": {
        "id": 42,
        "requirement_id": "REQ_001",
        "text": "Banks shall establish..."
    },
    "department": {
        "id": 1,
        "name": "Compliance"
    },
    "related_requirements": [
        {
            "id": 43,
            "requirement_id": "REQ_002",
            "text": "Related requirement..."
        }
    ]
}
```


### 6.4 MAP Detail Page

**Component**: `MapDetailPage.jsx`

**Purpose**: Display complete MAP information including evidence submission.

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ MAP #101: Update AML Risk Assessment Process               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Status: In Progress    Priority: High    Due: 2024-07-26  │
│                                                            │
│ ┌──────────────────── REQUIREMENT ──────────────────────┐ │
│ │ REQ_001: Banks shall establish comprehensive AML...    │ │
│ │ Source: RBI/2024/01/CS - RBI Cyber Security 2024-01   │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌────────────────── MAP DESCRIPTION ─────────────────────┐ │
│ │ Enhance the existing AML risk assessment process to... │ │
│ │ implement new screening criteria and monitoring...     │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌───────────────── AI ASSIGNMENT INFO ───────────────────┐ │
│ │ Confidence: 92.5% ✓                                    │ │
│ │ Reasoning: Strong domain match - requirement mentions  │ │
│ │ 'AML risk assessment' and Compliance dept handles all  │ │
│ │ AML-related processes. Historical assignment pattern   │ │
│ │ shows 95% accuracy for similar requirements.           │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌──────────────── LIFECYCLE TIMELINE ────────────────────┐ │
│ │ ✓ Assigned      2024-06-26 14:30                       │ │
│ │ ✓ Accepted      2024-06-26 15:00                       │ │
│ │ ✓ In Progress   2024-06-26 16:00                       │ │
│ │ ○ Completed     (pending)                              │ │
│ │ ○ Verified      (pending)                              │ │
│ │ ○ Closed        (pending)                              │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌───────────── COMPLETION EVIDENCE ──────────────────────┐ │
│ │ (visible when lifecycle_stage = 'in_progress')         │ │
│ │                                                         │ │
│ │ Completion Notes: [text area]                          │ │
│ │ Implementation Reference: [text input]                 │ │
│ │ Implementation Date: [date picker]                     │ │
│ │ Evidence Document: [file upload]                       │ │
│ │ Screenshot: [file upload]                              │ │
│ │                                                         │ │
│ │ [Submit Evidence & Mark Completed]                     │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ [View Contextual Graph] [Back to Dashboard]               │
└────────────────────────────────────────────────────────────┘
```

**State**:
```typescript
{
    map: MAPDetails | null;
    evidenceForm: {
        completionNotes: string;
        implementationReference: string;
        implementationDate: string;
        evidenceDocument: File | null;
        evidenceScreenshot: File | null;
    };
    submitting: boolean;
}
```

**API Calls**:
- `GET /api/maps/{mapId}` (on mount, polled every 10 seconds)
- `POST /api/maps/{mapId}/evidence` (on submit)
- `PATCH /api/maps/{mapId}/status` (on status transition)


### 6.5 Batch List Page

**Component**: `BatchListPage.jsx`

**Purpose**: Display all assignment batches for Head Office overview.

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ Assignment Batches                       [+ Upload New]    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Filter: [All ▼] [In Progress ▼] [Completed ▼]            │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ RBI Cyber Security 2024-01                             │ │
│ │ Status: In Progress | 67 MAPs | 32% Complete          │ │
│ │ Uploaded: 2024-06-26 by admin                         │ │
│ │ Published: 2024-06-26 14:30                           │ │
│ │ [View Details] [View Reports]                         │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ RBI AML Guidelines 2024-02                             │ │
│ │ Status: Pending Approval | 89 MAPs                    │ │
│ │ Uploaded: 2024-06-25 by admin                         │ │
│ │ AI Processing: Complete                                │ │
│ │ [Review Assignments] [View Details]                   │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ RBI KYC Norms Update 2024-03                           │ │
│ │ Status: Draft | Processing...                         │ │
│ │ Uploaded: 2024-06-27 by admin                         │ │
│ │ AI Processing: In Progress (45%)                      │ │
│ │ [View Processing Status]                              │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 6.6 Enhanced Pipeline Page

**Component**: `PipelinePage.jsx` (modified)

**Enhancement**: Replace static placeholder metrics with dynamic batch metrics.

**Current Metrics** (static placeholders):
```
Documents Processed: 14
Requirements Extracted: 127
MAPs Generated: 180
```

**New Metrics** (dynamic from batch):
```javascript
// Fetch from GET /api/batches/{batchId}/metrics

const metrics = {
    document: {
        page_count: 45,
        file_size_mb: 2.3,
        extracted_text_size_kb: 156
    },
    extraction: {
        total_chunks: 189,
        total_requirements: 67,
        processing_duration_seconds: 327
    },
    classification: {
        mandatory: 42,
        recommended: 18,
        informational: 7
    },
    assignment: {
        total_maps: 67,
        departments_involved: 5,
        avg_confidence_score: 84.6
    }
};
```


**Updated Pipeline Display**:
```
┌────────────────────────────────────────────────────────────┐
│ Select Batch: [RBI Cyber Security 2024-01 ▼]              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Document Processing                                        │
│ ├─ Pages: 45                                              │
│ ├─ File Size: 2.3 MB                                      │
│ └─ Extracted Text: 156 KB                                 │
│                                                            │
│ Requirement Extraction                                     │
│ ├─ Total Chunks: 189                                      │
│ ├─ Requirements Extracted: 67                             │
│ ├─ Processing Time: 5m 27s                                │
│ └─ Classification:                                        │
│     • Mandatory: 42                                       │
│     • Recommended: 18                                     │
│     • Informational: 7                                    │
│                                                            │
│ Department Assignment                                      │
│ ├─ Total MAPs: 67                                         │
│ ├─ Departments: 5                                         │
│ ├─ Avg Confidence: 84.6%                                  │
│ ├─ High Confidence (>80%): 52                             │
│ └─ Review Recommended (<70%): 8                           │
│                                                            │
│ Knowledge Graph                                            │
│ ├─ Total Nodes: 142                                       │
│ ├─ Total Edges: 267                                       │
│ └─ Department Nodes: 5                                    │
└────────────────────────────────────────────────────────────┘
```

---

## 7. Notification System

### 7.1 Notification Types and Triggers

| Notification Type | Trigger | Recipients | Priority |
|-------------------|---------|------------|----------|
| `batch_published` | Head Office publishes batch | Department users | High |
| `map_assigned` | Individual MAP assigned | Department users | Normal |
| `map_completed` | Department marks MAP complete | Head Office users | Normal |
| `map_verified` | Head Office verifies MAP | Department users | Normal |
| `map_overdue` | Deadline passes | Department + Head Office | High |
| `verification_requested` | Department requests verification | Head Office users | Normal |
| `batch_completed` | All MAPs verified | Head Office users | High |
| `assignment_approved` | Head Office approves assignment | Department users | High |

### 7.2 Notification Delivery Mechanism

**Implementation**: Polling-based (no WebSockets)

**Polling Strategy**:
```javascript
// NotificationProvider.jsx
useEffect(() => {
    const fetchNotifications = async () => {
        try {
            const response = await api.get('/api/notifications?is_read=false');
            setNotifications(response.data.notifications);
            setUnreadCount(response.data.unread_count);
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
        }
    };

    fetchNotifications(); // Initial fetch
    const interval = setInterval(fetchNotifications, 5000); // 5-second poll

    // Stop polling when tab not visible
    const handleVisibilityChange = () => {
        if (document.hidden) {
            clearInterval(interval);
        } else {
            fetchNotifications();
            setInterval(fetchNotifications, 5000);
        }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
        clearInterval(interval);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
}, []);
```


### 7.3 Notification UI Components

#### 7.3.1 NotificationBadge Component

```jsx
// NotificationBadge.jsx
import { useContext } from 'react';
import { NotificationContext } from '../context/NotificationContext';

export const NotificationBadge = () => {
    const { unreadCount } = useContext(NotificationContext);

    if (unreadCount === 0) return null;

    return (
        <span className="notification-badge">
            {unreadCount > 99 ? '99+' : unreadCount}
        </span>
    );
};
```

#### 7.3.2 NotificationDropdown Component

```jsx
// NotificationDropdown.jsx
import { useContext } from 'react';
import { NotificationContext } from '../context/NotificationContext';

export const NotificationDropdown = () => {
    const { notifications, markAsRead } = useContext(NotificationContext);

    return (
        <div className="notification-dropdown">
            {notifications.length === 0 && (
                <div className="no-notifications">No new notifications</div>
            )}
            {notifications.map(notification => (
                <div 
                    key={notification.id}
                    className={`notification-item ${notification.priority}`}
                    onClick={() => markAsRead(notification.id)}
                >
                    <div className="notification-title">{notification.title}</div>
                    <div className="notification-message">{notification.message}</div>
                    <div className="notification-time">
                        {formatTimeAgo(notification.created_at)}
                    </div>
                </div>
            ))}
        </div>
    );
};
```

### 7.4 Backend Notification Creation Logic

```python
# backend/services/notification_service.py

def create_notification(
    batch_id: int,
    notification_type: str,
    title: str,
    message: str,
    department_id: int = None,
    user_id: int = None,
    priority: str = "normal"
):
    """Create a notification for users or departments"""
    notification = Notification(
        batch_id=batch_id,
        notification_type=notification_type,
        title=title,
        message=message,
        department_id=department_id,
        user_id=user_id,
        priority=priority,
        is_read=False
    )
    db.add(notification)
    db.commit()
    return notification

def notify_batch_published(batch_id: int, department_ids: list[int]):
    """Notify departments when batch is published"""
    batch = db.query(AssignmentBatch).filter_by(id=batch_id).first()
    
    for dept_id in department_ids:
        dept = db.query(Department).filter_by(id=dept_id).first()
        map_count = db.query(Assignment).filter_by(
            batch_id=batch_id, 
            department_id=dept_id
        ).count()
        
        create_notification(
            batch_id=batch_id,
            notification_type="batch_published",
            title="New Compliance Batch Assigned",
            message=f"You have been assigned {map_count} MAPs from {batch.batch_name}",
            department_id=dept_id,
            priority="high"
        )
```


---

## 8. Reporting Architecture

### 8.1 Report Types

#### 8.1.1 Executive Compliance Report

**Purpose**: Institution-wide compliance overview for executive management.

**Content**:
- All active batches summary
- Overall completion percentage
- Department performance comparison
- Critical items status
- Overdue MAPs
- Risk score trends
- Compliance timeline

**Endpoint**: `GET /api/reports/executive?format=pdf`

**Generation Logic**:
```python
def generate_executive_report():
    data = {
        "batches": get_all_batches_summary(),
        "overall_metrics": {
            "total_maps": get_total_maps(),
            "completed_percentage": calculate_overall_completion(),
            "overdue_count": get_overdue_count(),
            "critical_count": get_critical_pending_count()
        },
        "department_performance": [
            {
                "department": dept.name,
                "assigned": get_dept_assigned(dept.id),
                "completed": get_dept_completed(dept.id),
                "completion_rate": calculate_rate(dept.id)
            }
            for dept in get_all_departments()
        ]
    }
    return render_pdf_template("executive_report.html", data)
```

#### 8.1.2 Assignment Batch Report

**Purpose**: Complete report for a single compliance campaign.

**Content**:
- Batch metadata (name, circular, dates)
- Processing metrics (pages, chunks, requirements)
- Department assignments breakdown
- AI confidence analysis
- Completion status by department
- Audit timeline
- Outstanding items

**Endpoint**: `GET /api/reports/batch/{batch_id}?format=pdf`

**Template Structure**:
```
┌────────────────────────────────────────────────────────────┐
│        Assignment Batch Report                             │
│        RBI Cyber Security 2024-01                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Batch Information                                          │
│ ├─ Circular: RBI/2024/01/CS                               │
│ ├─ Uploaded: 2024-06-26 by admin                          │
│ ├─ Published: 2024-06-26 14:30                            │
│ ├─ Status: In Progress                                    │
│ └─ Completion: 32.5%                                      │
│                                                            │
│ Processing Metrics                                         │
│ ├─ Pages: 45                                              │
│ ├─ Requirements: 67                                       │
│ ├─ MAPs: 67                                               │
│ └─ Processing Time: 5m 27s                                │
│                                                            │
│ Department Assignments                                     │
│ ├─ Compliance: 18 MAPs (6 completed, 2 verified)         │
│ ├─ Cyber Security: 12 MAPs (3 completed, 1 verified)     │
│ ├─ IT: 8 MAPs (2 completed, 0 verified)                  │
│ └─ ...                                                    │
│                                                            │
│ Outstanding Items                                          │
│ ├─ Overdue: 3 MAPs                                        │
│ ├─ Critical Pending: 5 MAPs                               │
│ └─ Awaiting Verification: 8 MAPs                          │
└────────────────────────────────────────────────────────────┘
```


#### 8.1.3 Department Report

**Purpose**: Department-specific compliance report.

**Content**:
- Department name and metadata
- All assigned MAPs with status
- Completion metrics
- Overdue items
- Pending verification
- Evidence submission history
- Performance trends

**Endpoint**: `GET /api/reports/department/{dept_id}?format=pdf&batch_id={batch_id}`

**Access Control**: 
- Department users can only generate their own department report
- Head Office users can generate any department report

#### 8.1.4 MAP Report

**Purpose**: Detailed report for a single MAP.

**Content**:
- MAP title and description
- Source requirement and circular
- Department assignment
- AI confidence and reasoning
- Complete lifecycle timeline
- Completion evidence (notes, documents, dates)
- Verification status and notes
- Full audit trail

**Endpoint**: `GET /api/reports/map/{map_id}?format=pdf`

### 8.2 PDF Generation Implementation

**Library**: ReportLab (Python) or WeasyPrint

**Base Template Structure**:
```python
# backend/services/report_service.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(template_name: str, data: dict) -> bytes:
    """Generate PDF from template and data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Build content based on template
    story = []
    
    if template_name == "executive_report":
        story = build_executive_report_content(data)
    elif template_name == "batch_report":
        story = build_batch_report_content(data)
    elif template_name == "department_report":
        story = build_department_report_content(data)
    elif template_name == "map_report":
        story = build_map_report_content(data)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
```

### 8.3 Report Export UI

**Button Placement**:
- Executive Dashboard: "Export Executive Report"
- Batch Detail Page: "Export Batch Report"
- Department Dashboard: "Export Department Report"
- MAP Detail Page: "Export MAP Report"

**Export Handler**:
```javascript
const handleExportReport = async (reportType, id) => {
    try {
        const response = await api.get(
            `/api/reports/${reportType}/${id}?format=pdf`,
            { responseType: 'blob' }
        );
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${reportType}_report_${id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (error) {
        console.error('Report generation failed:', error);
        alert('Failed to generate report');
    }
};
```


---

## 9. Security & Performance

### 9.1 Role-Based Access Control

#### 9.1.1 Access Control Matrix

| Endpoint | HEAD_OFFICE | DEPARTMENT | Notes |
|----------|-------------|------------|-------|
| `POST /api/batches` | ✓ | ✗ | Upload circular |
| `GET /api/batches` | ✓ | ✗ | List all batches |
| `GET /api/batches/{id}` | ✓ | ✗ | Batch details |
| `GET /api/batches/{id}/assignments/grouped` | ✓ | ✗ | Assignment approval |
| `POST /api/batches/{id}/assignments/approve` | ✓ | ✗ | Approve assignments |
| `POST /api/batches/{id}/assignments/reassign` | ✓ | ✗ | Reassign MAPs |
| `GET /api/departments/{id}/dashboard` | ✓ | ✓ (own) | Dashboard data |
| `GET /api/departments/{id}/maps` | ✓ | ✓ (own) | Department MAPs |
| `PATCH /api/maps/{id}/status` | ✓ | ✓ (own) | Update status |
| `POST /api/maps/{id}/evidence` | ✗ | ✓ (own) | Submit evidence |
| `POST /api/maps/{id}/verify` | ✓ | ✗ | Verify completion |
| `GET /api/notifications` | ✓ | ✓ | User notifications |
| `GET /api/reports/executive` | ✓ | ✗ | Executive report |
| `GET /api/reports/batch/{id}` | ✓ | ✗ | Batch report |
| `GET /api/reports/department/{id}` | ✓ | ✓ (own) | Department report |
| `GET /api/reports/map/{id}` | ✓ | ✓ (own) | MAP report |

#### 9.1.2 Middleware Implementation

```python
# backend/dependencies/auth.py

from fastapi import Depends, HTTPException, status
from typing import Annotated

def require_head_office(current_user: Annotated[User, Depends(get_current_user)]):
    """Require HEAD_OFFICE role"""
    if current_user.role != UserRole.HEAD_OFFICE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: HEAD_OFFICE role required"
        )
    return current_user

def require_department(current_user: Annotated[User, Depends(get_current_user)]):
    """Require DEPARTMENT role"""
    if current_user.role != UserRole.DEPARTMENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: DEPARTMENT role required"
        )
    return current_user

def verify_department_access(
    dept_id: int,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Verify user can access department data"""
    if current_user.role == UserRole.HEAD_OFFICE:
        return True
    
    if current_user.role == UserRole.DEPARTMENT:
        if current_user.department_id != dept_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Can only access own department"
            )
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )
```


### 9.2 Frontend Route Protection

```javascript
// ProtectedRoute.jsx (enhanced)

const ProtectedRoute = ({ children, allowedRoles }) => {
    const { user, loading } = useContext(AuthContext);
    const location = useLocation();

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        // Redirect to appropriate dashboard based on role
        if (user.role === 'department') {
            return <Navigate to="/" replace />;
        }
        return <Navigate to="/dashboard" replace />;
    }

    return children;
};

// App.jsx route configuration
<Routes>
    {/* Public routes */}
    <Route path="/login" element={<Login />} />

    {/* HEAD_OFFICE routes */}
    <Route path="/dashboard" element={
        <ProtectedRoute allowedRoles={['head_office']}>
            <ExecutiveDashboard />
        </ProtectedRoute>
    } />
    <Route path="/batches" element={
        <ProtectedRoute allowedRoles={['head_office']}>
            <BatchListPage />
        </ProtectedRoute>
    } />
    <Route path="/batches/:batchId/approve" element={
        <ProtectedRoute allowedRoles={['head_office']}>
            <AssignmentCenterPage />
        </ProtectedRoute>
    } />

    {/* DEPARTMENT routes */}
    <Route path="/" element={
        <ProtectedRoute allowedRoles={['department']}>
            <DepartmentDashboard />
        </ProtectedRoute>
    } />
    <Route path="/my-maps" element={
        <ProtectedRoute allowedRoles={['department']}>
            <MyMapsPage />
        </ProtectedRoute>
    } />
</Routes>
```

### 9.3 Performance Optimizations

#### 9.3.1 Database Indexing Strategy

```sql
-- Critical indexes for performance

-- Batch queries
CREATE INDEX idx_assignment_batches_status ON assignment_batches(status);
CREATE INDEX idx_assignment_batches_uploaded_by ON assignment_batches(uploaded_by);

-- MAP queries
CREATE INDEX idx_assignments_batch ON assignments(batch_id);
CREATE INDEX idx_assignments_dept ON assignments(department_id);
CREATE INDEX idx_assignments_lifecycle ON assignments(lifecycle_stage);
CREATE INDEX idx_assignments_deadline ON assignments(deadline);

-- Notification queries
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_dept_read ON notifications(department_id, is_read);

-- Requirement queries
CREATE INDEX idx_requirements_batch ON requirements(batch_id);
CREATE INDEX idx_requirements_domain ON requirements(domain);

-- Audit queries
CREATE INDEX idx_batch_audit_batch ON batch_audit_timeline(batch_id);
CREATE INDEX idx_status_history_assignment ON compliance_status_history(assignment_id);
```


#### 9.3.2 Query Optimization

```python
# Use eager loading to prevent N+1 queries

from sqlalchemy.orm import joinedload

def get_batch_with_details(batch_id: int):
    """Fetch batch with all related data in one query"""
    return db.query(AssignmentBatch).options(
        joinedload(AssignmentBatch.documents),
        joinedload(AssignmentBatch.requirements),
        joinedload(AssignmentBatch.assignments).joinedload(Assignment.department)
    ).filter_by(id=batch_id).first()

def get_department_maps(dept_id: int, filters: dict):
    """Optimized department MAP query"""
    query = db.query(Assignment).options(
        joinedload(Assignment.requirement),
        joinedload(Assignment.department)
    ).filter_by(department_id=dept_id)
    
    # Apply filters
    if filters.get('lifecycle_stage'):
        query = query.filter_by(lifecycle_stage=filters['lifecycle_stage'])
    if filters.get('priority'):
        query = query.filter_by(priority=filters['priority'])
    
    # Limit results
    return query.limit(100).all()
```

#### 9.3.3 Caching Strategy

```python
# Use Flask-Caching or similar for expensive queries

from functools import lru_cache
from datetime import datetime, timedelta

# Cache department dashboard data for 10 seconds
@lru_cache(maxsize=128)
def get_cached_dashboard_data(dept_id: int, cache_key: str):
    """Cache dashboard data with 10-second TTL"""
    return calculate_department_dashboard(dept_id)

# Generate cache key with timestamp rounded to 10 seconds
def get_dashboard_cache_key(dept_id: int):
    timestamp = int(datetime.utcnow().timestamp() / 10) * 10
    return f"dashboard_{dept_id}_{timestamp}"
```

#### 9.3.4 Frontend Performance

```javascript
// Use React.memo for expensive components
export const DepartmentDashboard = React.memo(({ departmentId }) => {
    // Component logic
});

// Use useMemo for expensive calculations
const sortedMaps = useMemo(() => {
    return maps.sort((a, b) => 
        new Date(b.deadline) - new Date(a.deadline)
    );
}, [maps]);

// Debounce search input
const debouncedSearch = useCallback(
    debounce((query) => {
        fetchSearchResults(query);
    }, 300),
    []
);
```

### 9.4 Security Measures

#### 9.4.1 Input Validation

```python
from pydantic import BaseModel, validator

class EvidenceSubmission(BaseModel):
    completion_notes: str
    implementation_reference: str | None = None
    implementation_date: date | None = None
    
    @validator('completion_notes')
    def validate_notes(cls, v):
        if len(v) < 10:
            raise ValueError('Completion notes must be at least 10 characters')
        if len(v) > 5000:
            raise ValueError('Completion notes too long')
        return v.strip()
```

#### 9.4.2 File Upload Security

```python
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file_upload(file):
    """Validate uploaded file"""
    if not file:
        raise ValueError("No file provided")
    
    # Check extension
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed: {ext}")
    
    # Check size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    return True
```


---

## 10. Migration Strategy

### 10.1 Migration Phases

#### Phase 1: Database Schema Migration
1. Create new tables: `assignment_batches`, `completion_evidence`, `notifications`, `batch_audit_timeline`
2. Add columns to existing tables: `documents`, `requirements`, `assignments`
3. Create indexes for performance
4. Create default legacy batch for existing data
5. Backfill batch_id for existing records

#### Phase 2: Backend API Development
1. Implement batch management endpoints
2. Implement grouped approval endpoints
3. Implement MAP lifecycle endpoints
4. Implement notification system
5. Implement dynamic metrics endpoints
6. Implement report generation
7. Add role-based access control middleware

#### Phase 3: Frontend Development
1. Create Assignment Center page
2. Create Department Dashboard
3. Create Batch List and Detail pages
4. Create MAP Detail page
5. Implement Contextual Graph
6. Add notification system (polling + UI)
7. Enhance Pipeline page with dynamic metrics
8. Update routing and access control

#### Phase 4: Integration & Testing
1. End-to-end workflow testing
2. Role-based access testing
3. Performance testing (100+ requirements, 9 departments)
4. Notification delivery testing
5. Report generation testing
6. Backward compatibility verification

### 10.2 Migration Script

```python
# migrations/002_add_batch_architecture.py

from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    """Apply migration"""
    
    # Step 1: Create assignment_batches table
    op.create_table(
        'assignment_batches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_name', sa.String(200), nullable=False),
        sa.Column('circular_name', sa.String(200), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('total_requirements', sa.Integer(), default=0),
        sa.Column('total_maps', sa.Integer(), default=0),
        sa.Column('completion_percentage', sa.Float(), default=0.0),
        sa.Column('verification_percentage', sa.Float(), default=0.0),
        sa.Column('ai_processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('ai_processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'])
    )
    
    # Step 2: Create completion_evidence table
    op.create_table(
        'completion_evidence',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('completion_notes', sa.Text(), nullable=False),
        sa.Column('evidence_document_path', sa.String(500), nullable=True),
        sa.Column('evidence_screenshot_path', sa.String(500), nullable=True),
        sa.Column('implementation_reference', sa.String(200), nullable=True),
        sa.Column('implementation_date', sa.Date(), nullable=True),
        sa.Column('submitted_by', sa.Integer(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id']),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'])
    )
    
    # Step 3: Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(20), default='normal'),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['batch_id'], ['assignment_batches.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'])
    )
    
    # Step 4: Create batch_audit_timeline table
    op.create_table(
        'batch_audit_timeline',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_description', sa.Text(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_role', sa.String(50), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['batch_id'], ['assignment_batches.id']),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'])
    )
    
    # Step 5: Add columns to documents
    op.add_column('documents', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('page_count', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('extracted_text_size', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('processing_duration_seconds', sa.Integer(), nullable=True))
    
    # Step 6: Add columns to requirements
    op.add_column('requirements', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.add_column('requirements', sa.Column('ai_confidence_score', sa.Float(), nullable=True))
    op.add_column('requirements', sa.Column('ai_reasoning', sa.Text(), nullable=True))
    op.add_column('requirements', sa.Column('chunk_count', sa.Integer(), nullable=True))
    
    # Step 7: Add columns to assignments
    op.add_column('assignments', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.add_column('assignments', sa.Column('lifecycle_stage', sa.String(50), default='assigned'))
    op.add_column('assignments', sa.Column('ai_confidence_score', sa.Float(), nullable=True))
    op.add_column('assignments', sa.Column('ai_reasoning', sa.Text(), nullable=True))
    op.add_column('assignments', sa.Column('map_title', sa.String(300), nullable=True))
    op.add_column('assignments', sa.Column('map_description', sa.Text(), nullable=True))
    op.add_column('assignments', sa.Column('accepted_at', sa.DateTime(), nullable=True))
    op.add_column('assignments', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('assignments', sa.Column('verified_at', sa.DateTime(), nullable=True))
    op.add_column('assignments', sa.Column('verified_by', sa.Integer(), nullable=True))
    op.add_column('assignments', sa.Column('closed_at', sa.DateTime(), nullable=True))
    op.add_column('assignments', sa.Column('deadline', sa.Date(), nullable=True))
    
    # Step 8: Create indexes
    op.create_index('idx_assignment_batches_status', 'assignment_batches', ['status'])
    op.create_index('idx_assignment_batches_uploaded_by', 'assignment_batches', ['uploaded_by'])
    op.create_index('idx_documents_batch', 'documents', ['batch_id'])
    op.create_index('idx_requirements_batch', 'requirements', ['batch_id'])
    op.create_index('idx_assignments_batch', 'assignments', ['batch_id'])
    op.create_index('idx_assignments_lifecycle', 'assignments', ['lifecycle_stage'])
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])
    op.create_index('idx_notifications_dept', 'notifications', ['department_id'])
    op.create_index('idx_notifications_read', 'notifications', ['is_read'])
    op.create_index('idx_batch_audit_batch', 'batch_audit_timeline', ['batch_id'])
    op.create_index('idx_completion_evidence_assignment', 'completion_evidence', ['assignment_id'])

def downgrade():
    """Rollback migration"""
    # Drop indexes
    op.drop_index('idx_assignment_batches_status')
    op.drop_index('idx_assignment_batches_uploaded_by')
    op.drop_index('idx_documents_batch')
    op.drop_index('idx_requirements_batch')
    op.drop_index('idx_assignments_batch')
    op.drop_index('idx_assignments_lifecycle')
    op.drop_index('idx_notifications_user')
    op.drop_index('idx_notifications_dept')
    op.drop_index('idx_notifications_read')
    op.drop_index('idx_batch_audit_batch')
    op.drop_index('idx_completion_evidence_assignment')
    
    # Drop columns
    op.drop_column('documents', 'batch_id')
    op.drop_column('documents', 'page_count')
    op.drop_column('documents', 'extracted_text_size')
    op.drop_column('documents', 'processing_duration_seconds')
    op.drop_column('requirements', 'batch_id')
    op.drop_column('requirements', 'ai_confidence_score')
    op.drop_column('requirements', 'ai_reasoning')
    op.drop_column('requirements', 'chunk_count')
    op.drop_column('assignments', 'batch_id')
    op.drop_column('assignments', 'lifecycle_stage')
    op.drop_column('assignments', 'ai_confidence_score')
    op.drop_column('assignments', 'ai_reasoning')
    op.drop_column('assignments', 'map_title')
    op.drop_column('assignments', 'map_description')
    op.drop_column('assignments', 'accepted_at')
    op.drop_column('assignments', 'started_at')
    op.drop_column('assignments', 'verified_at')
    op.drop_column('assignments', 'verified_by')
    op.drop_column('assignments', 'closed_at')
    op.drop_column('assignments', 'deadline')
    
    # Drop tables
    op.drop_table('batch_audit_timeline')
    op.drop_table('notifications')
    op.drop_table('completion_evidence')
    op.drop_table('assignment_batches')
```


### 10.3 Backward Compatibility Considerations

#### 10.3.1 Existing Data Handling

All existing data will be migrated to a "Legacy Data Batch":

```python
# Create legacy batch for existing data
def create_legacy_batch(db):
    """Create a legacy batch for existing requirements and assignments"""
    
    # Check if legacy batch already exists
    legacy_batch = db.query(AssignmentBatch).filter_by(
        circular_name='LEGACY/2024/00'
    ).first()
    
    if not legacy_batch:
        # Get admin user
        admin = db.query(User).filter_by(username='admin').first()
        
        # Create legacy batch
        legacy_batch = AssignmentBatch(
            batch_name='Legacy Data Batch',
            circular_name='LEGACY/2024/00',
            uploaded_by=admin.id,
            uploaded_at=datetime.utcnow(),
            status='published'
        )
        db.add(legacy_batch)
        db.commit()
        db.refresh(legacy_batch)
    
    # Update existing documents
    db.execute(
        "UPDATE documents SET batch_id = :batch_id WHERE batch_id IS NULL",
        {"batch_id": legacy_batch.id}
    )
    
    # Update existing requirements
    db.execute(
        "UPDATE requirements SET batch_id = :batch_id WHERE batch_id IS NULL",
        {"batch_id": legacy_batch.id}
    )
    
    # Update existing assignments
    db.execute(
        "UPDATE assignments SET batch_id = :batch_id, lifecycle_stage = 'assigned' WHERE batch_id IS NULL",
        {"batch_id": legacy_batch.id}
    )
    
    # Update batch totals
    legacy_batch.total_requirements = db.query(Requirement).filter_by(
        batch_id=legacy_batch.id
    ).count()
    legacy_batch.total_maps = db.query(Assignment).filter_by(
        batch_id=legacy_batch.id
    ).count()
    
    db.commit()
    
    return legacy_batch
```

#### 10.3.2 API Backward Compatibility

Existing API endpoints remain functional:

- `GET /api/requirements` - Still works, returns all requirements
- `GET /api/assignments` - Still works, returns all assignments
- Existing frontend pages continue to work during migration

New endpoints are additive, not replacing existing ones.

#### 10.3.3 Gradual Rollout Strategy

1. **Week 1**: Deploy backend with new tables and migration
2. **Week 2**: Deploy Assignment Center (HEAD_OFFICE only)
3. **Week 3**: Deploy Department Dashboard (DEPARTMENT users)
4. **Week 4**: Full system rollout with notifications and reports

### 10.4 Rollback Plan

If critical issues are discovered:

1. Run migration downgrade script
2. Restore database from backup
3. Revert backend code to Phase 1
4. Revert frontend code to Phase 1
5. Clear cached data
6. Restart services

**Data Loss Risk**: Minimal if rollback within 24 hours. New batches created during Phase 2 will be lost.

---

## 11. Implementation Checklist

### 11.1 Backend Tasks

- [ ] Create migration script for new tables
- [ ] Implement Assignment Batch model and CRUD
- [ ] Implement Notification model and service
- [ ] Implement Completion Evidence model
- [ ] Implement Batch Audit Timeline model
- [ ] Add batch_id to Documents, Requirements, Assignments
- [ ] Implement grouped approval endpoint
- [ ] Implement MAP lifecycle endpoints
- [ ] Implement dynamic metrics calculation
- [ ] Implement notification creation logic
- [ ] Implement report generation (4 types)
- [ ] Add role-based middleware
- [ ] Create indexes for performance
- [ ] Write unit tests for new endpoints
- [ ] Write integration tests for workflows

### 11.2 Frontend Tasks

- [ ] Create NotificationContext and Provider
- [ ] Create NotificationBadge component
- [ ] Create NotificationDropdown component
- [ ] Create AssignmentCenterPage (grouped approval)
- [ ] Create BatchListPage
- [ ] Create BatchDetailPage
- [ ] Create DepartmentDashboard (operational focus)
- [ ] Create MyMapsPage
- [ ] Create MapDetailPage with evidence submission
- [ ] Create ContextualGraph component
- [ ] Enhance PipelinePage with dynamic metrics
- [ ] Update routing with role-based protection
- [ ] Implement polling hooks
- [ ] Add report export buttons
- [ ] Create evidence upload components
- [ ] Write component tests
- [ ] Write E2E tests for critical flows

### 11.3 Testing Scenarios

- [ ] HEAD_OFFICE uploads circular → AI processes → pending approval
- [ ] HEAD_OFFICE approves grouped department assignments
- [ ] Departments receive notifications
- [ ] Department user views operational dashboard
- [ ] Department user accepts MAP
- [ ] Department user updates MAP to in_progress
- [ ] Department user submits completion evidence
- [ ] HEAD_OFFICE verifies completed MAP
- [ ] Notifications sent at each stage
- [ ] Batch status updates correctly
- [ ] Reports generate correctly (4 types)
- [ ] Role-based access control enforced
- [ ] Polling updates dashboards without refresh
- [ ] 100+ requirements handled efficiently
- [ ] 9 concurrent departments work smoothly

---

## 12. Conclusion

This revised design introduces **Assignment Batch** as the central workflow entity, enabling enterprise-scale compliance management with:

- **Scalability**: Handle multiple compliance campaigns simultaneously
- **Operational Focus**: Department dashboards prioritize daily execution
- **Transparency**: AI confidence scores and reasoning visible throughout
- **Efficiency**: Grouped approval reduces Head Office workload
- **Traceability**: Complete audit timeline for every batch
- **Evidence-Based**: Mandatory evidence submission for completion
- **Real Metrics**: Dynamic pipeline metrics from actual processing

The design maintains **100% backward compatibility** with Phase 1 while introducing powerful new capabilities for realistic banking compliance workflows.

