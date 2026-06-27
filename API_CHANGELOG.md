# API Changelog - Phase 2.1

## Overview

This document describes all API changes introduced in Phase 2.1 - Assignment Batch Foundation.

**Version**: 2.1.0  
**Date**: 2026-06-27  
**Backward Compatible**: ✅ Yes

---

## New Endpoints

### Assignment Batch Management

All new endpoints require `HEAD_OFFICE` role and JWT authentication.

#### 1. Create Assignment Batch

```
POST /api/assignment-batches/create
```

**Description**: Create a new Assignment Batch (Compliance Campaign).

**Authentication**: Required (HEAD_OFFICE only)

**Request Body**:
```json
{
  "batch_name": "RBI Cyber Security 2024-01",
  "circular_name": "RBI/2024/01/CS"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security 2024-01",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00Z",
  "status": "draft",
  "total_requirements": 0,
  "total_maps": 0,
  "completion_percentage": 0,
  "verification_percentage": 0
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User does not have HEAD_OFFICE role
- `422 Unprocessable Entity`: Validation error (missing required fields)

---

#### 2. Get All Assignment Batches

```
GET /api/assignment-batches?skip=0&limit=100
```

**Description**: Retrieve all Assignment Batches, ordered by most recent first.

**Authentication**: Required (HEAD_OFFICE only)

**Query Parameters**:
- `skip` (optional, default: 0): Number of records to skip for pagination
- `limit` (optional, default: 100): Maximum number of records to return

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "batch_name": "RBI Cyber Security 2024-01",
    "circular_name": "RBI/2024/01/CS",
    "uploaded_by": 1,
    "uploaded_at": "2024-06-27T10:00:00Z",
    "status": "published",
    "total_requirements": 45,
    "total_maps": 67,
    "completion_percentage": 32,
    "verification_percentage": 12
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User does not have HEAD_OFFICE role

---

#### 3. Get Assignment Batch by ID

```
GET /api/assignment-batches/{batch_id}
```

**Description**: Retrieve a specific Assignment Batch by its ID.

**Authentication**: Required (HEAD_OFFICE only)

**Path Parameters**:
- `batch_id` (required): ID of the batch to retrieve

**Response** (200 OK):
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security 2024-01",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00Z",
  "status": "published",
  "total_requirements": 45,
  "total_maps": 67,
  "completion_percentage": 32,
  "verification_percentage": 12
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User does not have HEAD_OFFICE role
- `404 Not Found`: Batch with specified ID does not exist

---

#### 4. Get Assignment Batch Summary

```
GET /api/assignment-batches/{batch_id}/summary
```

**Description**: Retrieve Assignment Batch with additional distribution data.

**Authentication**: Required (HEAD_OFFICE only)

**Path Parameters**:
- `batch_id` (required): ID of the batch to retrieve

**Response** (200 OK):
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security 2024-01",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00Z",
  "status": "published",
  "total_requirements": 45,
  "total_maps": 67,
  "completion_percentage": 32,
  "verification_percentage": 12,
  "department_distribution": {
    "Compliance": 18,
    "Cyber Security": 12,
    "IT": 8,
    "Risk Management": 15,
    "Treasury": 14
  },
  "priority_distribution": {
    "high": 22,
    "medium": 35,
    "low": 10
  },
  "uploader_name": "System Administrator"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User does not have HEAD_OFFICE role
- `404 Not Found`: Batch with specified ID does not exist

---

#### 5. Update Assignment Batch Status

```
PATCH /api/assignment-batches/{batch_id}/status
```

**Description**: Update the status of an Assignment Batch.

**Authentication**: Required (HEAD_OFFICE only)

**Path Parameters**:
- `batch_id` (required): ID of the batch to update

**Request Body**:
```json
{
  "status": "published"
}
```

**Valid Status Values**:
- `draft` - Initial state after creation
- `pending_approval` - AI processing complete, awaiting approval
- `published` - Approved and visible to departments
- `in_progress` - Departments executing
- `completed` - All MAPs completed
- `closed` - Archived

**Response** (200 OK):
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security 2024-01",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00Z",
  "status": "published",
  "total_requirements": 45,
  "total_maps": 67,
  "completion_percentage": 32,
  "verification_percentage": 12
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User does not have HEAD_OFFICE role
- `404 Not Found`: Batch with specified ID does not exist
- `422 Unprocessable Entity`: Invalid status value

---

#### 6. Refresh Batch Metrics

```
POST /api/assignment-batches/{batch_id}/refresh-metrics
```

**Description**: Recalculate and update batch metrics (requirements, MAPs, completion percentages).

**Authentication**: Required (HEAD_OFFICE only)

**Path Parameters**:
- `batch_id` (required): ID of the batch to refresh

**Response** (200 OK):
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security 2024-01",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00Z",
  "status": "published",
  "total_requirements": 45,
  "total_maps": 67,
  "completion_percentage": 32,
  "verification_percentage": 12
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User does not have HEAD_OFFICE role
- `404 Not Found`: Batch with specified ID does not exist

---

## Modified Endpoints

### None

All existing Phase 1 endpoints remain unchanged and fully functional.

---

## New Data Models

### AssignmentBatchResponse

```typescript
interface AssignmentBatchResponse {
  id: number;
  batch_name: string;
  circular_name: string;
  uploaded_by: number;
  uploaded_at: string; // ISO 8601 datetime
  status: "draft" | "pending_approval" | "published" | "in_progress" | "completed" | "closed";
  total_requirements: number;
  total_maps: number;
  completion_percentage: number; // 0-100
  verification_percentage: number; // 0-100
}
```

### AssignmentBatchSummary

Extends `AssignmentBatchResponse` with:

```typescript
interface AssignmentBatchSummary extends AssignmentBatchResponse {
  department_distribution: Record<string, number>; // dept_name -> count
  priority_distribution: Record<string, number>; // priority -> count
  uploader_name: string;
}
```

### AssignmentBatchCreate

```typescript
interface AssignmentBatchCreate {
  batch_name: string; // Required, max 200 chars
  circular_name: string; // Required, max 200 chars
}
```

### AssignmentBatchStatusUpdate

```typescript
interface AssignmentBatchStatusUpdate {
  status: "draft" | "pending_approval" | "published" | "in_progress" | "completed" | "closed";
}
```

---

## Database Schema Changes

### New Table: `assignment_batches`

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
    completion_percentage INTEGER DEFAULT 0,
    verification_percentage INTEGER DEFAULT 0,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);
```

### Modified Tables

#### `documents` table
- **Added**: `batch_id INTEGER` (nullable, references `assignment_batches.id`)

#### `requirements` table
- **Added**: `batch_id INTEGER` (nullable, references `assignment_batches.id`)

#### `assignments` table
- **Added**: `batch_id INTEGER` (nullable, references `assignment_batches.id`)

---

## Backward Compatibility

✅ **100% Backward Compatible**

All Phase 1 endpoints continue to work exactly as before:

### Unchanged Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

#### Admin (HEAD_OFFICE)
- `GET /api/admin/dashboard` - Dashboard summary
- `POST /api/admin/upload` - Upload document
- `GET /api/admin/documents` - Get all documents
- `GET /api/admin/requirements` - Get all requirements
- `GET /api/admin/requirements/unassigned` - Get unassigned requirements
- `POST /api/admin/assignments` - Create assignment
- `POST /api/admin/assignments/bulk` - Bulk assign
- `GET /api/admin/assignments` - Get all assignments
- `GET /api/admin/departments` - Get departments
- `GET /api/admin/audit-logs` - Get audit logs

#### Department
- `GET /api/departments/dashboard` - Department dashboard
- `GET /api/departments/assignments` - Get department assignments
- `PATCH /api/departments/assignments/{id}/status` - Update assignment status

### Data Compatibility

- Existing documents, requirements, and assignments have `batch_id = NULL`
- All existing data remains accessible through Phase 1 endpoints
- No data migration required for Phase 2.1

---

## Authentication & Authorization

### JWT Token

All new endpoints require JWT authentication via Bearer token:

```
Authorization: Bearer <jwt_token>
```

### Role-Based Access Control

| Endpoint | HEAD_OFFICE | DEPARTMENT |
|----------|-------------|------------|
| `POST /api/assignment-batches/create` | ✅ | ❌ (403) |
| `GET /api/assignment-batches` | ✅ | ❌ (403) |
| `GET /api/assignment-batches/{id}` | ✅ | ❌ (403) |
| `GET /api/assignment-batches/{id}/summary` | ✅ | ❌ (403) |
| `PATCH /api/assignment-batches/{id}/status` | ✅ | ❌ (403) |
| `POST /api/assignment-batches/{id}/refresh-metrics` | ✅ | ❌ (403) |

---

## Error Handling

### Standard Error Format

All errors return JSON with:

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK` - Successful operation
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Insufficient permissions (wrong role)
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error (invalid input)
- `500 Internal Server Error` - Server error (rare)

---

## API Documentation

### Swagger UI

Interactive API documentation available at:

```
http://localhost:8000/api/docs
```

Features:
- Try endpoints directly from browser
- View request/response schemas
- Test authentication
- See all available endpoints

### ReDoc

Alternative documentation format:

```
http://localhost:8000/api/redoc
```

---

## Usage Examples

### Complete Workflow Example

```bash
# 1. Login as HEAD_OFFICE
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Create Assignment Batch
BATCH=$(curl -s -X POST http://localhost:8000/api/assignment-batches/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_name": "RBI Cyber Security Directive 2024",
    "circular_name": "RBI/2024/01/CS"
  }')

echo $BATCH | python -m json.tool

# Extract batch ID
BATCH_ID=$(echo $BATCH | python -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 3. Upload circular (existing endpoint, now can link to batch)
# (Document upload modification will be in Phase 2.2)

# 4. Get batch summary
curl -s -X GET "http://localhost:8000/api/assignment-batches/$BATCH_ID/summary" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# 5. Update batch status
curl -s -X PATCH "http://localhost:8000/api/assignment-batches/$BATCH_ID/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}' | python -m json.tool

# 6. Refresh metrics
curl -s -X POST "http://localhost:8000/api/assignment-batches/$BATCH_ID/refresh-metrics" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# 7. Get all batches
curl -s -X GET "http://localhost:8000/api/assignment-batches" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

---

## Migration Guide

### For Frontend Developers

No changes required for existing Phase 1 functionality. To add Assignment Batch support:

1. **Add Batch List Page** (HEAD_OFFICE only):
```typescript
// Fetch batches
const response = await api.get('/api/assignment-batches', {
  headers: { Authorization: `Bearer ${token}` }
});
const batches = response.data;
```

2. **Add Batch Detail Page** (HEAD_OFFICE only):
```typescript
// Fetch batch details
const batch = await api.get(`/api/assignment-batches/${batchId}/summary`, {
  headers: { Authorization: `Bearer ${token}` }
});
```

3. **Add Batch Creation**:
```typescript
// Create batch
const newBatch = await api.post('/api/assignment-batches/create', {
  batch_name: 'RBI Cyber Security 2024',
  circular_name: 'RBI/2024/01/CS'
}, {
  headers: { Authorization: `Bearer ${token}` }
});
```

### For Backend Developers

No changes required. All existing CRUD operations work as before.

---

## Version History

### v2.1.0 (2026-06-27)

**Added**:
- Assignment Batch endpoints (6 new endpoints)
- Assignment Batch models and schemas
- Database schema extensions (batch_id columns)
- Role-based access control for batch endpoints

**Changed**:
- None

**Deprecated**:
- None

**Removed**:
- None

**Fixed**:
- None

---

## Support & Feedback

For issues or questions:
1. Check Swagger docs: http://localhost:8000/api/docs
2. Review TEST_REPORT.md for test results
3. Review DATABASE_MIGRATION.md for schema details
4. Check backend logs for detailed error messages

---

**API Version**: 2.1.0  
**Status**: ✅ Production Ready  
**Backward Compatible**: ✅ Yes

