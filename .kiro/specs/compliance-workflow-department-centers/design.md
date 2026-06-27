# Technical Design Document

## Document Information
- **Feature**: Compliance Workflow & Department Action Centers (Phase 2)
- **Spec ID**: compliance-workflow-department-centers
- **Version**: 1.0
- **Date**: June 26, 2026
- **Status**: Draft

## Table of Contents
1. [Introduction](#introduction)
2. [High-Level Design](#high-level-design)
3. [Database Design](#database-design)
4. [Backend API Design](#backend-api-design)
5. [Frontend Architecture](#frontend-architecture)
6. [Component Specifications](#component-specifications)
7. [Security Architecture](#security-architecture)
8. [Performance Optimization](#performance-optimization)
9. [Integration Points](#integration-points)
10. [Deployment Strategy](#deployment-strategy)

## 1. Introduction

### 1.1 Purpose
This document provides the technical design for Phase 2 of RegIntel AI, transforming the analytics dashboard into a realistic banking compliance workflow system with:
- Manual approval workflow for AI-suggested assignments
- Role-based department portals
- Real-time status synchronization
- Complete audit trails
- PDF report generation

### 1.2 Scope
**In Scope:**
- New Assignment Center for Head Office approval workflow
- Department-scoped portals with restricted access
- Task lifecycle management (Assigned → In Progress → Completed → Verified)
- Real-time updates via polling mechanism
- Audit trail tracking
- PDF report generation infrastructure
- Role-based access control enforcement

**Out of Scope:**
- Email notifications (offline system)
- Websocket implementation (using polling instead)
- Mobile applications
- External system integrations
- Advanced ML model training

### 1.3 Design Principles
1. **Preserve Phase 1**: No breaking changes to existing authentication or AI pipeline
2. **Offline First**: System must function without internet connectivity
3. **Security**: Strict role-based access control with proper authorization
4. **Performance**: Handle 100+ requirements per circular, 9 concurrent departments
5. **Maintainability**: Follow existing code patterns and conventions


## 2. High-Level Design

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT TIER (React SPA)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────┐         ┌──────────────────────┐         │
│  │   Head Office UI     │         │   Department UI      │         │
│  ├──────────────────────┤         ├──────────────────────┤         │
│  │ - Assignment Center  │         │ - Dept Dashboard     │         │
│  │ - Global Dashboard   │         │ - Assigned Reqs      │         │
│  │ - Upload Pipeline    │         │ - Assigned MAPs      │         │
│  │ - Global KG          │         │ - Dept KG (scoped)   │         │
│  │ - Verification UI    │         │ - Progress Tracker   │         │
│  │ - All Departments    │         │ - Profile            │         │
│  └──────────────────────┘         └──────────────────────┘         │
│           │                                  │                       │
│           └──────────────┬───────────────────┘                       │
│                          │                                           │
│                  ┌───────▼────────┐                                 │
│                  │  Auth Context   │                                 │
│                  │  (JWT Storage)  │                                 │
│                  └───────┬────────┘                                 │
│                          │                                           │
│                  ┌───────▼────────┐                                 │
│                  │  Polling Hook   │                                 │
│                  │  (5s interval)  │                                 │
│                  └───────┬────────┘                                 │
└──────────────────────────┼───────────────────────────────────────────┘
                           │ HTTPS/HTTP
┌──────────────────────────┼───────────────────────────────────────────┐
│                    APPLICATION TIER (FastAPI)                         │
├──────────────────────────┼───────────────────────────────────────────┤
│                          │                                           │
│  ┌───────────────────────▼────────────────────────────────────────┐ │
│  │             API Gateway (FastAPI main.py)                       │ │
│  │  - CORS Middleware                                              │ │
│  │  - JWT Auth Middleware                                          │ │
│  │  - Request Validation                                           │ │
│  └───────────────────┬───────────────────────────────┬────────────┘ │
│                      │                               │              │
│  ┌───────────────────▼───────────┐  ┌───────────────▼────────────┐ │
│  │   Assignment Router           │  │   Department Router        │ │
│  │  - POST /approve-assignment   │  │   - GET /dashboard         │ │
│  │  - POST /reject-assignment    │  │   - GET /assignments       │ │
│  │  - POST /reassign             │  │   - PUT /status            │ │
│  │  - GET /pending-assignments   │  │   - GET /knowledge-graph   │ │
│  │  - POST /verify               │  │   - GET /notifications     │ │
│  └───────────────────┬───────────┘  └───────────────┬────────────┘ │
│                      │                               │              │
│  ┌───────────────────▼───────────────────────────────▼────────────┐ │
│  │                    CRUD Layer (crud.py)                         │ │
│  │  - Role-based query filtering                                  │ │
│  │  - Department scoping logic                                    │ │
│  │  - Audit log creation                                          │ │
│  └───────────────────┬─────────────────────────────────────────────┘ │
│                      │                                              │
└──────────────────────┼──────────────────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────┼──────────────────────────────────────────────┐
│                DATA TIER (SQLite)                                    │
├──────────────────────┼──────────────────────────────────────────────┤
│  ┌───────────────────▼─────────────────────────────────────────┐   │
│  │  Tables (with Phase 2 Extensions)                            │   │
│  │  - users (existing)                                           │   │
│  │  - departments (existing)                                     │   │
│  │  - documents (existing)                                       │   │
│  │  - requirements (existing + ai_suggestion columns)            │   │
│  │  - assignments (existing + verified_by, verified_at)          │   │
│  │  - compliance_status_history (existing)                       │   │
│  │  - audit_logs (existing)                                      │   │
│  │  - notifications (NEW)                                        │   │
│  │  - ai_suggestions (NEW)                                       │   │
│  └───────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Workflow Architecture

**Complete Lifecycle Flow:**

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ Head Office │───▶│ AI Processing│───▶│ Assignment  │───▶│  Department  │
│   Upload    │    │   Pipeline    │    │   Center    │    │   Receives   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
      │                   │                    │                    │
      │                   │                    │                    │
      ▼                   ▼                    ▼                    ▼
   PDF Doc          Requirements +        AI Suggestions      Assignments
  Uploaded          MAP Generated         Displayed          (status: assigned)
                    + Dept Suggested     
                                         ┌─────────────┐
                                         │  Approve    │
                                         │  Reassign   │
                                         │  Reject     │
                                         └─────────────┘
                                                │
                                                ▼
┌──────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Department  │───▶│  Department  │───▶│ Head Office │───▶│   Verified   │
│  Executes    │    │  Completes   │    │  Verifies   │    │   (Final)    │
└──────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
      │                   │                    │                    │
      ▼                   ▼                    ▼                    ▼
  In Progress          Completed            Verified           Audit Trail
   (updates)          (awaiting)          (approved)           Complete
```


## 3. Database Design

### 3.1 Schema Extensions

**New Tables:**

```sql
-- AI Suggestions table (NEW)
CREATE TABLE ai_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL,
    suggested_department_id INTEGER NOT NULL,
    confidence_score REAL NOT NULL CHECK(confidence_score >= 0 AND confidence_score <= 100),
    reasoning TEXT,
    alternative_suggestions TEXT,  -- JSON array of {dept_id, score}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id),
    FOREIGN KEY (suggested_department_id) REFERENCES departments(id)
);

-- Notifications table (NEW)
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    notification_type VARCHAR(50) NOT NULL,  -- 'new_assignment', 'status_change'
    priority VARCHAR(20),
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (acknowledged_by) REFERENCES users(id)
);

-- MAP (Mitigation Action Plans) table (NEW)
CREATE TABLE maps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    map_id VARCHAR(100) UNIQUE NOT NULL,
    requirement_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    action_steps TEXT,  -- JSON array of steps
    priority VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id)
);

-- MAP Progress table (NEW)
CREATE TABLE map_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    map_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    progress_note TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (map_id) REFERENCES maps(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

**Extended Tables:**

```sql
-- Extend requirements table (ADD COLUMNS)
ALTER TABLE requirements ADD COLUMN ai_suggested_department_id INTEGER;
ALTER TABLE requirements ADD COLUMN ai_confidence_score REAL;
ALTER TABLE requirements ADD COLUMN ai_reasoning TEXT;
ALTER TABLE requirements ADD COLUMN assignment_status VARCHAR(50) DEFAULT 'pending_review';
    -- Values: 'pending_review', 'approved', 'rejected', 'assigned'

-- Extend assignments table (ADD COLUMNS)
ALTER TABLE assignments ADD COLUMN verified_by INTEGER;
ALTER TABLE assignments ADD COLUMN verified_at TIMESTAMP;
ALTER TABLE assignments ADD COLUMN deadline TIMESTAMP;
ALTER TABLE assignments ADD COLUMN is_manual_override BOOLEAN DEFAULT FALSE;
ALTER TABLE assignments ADD COLUMN acknowledgement_required BOOLEAN DEFAULT TRUE;
ALTER TABLE assignments ADD COLUMN map_id INTEGER;

-- Add foreign keys (SQLite requires recreating table in practice)
-- verified_by → users.id
-- map_id → maps.id

-- Update ComplianceStatus enum to include 'verified'
-- Status flow: pending → in_progress → completed → verified
```

### 3.2 Entity Relationship Diagram

```
┌──────────────┐       ┌────────────────┐       ┌───────────────┐
│   Document   │──────▶│  Requirement   │──────▶│ AI_Suggestion │
│              │ 1:N   │                │ 1:1   │               │
│ - id         │       │ - id           │       │ - id          │
│ - filename   │       │ - text         │       │ - confidence  │
│ - uploaded   │       │ - domain       │       │ - reasoning   │
└──────────────┘       │ - priority     │       └───────────────┘
                       │ - assignment_  │              │
                       │   status       │              │
                       └────────────────┘              │
                              │                        │
                              │ 1:N                    │ N:1
                              ▼                        ▼
                       ┌────────────────┐       ┌───────────────┐
                       │   Assignment   │──────▶│  Department   │
                       │                │ N:1   │               │
                       │ - id           │       │ - id          │
                       │ - status       │       │ - name        │
                       │ - assigned_at  │       │ - code        │
                       │ - verified_by  │       └───────────────┘
                       │ - map_id       │              │
                       └────────────────┘              │ 1:N
                              │                        ▼
                              │ 1:1                ┌──────────┐
                              ▼                    │  User    │
                       ┌────────────────┐          │          │
                       │ Notification   │          │ - id     │
                       │                │          │ - role   │
                       │ - assignment_id│          │ - dept_id│
                       │ - is_ack       │          └──────────┘
                       └────────────────┘
                              │
                              │ 1:N
                              ▼
                       ┌────────────────┐
                       │  Audit Trail   │
                       │  (via history) │
                       └────────────────┘
```


### 3.3 Data Access Patterns

**Head Office Queries:**
- Get all pending assignments (for Assignment Center): `SELECT * FROM requirements WHERE assignment_status = 'pending_review'`
- Get pending verifications: `SELECT * FROM assignments WHERE status = 'completed' AND verified_by IS NULL`
- Get all assignments across departments: `SELECT * FROM assignments JOIN departments...`

**Department Queries:**
- Get department assignments: `SELECT * FROM assignments WHERE department_id = ?`
- Get department knowledge graph: `SELECT requirements, maps WHERE assignment.department_id = ?`
- Get notifications: `SELECT * FROM notifications WHERE department_id = ? AND is_acknowledged = FALSE`

**Performance Indexes:**
```sql
CREATE INDEX idx_requirements_assignment_status ON requirements(assignment_status);
CREATE INDEX idx_assignments_department_status ON assignments(department_id, status);
CREATE INDEX idx_assignments_status ON assignments(status);
CREATE INDEX idx_notifications_dept_ack ON notifications(department_id, is_acknowledged);
CREATE INDEX idx_ai_suggestions_requirement ON ai_suggestions(requirement_id);
CREATE INDEX idx_maps_requirement ON maps(requirement_id);
```

## 4. Backend API Design

### 4.1 New API Endpoints

**Assignment Center Endpoints (HEAD_OFFICE only):**

```python
# Get pending assignments for review
GET /api/assignment-center/pending
Response: {
    "requirements": [
        {
            "id": 123,
            "requirement_id": "REQ_2024_001",
            "text": "Banks must implement...",
            "domain": "Cybersecurity",
            "priority": "high",
            "suggested_department": {
                "id": 5,
                "name": "Cyber Security",
                "code": "CYBER",
                "confidence_score": 92.5,
                "reasoning": "Requirement mentions cybersecurity controls..."
            },
            "alternative_suggestions": [
                {"dept_id": 2, "dept_name": "IT", "score": 75.0}
            ],
            "suggested_map": {
                "map_id": "MAP_2024_001",
                "title": "Implement Firewall Rules",
                "description": "..."
            },
            "source_document": "RBI/2024/01",
            "extracted_at": "2024-01-15T10:30:00Z"
        }
    ],
    "total_count": 45
}

# Approve assignment
POST /api/assignment-center/approve
Request: {
    "requirement_ids": [123, 124, 125],
    "department_id": 5,  # Can override AI suggestion
    "deadline": "2024-06-30T23:59:59Z",
    "remarks": "Urgent - regulatory deadline"
}
Response: {
    "success": true,
    "assignments_created": 3,
    "notification_sent": true
}

# Reassign to different department
POST /api/assignment-center/reassign
Request: {
    "requirement_id": 123,
    "from_department_id": 5,
    "to_department_id": 2,
    "reason": "Better suited for IT team"
}

# Reject assignment (don't assign)
POST /api/assignment-center/reject
Request: {
    "requirement_ids": [126],
    "reason": "Not applicable to our institution"
}

# Verify completed assignment
POST /api/assignment-center/verify
Request: {
    "assignment_id": 456,
    "verification_notes": "Reviewed and approved",
    "status": "verified"  # or "in_progress" to request rework
}
```

**Department Endpoints (DEPARTMENT only):**

```python
# Get department dashboard
GET /api/department/dashboard
Response: {
    "department": {
        "id": 5,
        "name": "Cyber Security",
        "code": "CYBER"
    },
    "metrics": {
        "total_assigned": 28,
        "assigned": 5,
        "in_progress": 12,
        "completed": 8,
        "verified": 3,
        "completion_percentage": 39.3
    },
    "priority_breakdown": {
        "critical": 2,
        "high": 8,
        "medium": 15,
        "low": 3
    },
    "recent_assignments": [...],
    "upcoming_deadlines": [...]
}

# Get assigned requirements
GET /api/department/requirements?status=assigned&priority=high
Response: {
    "requirements": [...],
    "total_count": 15,
    "filters_applied": {"status": "assigned", "priority": "high"}
}

# Update assignment status
PUT /api/department/assignments/{assignment_id}/status
Request: {
    "new_status": "in_progress",  # or "completed"
    "remarks": "Started implementation"
}
Response: {
    "success": true,
    "assignment": {...},
    "audit_trail_updated": true
}

# Get department knowledge graph (scoped)
GET /api/department/knowledge-graph
Response: {
    "nodes": [
        {"id": "doc_1", "type": "document", "label": "RBI/2024/01"},
        {"id": "req_123", "type": "requirement", "label": "REQ_001", "status": "in_progress"},
        {"id": "map_456", "type": "map", "label": "MAP_001"},
        {"id": "dept_5", "type": "department", "label": "Cyber Security"}
    ],
    "edges": [
        {"from": "doc_1", "to": "req_123"},
        {"from": "req_123", "to": "map_456"},
        {"from": "map_456", "to": "dept_5"}
    ]
}

# Get notifications
GET /api/department/notifications?unread=true
Response: {
    "notifications": [
        {
            "id": 789,
            "type": "new_assignment",
            "assignment_id": 456,
            "priority": "high",
            "deadline": "2024-06-30",
            "source_circular": "RBI/2024/01",
            "created_at": "2024-01-15T14:00:00Z",
            "is_acknowledged": false
        }
    ],
    "unread_count": 5
}

# Acknowledge notification
POST /api/department/notifications/{notification_id}/acknowledge
```


**Polling Endpoint (ALL roles):**

```python
# Get updates since last check
GET /api/updates?since=2024-01-15T14:00:00Z&department_id=5
Response: {
    "has_updates": true,
    "last_update_time": "2024-01-15T14:05:23Z",
    "updates": {
        "assignments": [
            {"id": 456, "status": "in_progress", "updated_at": "..."}
        ],
        "notifications": [
            {"id": 789, "type": "new_assignment"}
        ],
        "metrics": {
            "completion_percentage": 42.5
        }
    }
}
```

### 4.2 Authorization Middleware

**Role-based Access Control Implementation:**

```python
# backend/auth.py

from functools import wraps
from fastapi import HTTPException, Depends, status
from .security import decode_access_token
from .crud import get_user_by_username

def require_role(allowed_roles: List[str]):
    """Decorator to enforce role-based access control"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {allowed_roles}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_department_access(func):
    """Decorator to ensure department users can only access their own data"""
    @wraps(func)
    async def wrapper(*args, department_id: int, current_user: User = Depends(get_current_user), **kwargs):
        if current_user.role == "department" and current_user.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view your own department's data."
            )
        return await func(*args, department_id=department_id, current_user=current_user, **kwargs)
    return wrapper

# Usage example in routers:
@router.get("/department/dashboard")
@require_role(["department"])
@require_department_access
async def get_department_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_department_dashboard(db, current_user.department_id)
```

## 5. Frontend Architecture

### 5.1 Component Structure

```
frontend/dashboard/src/
├── pages/
│   ├── AssignmentCenter.jsx      (NEW - Head Office only)
│   ├── DepartmentDashboard.jsx   (NEW - Department only)
│   ├── DepartmentRequirements.jsx (NEW - Department only)
│   ├── DepartmentMAPs.jsx         (NEW - Department only)
│   ├── DepartmentGraph.jsx        (NEW - Department scoped)
│   ├── ProgressTracker.jsx        (NEW - Department only)
│   ├── CompletedWork.jsx          (NEW - Department only)
│   ├── Profile.jsx                (NEW - Department only)
│   ├── Dashboard.jsx              (UPDATED - Head Office only)
│   ├── Pipeline.jsx               (UPDATED - Head Office only)
│   ├── Graph.jsx                  (UPDATED - Head Office only)
│   └── ...existing pages
├── components/
│   ├── AssignmentCard.jsx         (NEW - Display AI suggestions)
│   ├── StatusBadge.jsx            (NEW - Visual status indicators)
│   ├── NotificationBell.jsx       (NEW - Notification dropdown)
│   ├── DepartmentFilter.jsx       (NEW - Filter by dept)
│   ├── PriorityBadge.jsx          (NEW - Priority indicators)
│   ├── AuditTimeline.jsx          (NEW - Display audit trail)
│   ├── ConfidenceScore.jsx        (NEW - AI confidence display)
│   ├── RoleGuard.jsx              (NEW - Protect routes by role)
│   └── ...existing components
├── hooks/
│   ├── usePolling.js              (NEW - Polling hook)
│   ├── useDepartmentData.js       (NEW - Department data fetching)
│   ├── useNotifications.js        (NEW - Notification management)
│   └── useRealTimeUpdates.js      (NEW - Real-time sync)
├── context/
│   ├── AuthContext.jsx            (EXISTING - preserved)
│   ├── NotificationContext.jsx    (NEW - Notification state)
│   └── DepartmentContext.jsx      (NEW - Department-scoped state)
└── utils/
    ├── roleUtils.js               (NEW - Role check utilities)
    ├── statusUtils.js             (NEW - Status transition logic)
    └── graphUtils.js              (NEW - Graph filtering)
```

### 5.2 Routing Architecture

```javascript
// App.jsx - Updated routing with role-based access

function App() {
  const { user, loading } = useAuth();
  
  if (loading) return <LoadingScreen />;
  
  if (!user) return <Navigate to="/login" />;
  
  return (
    <Routes>
      {/* Head Office Routes */}
      {user.role === 'head_office' && (
        <>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assignment-center" element={<AssignmentCenter />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/maps" element={<Maps />} />
          <Route path="/graph" element={<GlobalGraph />} />
          <Route path="/departments" element={<AllDepartments />} />
          <Route path="/verification" element={<VerificationQueue />} />
        </>
      )}
      
      {/* Department Routes */}
      {user.role === 'department' && (
        <>
          <Route path="/" element={<Navigate to="/department/dashboard" />} />
          <Route path="/department/dashboard" element={<DepartmentDashboard />} />
          <Route path="/department/requirements" element={<DepartmentRequirements />} />
          <Route path="/department/maps" element={<DepartmentMAPs />} />
          <Route path="/department/graph" element={<DepartmentGraph />} />
          <Route path="/department/progress" element={<ProgressTracker />} />
          <Route path="/department/completed" element={<CompletedWork />} />
          <Route path="/department/profile" element={<Profile />} />
        </>
      )}
      
      {/* Blocked routes for department users */}
      {user.role === 'department' && (
        <Route path="/pipeline" element={<Navigate to="/department/dashboard" />} />
        {/* Block other head office routes */}
      )}
      
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```


### 5.3 Real-Time Updates (Polling Implementation)

```javascript
// hooks/usePolling.js

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

export function usePolling(endpoint, interval = 5000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const { api, user } = useAuth();
  const intervalRef = useRef(null);
  const isVisible = usePageVisibility();

  useEffect(() => {
    if (!isVisible) {
      // Stop polling when tab is not visible
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    const fetchUpdates = async () => {
      try {
        const params = {
          since: lastUpdate || new Date().toISOString(),
        };
        
        if (user.role === 'department') {
          params.department_id = user.department_id;
        }

        const response = await api.get(endpoint, { params });
        
        if (response.data.has_updates) {
          setData(response.data.updates);
          setLastUpdate(response.data.last_update_time);
        }
        setError(null);
      } catch (err) {
        console.error('Polling error:', err);
        setError(err);
      }
    };

    // Initial fetch
    fetchUpdates();

    // Setup polling
    intervalRef.current = setInterval(fetchUpdates, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [endpoint, interval, lastUpdate, isVisible, user]);

  return { data, error, lastUpdate };
}

// hooks/usePageVisibility.js
function usePageVisibility() {
  const [isVisible, setIsVisible] = useState(!document.hidden);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return isVisible;
}
```

### 5.4 State Management Architecture

**Notification Context:**

```javascript
// context/NotificationContext.jsx

import { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { usePolling } from '../hooks/usePolling';

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  
  // Poll for new notifications
  const { data: updates } = usePolling('/api/department/notifications', 10000);
  
  useEffect(() => {
    if (updates && updates.notifications) {
      setNotifications(prev => {
        const newNotifs = updates.notifications.filter(
          n => !prev.some(p => p.id === n.id)
        );
        return [...newNotifs, ...prev];
      });
      setUnreadCount(updates.unread_count);
    }
  }, [updates]);
  
  const acknowledgeNotification = async (notificationId) => {
    try {
      await api.post(`/api/department/notifications/${notificationId}/acknowledge`);
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, is_acknowledged: true } : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to acknowledge notification:', err);
    }
  };
  
  return (
    <NotificationContext.Provider value={{ 
      notifications, 
      unreadCount, 
      acknowledgeNotification 
    }}>
      {children}
    </NotificationContext.Provider>
  );
}

export const useNotifications = () => useContext(NotificationContext);
```

## 6. Component Specifications

### 6.1 AssignmentCenter Component (Head Office)

```javascript
// pages/AssignmentCenter.jsx

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import AssignmentCard from '../components/AssignmentCard';
import ConfidenceScore from '../components/ConfidenceScore';

export default function AssignmentCenter() {
  const { api } = useAuth();
  const [pendingRequirements, setPendingRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState([]);
  const [sortBy, setSortBy] = useState('confidence'); // confidence, priority, date
  
  useEffect(() => {
    fetchPendingRequirements();
  }, []);
  
  const fetchPendingRequirements = async () => {
    try {
      const response = await api.get('/api/assignment-center/pending');
      setPendingRequirements(response.data.requirements);
    } catch (err) {
      console.error('Failed to fetch pending requirements:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleApprove = async (requirementIds, deptId) => {
    try {
      await api.post('/api/assignment-center/approve', {
        requirement_ids: requirementIds,
        department_id: deptId
      });
      // Refresh list
      fetchPendingRequirements();
      setSelectedIds([]);
    } catch (err) {
      console.error('Failed to approve assignment:', err);
    }
  };
  
  const handleReassign = async (requirementId, newDeptId, reason) => {
    try {
      await api.post('/api/assignment-center/reassign', {
        requirement_id: requirementId,
        to_department_id: newDeptId,
        reason
      });
      fetchPendingRequirements();
    } catch (err) {
      console.error('Failed to reassign:', err);
    }
  };
  
  const handleReject = async (requirementIds, reason) => {
    try {
      await api.post('/api/assignment-center/reject', {
        requirement_ids: requirementIds,
        reason
      });
      fetchPendingRequirements();
      setSelectedIds([]);
    } catch (err) {
      console.error('Failed to reject:', err);
    }
  };
  
  const sortedRequirements = [...pendingRequirements].sort((a, b) => {
    if (sortBy === 'confidence') {
      return b.suggested_department.confidence_score - 
             a.suggested_department.confidence_score;
    }
    // Other sorting logic...
  });
  
  return (
    <div style={{ padding: '24px' }}>
      <h1>Assignment Center</h1>
      <p>Review AI-suggested assignments before publishing to departments</p>
      
      {/* Toolbar */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="confidence">Sort by Confidence</option>
          <option value="priority">Sort by Priority</option>
          <option value="date">Sort by Date</option>
        </select>
        
        {selectedIds.length > 0 && (
          <button onClick={() => handleApprove(selectedIds)}>
            Approve Selected ({selectedIds.length})
          </button>
        )}
      </div>
      
      {/* Requirements List */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {sortedRequirements.map(req => (
            <AssignmentCard
              key={req.id}
              requirement={req}
              selected={selectedIds.includes(req.id)}
              onSelect={(id) => setSelectedIds(prev =>
                prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
              )}
              onApprove={(id) => handleApprove([id], req.suggested_department.id)}
              onReassign={(id) => handleReassign(id)}
              onReject={(id) => handleReject([id])}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```


### 6.2 DepartmentDashboard Component

```javascript
// pages/DepartmentDashboard.jsx

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';
import { usePolling } from '../hooks/usePolling';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';

export default function DepartmentDashboard() {
  const { api, user } = useAuth();
  const { unreadCount } = useNotifications();
  const [dashboard, setDashboard] = useState(null);
  const [filter, setFilter] = useState({ status: 'all', priority: 'all' });
  
  // Poll for updates
  const { data: updates } = usePolling('/api/updates', 5000);
  
  useEffect(() => {
    fetchDashboard();
  }, []);
  
  useEffect(() => {
    // Handle real-time updates
    if (updates && updates.metrics) {
      setDashboard(prev => ({
        ...prev,
        metrics: { ...prev.metrics, ...updates.metrics }
      }));
    }
  }, [updates]);
  
  const fetchDashboard = async () => {
    try {
      const response = await api.get('/api/department/dashboard');
      setDashboard(response.data);
    } catch (err) {
      console.error('Failed to fetch dashboard:', err);
    }
  };
  
  if (!dashboard) return <div>Loading...</div>;
  
  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h1>{dashboard.department.name} Dashboard</h1>
          <p>Track your department's compliance progress</p>
        </div>
        {unreadCount > 0 && (
          <div style={{ 
            padding: '8px 16px', 
            background: '#f59e0b', 
            borderRadius: '8px',
            color: 'white',
            fontWeight: 'bold'
          }}>
            {unreadCount} New Assignment{unreadCount > 1 ? 's' : ''}
          </div>
        )}
      </div>
      
      {/* Metrics Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)', 
        gap: '16px',
        marginBottom: '32px'
      }}>
        <MetricCard 
          title="Assigned" 
          value={dashboard.metrics.assigned}
          color="#6b7280"
        />
        <MetricCard 
          title="In Progress" 
          value={dashboard.metrics.in_progress}
          color="#f59e0b"
        />
        <MetricCard 
          title="Completed" 
          value={dashboard.metrics.completed}
          color="#10b981"
        />
        <MetricCard 
          title="Verified" 
          value={dashboard.metrics.verified}
          color="#3b82f6"
        />
      </div>
      
      {/* Completion Progress */}
      <div style={{ marginBottom: '32px' }}>
        <h3>Completion Progress</h3>
        <div style={{ 
          height: '32px', 
          background: '#e5e7eb', 
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${dashboard.metrics.completion_percentage}%`,
            background: 'linear-gradient(90deg, #10b981, #059669)',
            transition: 'width 0.5s ease-in-out',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold'
          }}>
            {dashboard.metrics.completion_percentage.toFixed(1)}%
          </div>
        </div>
      </div>
      
      {/* Priority Breakdown */}
      <div style={{ marginBottom: '32px' }}>
        <h3>Priority Breakdown</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          <PriorityCard priority="critical" count={dashboard.priority_breakdown.critical} />
          <PriorityCard priority="high" count={dashboard.priority_breakdown.high} />
          <PriorityCard priority="medium" count={dashboard.priority_breakdown.medium} />
          <PriorityCard priority="low" count={dashboard.priority_breakdown.low} />
        </div>
      </div>
      
      {/* Recent Assignments */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3>Recent Assignments</h3>
          <select 
            value={filter.status} 
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          >
            <option value="all">All Statuses</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <AssignmentList 
          assignments={dashboard.recent_assignments}
          filter={filter}
        />
      </div>
    </div>
  );
}

function MetricCard({ title, value, color }) {
  return (
    <div style={{ 
      padding: '20px', 
      background: '#1f2937', 
      borderRadius: '12px',
      border: `2px solid ${color}`
    }}>
      <div style={{ fontSize: '14px', color: '#9ca3af', marginBottom: '8px' }}>
        {title}
      </div>
      <div style={{ fontSize: '32px', fontWeight: 'bold', color }}>
        {value}
      </div>
    </div>
  );
}

function PriorityCard({ priority, count }) {
  const colors = {
    critical: '#ef4444',
    high: '#f59e0b',
    medium: '#3b82f6',
    low: '#6b7280'
  };
  
  return (
    <div style={{ 
      padding: '12px', 
      background: '#1f2937', 
      borderRadius: '8px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <span style={{ textTransform: 'capitalize', color: '#e5e7eb' }}>
        {priority}
      </span>
      <span style={{ 
        fontSize: '20px', 
        fontWeight: 'bold', 
        color: colors[priority] 
      }}>
        {count}
      </span>
    </div>
  );
}
```

### 6.3 Department Knowledge Graph (Scoped)

```javascript
// pages/DepartmentGraph.jsx

import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import GraphVisualization from '../components/GraphVisualization';

export default function DepartmentGraph() {
  const { api, user } = useAuth();
  const [graphData, setGraphData] = useState(null);
  const [filter, setFilter] = useState({ status: 'all', priority: 'all' });
  
  useEffect(() => {
    fetchGraph();
  }, [filter]);
  
  const fetchGraph = async () => {
    try {
      const response = await api.get('/api/department/knowledge-graph', {
        params: filter
      });
      
      // Filter graph to only show department-relevant nodes
      const filteredData = filterGraphData(response.data, user.department_id);
      setGraphData(filteredData);
    } catch (err) {
      console.error('Failed to fetch graph:', err);
    }
  };
  
  const filterGraphData = (data, deptId) => {
    // Only include nodes relevant to this department
    const relevantNodes = data.nodes.filter(node => {
      if (node.type === 'department') {
        return node.id === `dept_${deptId}`;
      }
      // Include documents, requirements, and MAPs that are assigned to this dept
      return node.department_id === deptId || node.type === 'document';
    });
    
    const nodeIds = new Set(relevantNodes.map(n => n.id));
    const relevantEdges = data.edges.filter(edge =>
      nodeIds.has(edge.from) && nodeIds.has(edge.to)
    );
    
    return { nodes: relevantNodes, edges: relevantEdges };
  };
  
  return (
    <div style={{ padding: '24px' }}>
      <h1>Department Knowledge Graph</h1>
      <p>Visualize your department's compliance work</p>
      
      {/* Filters */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <select 
          value={filter.status} 
          onChange={(e) => setFilter({ ...filter, status: e.target.value })}
        >
          <option value="all">All Statuses</option>
          <option value="assigned">Assigned</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="verified">Verified</option>
        </select>
        
        <select 
          value={filter.priority} 
          onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>
      
      {/* Graph Visualization */}
      {graphData ? (
        <GraphVisualization 
          data={graphData}
          onNodeClick={(node) => console.log('Node clicked:', node)}
          colorByStatus={true}
        />
      ) : (
        <div>Loading graph...</div>
      )}
      
      {/* Legend */}
      <div style={{ marginTop: '24px' }}>
        <h3>Status Legend</h3>
        <div style={{ display: 'flex', gap: '16px' }}>
          <LegendItem color="#6b7280" label="Assigned" />
          <LegendItem color="#f59e0b" label="In Progress" />
          <LegendItem color="#10b981" label="Completed" />
          <LegendItem color="#3b82f6" label="Verified" />
        </div>
      </div>
    </div>
  );
}

function LegendItem({ color, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ 
        width: '16px', 
        height: '16px', 
        background: color, 
        borderRadius: '50%' 
      }} />
      <span>{label}</span>
    </div>
  );
}
```


## 7. Security Architecture

### 7.1 Authentication Flow (Preserved from Phase 1)

```
1. User Login
   ↓
2. Backend validates credentials (bcrypt)
   ↓
3. Generate JWT token (8-hour expiry)
   ↓
4. Return token to frontend
   ↓
5. Store token in localStorage
   ↓
6. Include token in all API requests (Authorization: Bearer <token>)
   ↓
7. Backend validates token on each request
   ↓
8. Extract user role from token
   ↓
9. Apply role-based authorization
```

### 7.2 Authorization Matrix

| Endpoint | HEAD_OFFICE | DEPARTMENT |
|----------|-------------|------------|
| GET /api/assignment-center/pending | ✅ | ❌ |
| POST /api/assignment-center/approve | ✅ | ❌ |
| POST /api/assignment-center/verify | ✅ | ❌ |
| GET /api/department/dashboard | ✅ (all depts) | ✅ (own dept only) |
| PUT /api/department/assignments/:id/status | ✅ | ✅ (own dept only) |
| GET /api/department/knowledge-graph | ❌ | ✅ (scoped) |
| GET /api/admin/* | ✅ | ❌ |
| POST /api/documents/upload | ✅ | ❌ |

### 7.3 Data Access Control

**Department Scoping Logic:**

```python
# backend/crud.py

def get_department_assignments(
    db: Session,
    department_id: int,
    current_user: User,
    status: Optional[str] = None
) -> List[Assignment]:
    """Get assignments for a department with proper access control"""
    
    # Head Office can view all departments
    if current_user.role == "head_office":
        query = db.query(Assignment).filter(Assignment.department_id == department_id)
    # Department users can only view their own department
    elif current_user.role == "department":
        if current_user.department_id != department_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied. You can only view your own department's assignments."
            )
        query = db.query(Assignment).filter(Assignment.department_id == current_user.department_id)
    else:
        raise HTTPException(status_code=403, detail="Invalid role")
    
    if status:
        query = query.filter(Assignment.status == status)
    
    return query.all()
```

### 7.4 Input Validation

```python
# backend/schemas.py - Add validation

class AssignmentApproveRequest(BaseModel):
    requirement_ids: List[int] = Field(..., min_items=1, max_items=100)
    department_id: int = Field(..., gt=0)
    deadline: Optional[datetime] = None
    remarks: Optional[str] = Field(None, max_length=1000)
    
    @validator('requirement_ids')
    def validate_requirement_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Duplicate requirement IDs not allowed')
        return v

class StatusUpdateRequest(BaseModel):
    new_status: str = Field(..., regex='^(in_progress|completed)$')
    remarks: Optional[str] = Field(None, max_length=2000)
    
    @validator('new_status')
    def validate_status_transition(cls, v):
        allowed_transitions = ['in_progress', 'completed']
        if v not in allowed_transitions:
            raise ValueError(f'Department users can only set status to: {allowed_transitions}')
        return v
```

### 7.5 SQL Injection Prevention

All database queries use SQLAlchemy ORM with parameterized queries:

```python
# SAFE - Parameterized query
assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

# SAFE - Using ORM filters
requirements = db.query(Requirement).filter(
    Requirement.assignment_status == 'pending_review',
    Requirement.priority == priority
).all()

# NEVER do this (vulnerable to SQL injection):
# query = f"SELECT * FROM assignments WHERE id = {assignment_id}"  # ❌ WRONG
```

## 8. Performance Optimization

### 8.1 Database Indexing Strategy

```sql
-- Critical indexes for performance

-- Assignment queries (most frequent)
CREATE INDEX idx_assignments_dept_status ON assignments(department_id, status);
CREATE INDEX idx_assignments_status_verified ON assignments(status, verified_by);

-- Requirement queries
CREATE INDEX idx_requirements_assignment_status ON requirements(assignment_status);
CREATE INDEX idx_requirements_domain_priority ON requirements(domain, priority);

-- Notification queries
CREATE INDEX idx_notifications_dept_ack ON notifications(department_id, is_acknowledged);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);

-- AI Suggestion queries
CREATE INDEX idx_ai_suggestions_requirement ON ai_suggestions(requirement_id);
CREATE INDEX idx_ai_suggestions_confidence ON ai_suggestions(confidence_score DESC);

-- Audit queries
CREATE INDEX idx_compliance_history_assignment ON compliance_status_history(assignment_id, changed_at DESC);
CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp DESC);
```

### 8.2 Query Optimization

**Batch Loading Strategy:**

```python
# Efficient batch loading with joins
def get_assignments_with_details(db: Session, department_id: int) -> List[Dict]:
    """Fetch assignments with all related data in a single query"""
    
    assignments = db.query(Assignment)\
        .join(Requirement)\
        .join(Department)\
        .join(Document)\
        .options(
            joinedload(Assignment.requirement),
            joinedload(Assignment.department),
            joinedload(Assignment.requirement.document)
        )\
        .filter(Assignment.department_id == department_id)\
        .all()
    
    return assignments

# Avoid N+1 queries by eager loading
```

### 8.3 Frontend Performance

**Lazy Loading:**

```javascript
// Lazy load pages for faster initial load
const AssignmentCenter = lazy(() => import('./pages/AssignmentCenter'));
const DepartmentDashboard = lazy(() => import('./pages/DepartmentDashboard'));
const DepartmentGraph = lazy(() => import('./pages/DepartmentGraph'));
```

**Memoization:**

```javascript
// Memoize expensive computations
import { useMemo } from 'react';

function DepartmentDashboard() {
  const assignments = useFetchAssignments();
  
  const metrics = useMemo(() => {
    return {
      total: assignments.length,
      assigned: assignments.filter(a => a.status === 'assigned').length,
      in_progress: assignments.filter(a => a.status === 'in_progress').length,
      completed: assignments.filter(a => a.status === 'completed').length,
      verified: assignments.filter(a => a.status === 'verified').length,
    };
  }, [assignments]);
  
  return <div>{/* render metrics */}</div>;
}
```

**Virtual Scrolling:**

```javascript
// Use virtual scrolling for large lists
import { FixedSizeList } from 'react-window';

function RequirementList({ requirements }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <RequirementCard requirement={requirements[index]} />
    </div>
  );
  
  return (
    <FixedSizeList
      height={600}
      itemCount={requirements.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

### 8.4 Caching Strategy

**Backend Caching:**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_department_by_id_cached(department_id: int):
    """Cache department lookups (departments rarely change)"""
    return db.query(Department).filter(Department.id == department_id).first()

# Clear cache when department is updated
def update_department(db: Session, dept_id: int, updates: dict):
    # Update logic...
    get_department_by_id_cached.cache_clear()
```

**Frontend Caching:**

```javascript
// Cache API responses
const cache = new Map();

async function fetchWithCache(url, options = {}) {
  const cacheKey = `${url}_${JSON.stringify(options)}`;
  
  if (cache.has(cacheKey)) {
    const { data, timestamp } = cache.get(cacheKey);
    // Use cached data if less than 5 minutes old
    if (Date.now() - timestamp < 5 * 60 * 1000) {
      return data;
    }
  }
  
  const response = await api.get(url, options);
  cache.set(cacheKey, { data: response.data, timestamp: Date.now() });
  return response.data;
}
```


## 9. Integration Points

### 9.1 Phase 1 Authentication Integration

**Preserve Existing Authentication:**

```python
# backend/auth.py - Extend existing auth without breaking changes

from .security import decode_access_token, get_password_hash, verify_password
from .models import User, UserRole

# EXISTING - Keep as is
def authenticate_user(db: Session, username: str, password: str):
    """Existing authentication function - DO NOT MODIFY"""
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# EXISTING - Keep as is
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Existing current user extraction - DO NOT MODIFY"""
    credentials_exception = HTTPException(...)
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username = payload.get("sub")
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

# NEW - Add role-based decorators
def require_head_office(current_user: User = Depends(get_current_user)):
    """Require head office role"""
    if current_user.role != UserRole.HEAD_OFFICE:
        raise HTTPException(status_code=403, detail="Head Office access required")
    return current_user

def require_department(current_user: User = Depends(get_current_user)):
    """Require department role"""
    if current_user.role != UserRole.DEPARTMENT:
        raise HTTPException(status_code=403, detail="Department access required")
    return current_user
```

### 9.2 AI Pipeline Integration

**Preserve Existing Scripts:**

All 42 existing AI pipeline scripts remain untouched. New functionality added as separate scripts:

```
ai_pipeline/
├── (existing scripts - DO NOT MODIFY)
│   ├── extract_requirements.py
│   ├── gap_analysis_engine.py
│   ├── cross_reference_parser.py
│   └── ... (39 more)
│
└── (new scripts for Phase 2)
    ├── suggest_department.py          (NEW - AI department suggestion)
    ├── calculate_confidence.py        (NEW - Confidence scoring)
    └── generate_alternatives.py       (NEW - Alternative dept suggestions)
```

**New AI Script: suggest_department.py**

```python
"""
AI Department Suggestion Script
Analyzes requirements and suggests appropriate departments with confidence scores
"""
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Department domain keywords (existing in system)
DEPARTMENT_DOMAINS = {
    "COMP": ["compliance", "regulatory", "audit", "governance"],
    "RISK": ["risk", "credit", "market", "operational risk"],
    "TRES": ["treasury", "liquidity", "investment", "funds"],
    "OPS": ["operations", "processing", "settlement", "transaction"],
    "CYBER": ["cybersecurity", "information security", "data protection", "firewall"],
    "IT": ["technology", "system", "infrastructure", "software"],
    "FIN": ["finance", "accounting", "reporting", "financial"],
    "AML": ["aml", "money laundering", "kyc", "suspicious activity"],
    "LEGAL": ["legal", "contract", "litigation", "counsel"]
}

def suggest_department_for_requirement(requirement_text: str, domain: str) -> dict:
    """
    Suggest department(s) for a requirement
    
    Returns:
        {
            "suggested_department_code": "CYBER",
            "confidence_score": 92.5,
            "reasoning": "Requirement mentions cybersecurity controls...",
            "alternatives": [
                {"code": "IT", "score": 75.0},
                {"code": "RISK", "score": 60.0}
            ]
        }
    """
    # Simple keyword-based matching (can be enhanced with ML)
    scores = {}
    
    req_lower = requirement_text.lower()
    
    for dept_code, keywords in DEPARTMENT_DOMAINS.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in req_lower:
                score += 10
                matched_keywords.append(keyword)
        
        # Bonus for domain match
        if domain and dept_code in ["CYBER", "AML", "RISK"] and domain.lower() in dept_code.lower():
            score += 30
        
        if score > 0:
            scores[dept_code] = {
                "score": min(score, 100),
                "keywords": matched_keywords
            }
    
    if not scores:
        # Default to Compliance if no match
        return {
            "suggested_department_code": "COMP",
            "confidence_score": 50.0,
            "reasoning": "Default assignment to Compliance department",
            "alternatives": []
        }
    
    # Sort by score
    sorted_depts = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    top_dept = sorted_depts[0]
    
    return {
        "suggested_department_code": top_dept[0],
        "confidence_score": float(top_dept[1]["score"]),
        "reasoning": f"Matched keywords: {', '.join(top_dept[1]['keywords'])}",
        "alternatives": [
            {"code": dept, "score": float(data["score"])}
            for dept, data in sorted_depts[1:3]  # Top 2 alternatives
        ]
    }

# Integration with existing pipeline
def process_document_with_suggestions(document_id: int):
    """
    Process document through existing pipeline + add dept suggestions
    This is called AFTER existing requirement extraction
    """
    from backend.database import SessionLocal
    from backend.crud import get_requirements_by_document
    from backend.models import AISuggestion
    
    db = SessionLocal()
    try:
        # Get extracted requirements (from existing pipeline)
        requirements = get_requirements_by_document(db, document_id)
        
        # For each requirement, generate department suggestion
        for req in requirements:
            suggestion = suggest_department_for_requirement(req.text, req.domain)
            
            # Store suggestion in database
            ai_suggestion = AISuggestion(
                requirement_id=req.id,
                suggested_department_code=suggestion["suggested_department_code"],
                confidence_score=suggestion["confidence_score"],
                reasoning=suggestion["reasoning"],
                alternative_suggestions=json.dumps(suggestion["alternatives"])
            )
            db.add(ai_suggestion)
            
            # Update requirement with suggestion
            req.ai_suggested_department_code = suggestion["suggested_department_code"]
            req.ai_confidence_score = suggestion["confidence_score"]
            req.ai_reasoning = suggestion["reasoning"]
            req.assignment_status = "pending_review"
        
        db.commit()
        return {"success": True, "requirements_processed": len(requirements)}
    
    finally:
        db.close()
```

### 9.3 CRUD Operation Extensions

**Extend Existing CRUD Without Breaking Changes:**

```python
# backend/crud.py - Add new functions, keep existing ones intact

# EXISTING functions - DO NOT MODIFY
def get_user_by_username(db: Session, username: str):
    """EXISTING - Keep as is"""
    pass

def create_user(db: Session, user: schemas.UserCreate):
    """EXISTING - Keep as is"""
    pass

# NEW functions for Phase 2
def get_pending_assignments_for_review(db: Session) -> List[Requirement]:
    """Get requirements awaiting Head Office approval"""
    return db.query(Requirement)\
        .filter(Requirement.assignment_status == 'pending_review')\
        .order_by(Requirement.ai_confidence_score.desc())\
        .all()

def approve_assignment(
    db: Session,
    requirement_id: int,
    department_id: int,
    approved_by: int,
    deadline: Optional[datetime] = None
) -> Assignment:
    """Approve AI suggestion and create assignment"""
    # Update requirement status
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    requirement.assignment_status = 'approved'
    
    # Create assignment
    assignment = Assignment(
        requirement_id=requirement_id,
        department_id=department_id,
        assigned_by=approved_by,
        status='assigned',
        deadline=deadline,
        is_manual_override=(department_id != requirement.ai_suggested_department_id)
    )
    db.add(assignment)
    
    # Create notification
    notification = Notification(
        assignment_id=assignment.id,
        department_id=department_id,
        notification_type='new_assignment',
        priority=requirement.priority
    )
    db.add(notification)
    
    # Audit log
    create_audit_log(
        db, approved_by, 'approve_assignment',
        entity_type='assignment',
        entity_id=assignment.id,
        details=f"Approved assignment of req {requirement_id} to dept {department_id}"
    )
    
    db.commit()
    db.refresh(assignment)
    return assignment

def verify_assignment(
    db: Session,
    assignment_id: int,
    verified_by: int,
    verification_notes: Optional[str] = None
) -> Assignment:
    """Verify completed assignment"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise ValueError("Assignment not found")
    
    if assignment.status != 'completed':
        raise ValueError("Can only verify completed assignments")
    
    # Update to verified
    old_status = assignment.status
    assignment.status = 'verified'
    assignment.verified_by = verified_by
    assignment.verified_at = datetime.utcnow()
    
    if verification_notes:
        assignment.remarks = f"{assignment.remarks}\n\nVerification: {verification_notes}"
    
    # Create history record
    history = ComplianceStatusHistory(
        assignment_id=assignment_id,
        old_status=old_status,
        new_status='verified',
        remarks=verification_notes,
        changed_by=verified_by
    )
    db.add(history)
    
    # Audit log
    create_audit_log(
        db, verified_by, 'verify_assignment',
        entity_type='assignment',
        entity_id=assignment_id,
        details=f"Verified assignment {assignment_id}"
    )
    
    db.commit()
    db.refresh(assignment)
    return assignment

def get_department_scoped_graph(db: Session, department_id: int) -> dict:
    """Get knowledge graph scoped to department"""
    # Get all assignments for this department
    assignments = db.query(Assignment)\
        .filter(Assignment.department_id == department_id)\
        .all()
    
    requirement_ids = [a.requirement_id for a in assignments]
    
    # Get requirements
    requirements = db.query(Requirement)\
        .filter(Requirement.id.in_(requirement_ids))\
        .all()
    
    document_ids = list(set([r.document_id for r in requirements]))
    
    # Get documents
    documents = db.query(Document)\
        .filter(Document.id.in_(document_ids))\
        .all()
    
    # Get MAPs
    maps = db.query(MAP)\
        .filter(MAP.requirement_id.in_(requirement_ids))\
        .all()
    
    # Build graph structure
    nodes = []
    edges = []
    
    # Add document nodes
    for doc in documents:
        nodes.append({
            "id": f"doc_{doc.id}",
            "type": "document",
            "label": doc.filename,
            "data": {"id": doc.id, "filename": doc.filename}
        })
    
    # Add requirement nodes
    for req in requirements:
        assignment = next((a for a in assignments if a.requirement_id == req.id), None)
        nodes.append({
            "id": f"req_{req.id}",
            "type": "requirement",
            "label": req.requirement_id,
            "status": assignment.status if assignment else "pending",
            "priority": req.priority,
            "data": {"id": req.id, "text": req.text}
        })
        # Edge: document -> requirement
        edges.append({"from": f"doc_{req.document_id}", "to": f"req_{req.id}"})
    
    # Add MAP nodes
    for map_item in maps:
        nodes.append({
            "id": f"map_{map_item.id}",
            "type": "map",
            "label": map_item.map_id,
            "status": map_item.status,
            "data": {"id": map_item.id, "title": map_item.title}
        })
        # Edge: requirement -> MAP
        edges.append({"from": f"req_{map_item.requirement_id}", "to": f"map_{map_item.id}"})
    
    # Add department node
    department = db.query(Department).filter(Department.id == department_id).first()
    nodes.append({
        "id": f"dept_{department_id}",
        "type": "department",
        "label": department.name,
        "data": {"id": department_id, "name": department.name, "code": department.code}
    })
    
    # Edges: MAPs -> Department
    for map_item in maps:
        edges.append({"from": f"map_{map_item.id}", "to": f"dept_{department_id}"})
    
    return {"nodes": nodes, "edges": edges}
```

### 9.4 Router Extensions

**Add New Routers Without Modifying Existing:**

```python
# backend/routers/assignment_center_router.py (NEW FILE)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models
from ..auth import get_current_user, require_head_office
from ..database import get_db

router = APIRouter(prefix="/assignment-center", tags=["assignment-center"])

@router.get("/pending")
async def get_pending_assignments(
    current_user: models.User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """Get all requirements pending approval"""
    requirements = crud.get_pending_assignments_for_review(db)
    return {"requirements": requirements, "total_count": len(requirements)}

@router.post("/approve")
async def approve_assignments(
    request: schemas.AssignmentApproveRequest,
    current_user: models.User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """Approve one or more assignments"""
    assignments_created = []
    
    for req_id in request.requirement_ids:
        assignment = crud.approve_assignment(
            db, req_id, request.department_id,
            current_user.id, request.deadline
        )
        assignments_created.append(assignment)
    
    return {
        "success": True,
        "assignments_created": len(assignments_created),
        "notification_sent": True
    }

@router.post("/reject")
async def reject_assignments(
    request: schemas.AssignmentRejectRequest,
    current_user: models.User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """Reject assignment suggestions"""
    for req_id in request.requirement_ids:
        crud.reject_assignment(db, req_id, current_user.id, request.reason)
    
    return {"success": True, "rejected_count": len(request.requirement_ids)}

@router.post("/verify")
async def verify_assignment(
    request: schemas.VerificationRequest,
    current_user: models.User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """Verify completed assignment"""
    assignment = crud.verify_assignment(
        db, request.assignment_id, current_user.id, request.verification_notes
    )
    return {"success": True, "assignment": assignment}
```

**Register New Router in main.py:**

```python
# backend/main.py - ADD new router

from .routers import auth_router, admin_router, department_router
from .routers import assignment_center_router  # NEW

# Include routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(department_router.router, prefix="/api")
app.include_router(assignment_center_router.router, prefix="/api")  # NEW
```


## 10. Deployment Strategy

### 10.1 Database Migration

**Migration Script: migrate_phase2.py**

```python
"""
Database migration script for Phase 2
Adds new tables and columns without breaking existing data
"""
from sqlalchemy import create_engine, text
from backend.database import Base, engine
from backend.models import *  # Import all models

def migrate_to_phase2():
    """Execute Phase 2 database migrations"""
    
    print("Starting Phase 2 database migration...")
    
    with engine.begin() as conn:
        # 1. Add new columns to existing tables
        print("Adding new columns to requirements table...")
        try:
            conn.execute(text("""
                ALTER TABLE requirements 
                ADD COLUMN ai_suggested_department_id INTEGER
            """))
        except Exception as e:
            print(f"  Column ai_suggested_department_id may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE requirements 
                ADD COLUMN ai_confidence_score REAL
            """))
        except Exception as e:
            print(f"  Column ai_confidence_score may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE requirements 
                ADD COLUMN ai_reasoning TEXT
            """))
        except Exception as e:
            print(f"  Column ai_reasoning may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE requirements 
                ADD COLUMN assignment_status VARCHAR(50) DEFAULT 'pending_review'
            """))
        except Exception as e:
            print(f"  Column assignment_status may already exist: {e}")
        
        print("Adding new columns to assignments table...")
        try:
            conn.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN verified_by INTEGER
            """))
        except Exception as e:
            print(f"  Column verified_by may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN verified_at TIMESTAMP
            """))
        except Exception as e:
            print(f"  Column verified_at may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN deadline TIMESTAMP
            """))
        except Exception as e:
            print(f"  Column deadline may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN is_manual_override BOOLEAN DEFAULT FALSE
            """))
        except Exception as e:
            print(f"  Column is_manual_override may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN acknowledgement_required BOOLEAN DEFAULT TRUE
            """))
        except Exception as e:
            print(f"  Column acknowledgement_required may already exist: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN map_id INTEGER
            """))
        except Exception as e:
            print(f"  Column map_id may already exist: {e}")
    
    # 2. Create new tables using SQLAlchemy models
    print("Creating new tables...")
    Base.metadata.create_all(engine)
    
    # 3. Create indexes
    print("Creating indexes...")
    with engine.begin() as conn:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_requirements_assignment_status ON requirements(assignment_status)",
            "CREATE INDEX IF NOT EXISTS idx_assignments_dept_status ON assignments(department_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_assignments_status_verified ON assignments(status, verified_by)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_dept_ack ON notifications(department_id, is_acknowledged)",
            "CREATE INDEX IF NOT EXISTS idx_ai_suggestions_requirement ON ai_suggestions(requirement_id)",
            "CREATE INDEX IF NOT EXISTS idx_maps_requirement ON maps(requirement_id)",
        ]
        
        for idx_sql in indexes:
            try:
                conn.execute(text(idx_sql))
                print(f"  Created index: {idx_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"  Index may already exist: {e}")
    
    print("\nPhase 2 migration completed successfully!")
    print("All existing data preserved.")

if __name__ == "__main__":
    migrate_to_phase2()
```

### 10.2 Deployment Checklist

**Pre-Deployment:**
- [ ] Backup existing database: `cp data/compliance.db data/compliance_backup_$(date +%Y%m%d).db`
- [ ] Run tests: `pytest tests/`
- [ ] Review all code changes
- [ ] Update requirements.txt: `pip freeze > requirements.txt`
- [ ] Document new API endpoints

**Deployment Steps:**
1. Stop backend server
2. Activate virtual environment: `venv\Scripts\activate`
3. Install new dependencies: `pip install -r requirements.txt`
4. Run database migration: `python migrate_phase2.py`
5. Verify migration: Check new tables exist
6. Start backend server: `python run_backend.py`
7. Test Assignment Center: Login as admin, navigate to `/assignment-center`
8. Test Department Portal: Login as department user, check dashboard
9. Verify role-based access: Ensure departments can't access head office pages
10. Test status updates: Update assignment status, verify real-time sync

**Post-Deployment Verification:**
```bash
# Test backend endpoints
curl http://localhost:8000/api/health
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/assignment-center/pending

# Test frontend
# 1. Login as admin (admin/admin123)
# 2. Check Assignment Center loads
# 3. Login as department (compliance/compliance123)
# 4. Check Department Dashboard loads
# 5. Verify cannot access /pipeline or /assignment-center
```

### 10.3 Rollback Plan

If issues occur:

```bash
# 1. Stop backend
# 2. Restore database backup
cp data/compliance_backup_YYYYMMDD.db data/compliance.db

# 3. Revert code changes
git revert <commit-hash>

# 4. Restart backend with Phase 1 code
python run_backend.py
```

### 10.4 Configuration Management

**Environment Variables:**

```bash
# .env file (create if doesn't exist)

# Database
DATABASE_URL=sqlite:///./data/compliance.db

# JWT
JWT_SECRET_KEY=regintel_ai_offline_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480

# Phase 2 Settings
POLLING_INTERVAL_SECONDS=5
MAX_ASSIGNMENTS_PER_APPROVAL=100
ENABLE_PDF_EXPORT=false  # Set to true when PDF generation is ready

# Feature Flags
ENABLE_ASSIGNMENT_CENTER=true
ENABLE_DEPARTMENT_PORTAL=true
ENABLE_REAL_TIME_UPDATES=true
```

**Configuration Loading:**

```python
# backend/config.py (NEW FILE)

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/compliance.db"
    jwt_secret_key: str = "regintel_ai_offline_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480
    
    polling_interval_seconds: int = 5
    max_assignments_per_approval: int = 100
    enable_pdf_export: bool = False
    
    enable_assignment_center: bool = True
    enable_department_portal: bool = True
    enable_real_time_updates: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 10.5 Monitoring and Logging

**Enhanced Logging:**

```python
# backend/main.py - Add logging configuration

import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/backend.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log important events
@app.on_event("startup")
def on_startup():
    logger.info("RegIntel AI Backend Starting - Phase 2")
    logger.info(f"Assignment Center enabled: {settings.enable_assignment_center}")
    logger.info(f"Department Portal enabled: {settings.enable_department_portal}")
    # ... rest of startup code

# Log authentication events
@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt: {form_data.username}")
    # ... login logic
    logger.info(f"Login successful: {form_data.username}")

# Log assignment approvals
@router.post("/assignment-center/approve")
async def approve_assignments(request: AssignmentApproveRequest):
    logger.info(f"Assignment approval: {len(request.requirement_ids)} requirements by user {current_user.username}")
    # ... approval logic
    logger.info(f"Assignment approval completed: {len(assignments_created)} assignments created")
```

**Performance Monitoring:**

```python
# backend/middleware/performance.py (NEW FILE)

import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"with status {response.status_code}"
    )
    
    # Alert on slow requests
    if process_time > 3.0:
        logger.warning(f"Slow request detected: {request.url.path} took {process_time:.3f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 11. Testing Strategy

### 11.1 Unit Tests

**Test Assignment Approval:**

```python
# tests/test_assignment_center.py (NEW FILE)

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db, Base
from backend.models import User, Department, Requirement
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_approve_assignment(setup_database):
    """Test approving an AI-suggested assignment"""
    # Create test data
    db = TestingSessionLocal()
    
    # Create department
    dept = Department(name="Cyber Security", code="CYBER")
    db.add(dept)
    db.commit()
    
    # Create head office user
    admin = User(
        username="test_admin",
        hashed_password="hashed",
        role="head_office"
    )
    db.add(admin)
    db.commit()
    
    # Create requirement
    req = Requirement(
        requirement_id="TEST_001",
        text="Test requirement",
        document_id=1,
        assignment_status="pending_review",
        ai_suggested_department_id=dept.id,
        ai_confidence_score=95.0
    )
    db.add(req)
    db.commit()
    
    # Login and get token
    response = client.post("/api/auth/login", data={
        "username": "test_admin",
        "password": "admin123"
    })
    token = response.json()["access_token"]
    
    # Approve assignment
    response = client.post(
        "/api/assignment-center/approve",
        json={
            "requirement_ids": [req.id],
            "department_id": dept.id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["assignments_created"] == 1
    
    db.close()

def test_department_cannot_access_assignment_center(setup_database):
    """Test that department users cannot access Assignment Center"""
    # Create department user
    db = TestingSessionLocal()
    dept_user = User(
        username="test_dept",
        hashed_password="hashed",
        role="department",
        department_id=1
    )
    db.add(dept_user)
    db.commit()
    
    # Login as department user
    response = client.post("/api/auth/login", data={
        "username": "test_dept",
        "password": "dept123"
    })
    token = response.json()["access_token"]
    
    # Try to access Assignment Center
    response = client.get(
        "/api/assignment-center/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403  # Forbidden
    
    db.close()
```

### 11.2 Integration Tests

```python
# tests/test_workflow_integration.py (NEW FILE)

def test_complete_workflow():
    """Test the complete workflow from approval to verification"""
    
    # 1. Admin approves assignment
    # 2. Department receives notification
    # 3. Department updates status to in_progress
    # 4. Department completes task
    # 5. Admin verifies completion
    
    # ... test implementation
```

### 11.3 Frontend Tests

```javascript
// frontend/dashboard/src/__tests__/AssignmentCenter.test.jsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AssignmentCenter } from '../pages/AssignmentCenter';
import { AuthProvider } from '../context/AuthContext';

test('renders pending assignments', async () => {
  render(
    <AuthProvider>
      <AssignmentCenter />
    </AuthProvider>
  );
  
  await waitFor(() => {
    expect(screen.getByText(/Assignment Center/i)).toBeInTheDocument();
  });
});

test('approves assignment when approve button clicked', async () => {
  // ... test implementation
});
```

## 12. Documentation Requirements

### 12.1 API Documentation

All new endpoints must be documented in Swagger/OpenAPI:

```python
@router.post(
    "/approve",
    summary="Approve AI-suggested assignments",
    description="Head Office approves one or more AI-suggested department assignments",
    response_model=schemas.AssignmentApproveResponse,
    responses={
        200: {"description": "Assignments approved successfully"},
        403: {"description": "Access denied - Head Office only"},
        404: {"description": "Requirement not found"}
    }
)
async def approve_assignments(
    request: schemas.AssignmentApproveRequest,
    current_user: models.User = Depends(require_head_office),
    db: Session = Depends(get_db)
):
    """
    Approve AI-suggested assignments and publish them to departments.
    
    - **requirement_ids**: List of requirement IDs to approve (max 100)
    - **department_id**: Target department ID (can override AI suggestion)
    - **deadline**: Optional deadline for completion
    - **remarks**: Optional notes
    
    Creates assignment records and notifications for the department.
    """
    pass
```

### 12.2 User Documentation

Create the following guides:
- **ROLE_BASED_WORKFLOW.md**: Explains the workflow for each role
- **COMPLIANCE_LIFECYCLE.md**: Documents the complete compliance lifecycle
- **DEPARTMENT_PORTAL_GUIDE.md**: Guide for department users
- **EXECUTIVE_DASHBOARD_GUIDE.md**: Guide for head office users

### 12.3 README Update

```markdown
# RegIntel AI - Compliance Workflow Platform

## Phase 2: Compliance Workflow & Department Action Centers

### New Features
- ✅ Assignment Center for manual approval of AI suggestions
- ✅ Department-scoped portals with restricted access
- ✅ Task lifecycle management (Assigned → In Progress → Completed → Verified)
- ✅ Real-time updates via polling
- ✅ Complete audit trails
- ✅ Role-based access control

### Quick Start

**Start Backend:**
```bash
cd d:\SuRaksha
venv\Scripts\activate
python run_backend.py
```

**Start Frontend:**
```bash
cd frontend\dashboard
npm run dev
```

**Default Users:**
- Head Office: admin / admin123
- Departments: compliance / compliance123 (and other departments)

### New Pages
- `/assignment-center` - Review AI suggestions (Head Office only)
- `/department/dashboard` - Department dashboard (Department only)
- `/department/requirements` - Assigned requirements (Department only)
- `/department/graph` - Department knowledge graph (Department only)

### API Endpoints
See `/api/docs` for complete API documentation.
```

---

## Summary

This technical design provides:

1. **Complete system architecture** with clear separation of Head Office and Department concerns
2. **Database schema extensions** that preserve Phase 1 data
3. **Comprehensive API design** with role-based authorization
4. **Frontend component specifications** for all new pages
5. **Real-time update mechanism** via polling
6. **Security architecture** with proper access controls
7. **Performance optimization** strategies
8. **Integration plan** preserving existing Phase 1 and AI pipeline code
9. **Deployment strategy** with migration scripts and rollback plans
10. **Testing strategy** covering unit, integration, and frontend tests

All design decisions maintain:
- ✅ Phase 1 authentication and authorization
- ✅ Existing 42 AI pipeline scripts
- ✅ Offline architecture
- ✅ SQLite database
- ✅ FastAPI + React technology stack
- ✅ No breaking changes

**Next Step**: Generate task list from this design to begin implementation.

---

**Document Version**: 1.0  
**Created**: June 26, 2026  
**Status**: Ready for Task Generation
