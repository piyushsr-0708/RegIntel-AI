# Phase 2.1 Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide helps you quickly test the new Assignment Batch functionality.

---

## Prerequisites

✅ Phase 1 backend running  
✅ Python dependencies installed  
✅ Default credentials available

---

## Step 1: Verify Installation (30 seconds)

Run the automated verification script:

```bash
python verify_phase_2_1.py
```

**Expected Output**:
```
============================================================
PHASE 2.1 VERIFICATION SCRIPT
============================================================

DATABASE VERIFICATION
============================================================
✓ Total tables: 8
✓ assignment_batches table exists
✓ All columns present: 10
✓ documents.batch_id exists
✓ requirements.batch_id exists
✓ assignments.batch_id exists
✓ Indexes on assignment_batches: 2

✅ DATABASE VERIFICATION PASSED

BACKEND IMPORTS VERIFICATION
============================================================
✓ AssignmentBatch model imported
✓ BatchStatus enum imported
✓ BatchStatus has all 6 values
✓ AssignmentBatch schemas imported
✓ AssignmentBatch CRUD functions imported
✓ assignment_batch_router imported

✅ BACKEND IMPORTS VERIFICATION PASSED

BACKWARD COMPATIBILITY VERIFICATION
============================================================
✓ Phase 1 models imported
✓ Phase 1 routers imported
✓ Phase 1 CRUD functions imported

✅ BACKWARD COMPATIBILITY VERIFICATION PASSED

VERIFICATION SUMMARY
============================================================
Database Schema: ✅ PASS
Backend Imports: ✅ PASS
Backward Compatibility: ✅ PASS

============================================================
✅ ALL VERIFICATIONS PASSED
============================================================
```

---

## Step 2: Start Backend (10 seconds)

```bash
python run_backend.py
```

**Expected Output**:
```
============================================================
REGINTEL AI - COMPLIANCE BACKEND STARTING
============================================================

✓ Creating database tables...
✓ Database seeding completed successfully

✓ Backend is ready!
✓ API Documentation: http://localhost:8000/api/docs
============================================================
```

---

## Step 3: Test API (2 minutes)

### 3.1 Login as HEAD_OFFICE

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Save the token** from the response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "token_type": "bearer"
}
```

### 3.2 Create an Assignment Batch

```bash
# Replace <TOKEN> with your actual token
curl -X POST http://localhost:8000/api/assignment-batches/create \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_name": "RBI Cyber Security Directive 2024",
    "circular_name": "RBI/2024/01/CS"
  }'
```

**Expected Response**:
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security Directive 2024",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00.123456",
  "status": "draft",
  "total_requirements": 0,
  "total_maps": 0,
  "completion_percentage": 0,
  "verification_percentage": 0
}
```

### 3.3 Get All Batches

```bash
curl -X GET http://localhost:8000/api/assignment-batches \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected**: Array with your created batch.

### 3.4 Get Batch Summary

```bash
# Replace {batch_id} with the ID from step 3.2 (e.g., 1)
curl -X GET http://localhost:8000/api/assignment-batches/1/summary \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected Response**:
```json
{
  "id": 1,
  "batch_name": "RBI Cyber Security Directive 2024",
  "circular_name": "RBI/2024/01/CS",
  "uploaded_by": 1,
  "uploaded_at": "2024-06-27T10:00:00.123456",
  "status": "draft",
  "total_requirements": 0,
  "total_maps": 0,
  "completion_percentage": 0,
  "verification_percentage": 0,
  "department_distribution": {},
  "priority_distribution": {},
  "uploader_name": "System Administrator"
}
```

### 3.5 Update Batch Status

```bash
curl -X PATCH http://localhost:8000/api/assignment-batches/1/status \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'
```

**Expected**: Batch with status changed to "published".

### 3.6 Verify Backward Compatibility

Test that Phase 1 endpoints still work:

```bash
# Dashboard should work
curl -X GET http://localhost:8000/api/admin/dashboard \
  -H "Authorization: Bearer <TOKEN>"

# Documents endpoint should work
curl -X GET http://localhost:8000/api/admin/documents \
  -H "Authorization: Bearer <TOKEN>"

# Requirements endpoint should work
curl -X GET http://localhost:8000/api/admin/requirements \
  -H "Authorization: Bearer <TOKEN>"
```

**Expected**: All return valid responses (may be empty arrays if no data).

---

## Step 4: Explore Interactive Docs (1 minute)

Open your browser:

```
http://localhost:8000/api/docs
```

### What to Look For

1. **"Assignment Batches" Tag**: Should be visible in the sidebar
2. **6 New Endpoints**: All batch endpoints listed
3. **Try It Out**: Click "Try it out" on any endpoint
4. **Authenticate**: Click "Authorize" button, paste your token
5. **Test**: Execute requests directly from the browser

---

## Step 5: Test Role-Based Access (1 minute)

### Login as Department User

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"compliance","password":"compliance123"}'
```

**Save the DEPARTMENT token**.

### Try to Access Batch Endpoint

```bash
# This should FAIL with 403 Forbidden
curl -X GET http://localhost:8000/api/assignment-batches \
  -H "Authorization: Bearer <DEPARTMENT_TOKEN>"
```

**Expected Response**:
```json
{
  "detail": "Insufficient permissions. HEAD_OFFICE role required."
}
```

✅ This confirms role-based access control is working!

---

## Common Issues

### Issue: "Module not found"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "Database locked"

**Cause**: Another process is using the database

**Solution**:
```bash
# Stop all Python processes
# Restart backend
python run_backend.py
```

### Issue: "401 Unauthorized"

**Cause**: Token expired or invalid

**Solution**:
```bash
# Login again to get a fresh token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Issue: "Table assignment_batches does not exist"

**Cause**: Database migration didn't run

**Solution**:
```bash
# Stop backend
# Delete old database
rm data/compliance.db
# Restart backend (will recreate with new schema)
python run_backend.py
```

---

## Next Steps

### Explore the API

- Try creating multiple batches
- Test status transitions
- Refresh metrics
- View batch distributions

### Read Documentation

- **Full Implementation Report**: `PHASE_2_1_IMPLEMENTATION_REPORT.md`
- **API Reference**: `API_CHANGELOG.md`
- **Database Details**: `DATABASE_MIGRATION.md`
- **Test Guide**: `TEST_REPORT.md`

### Prepare for Phase 2.2

Phase 2.2 will add:
- Frontend Assignment Batch page
- Department Dashboard redesign
- Notification system
- Evidence upload
- Verification workflow

---

## Quick Reference

### Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/assignment-batches/create` | Create batch |
| GET | `/api/assignment-batches` | List batches |
| GET | `/api/assignment-batches/{id}` | Get batch |
| GET | `/api/assignment-batches/{id}/summary` | Get summary |
| PATCH | `/api/assignment-batches/{id}/status` | Update status |
| POST | `/api/assignment-batches/{id}/refresh-metrics` | Refresh metrics |

### Status Values

- `draft` - Initial state
- `pending_approval` - Awaiting approval
- `published` - Approved
- `in_progress` - Being executed
- `completed` - All MAPs done
- `closed` - Archived

### Authentication

**HEAD_OFFICE**: Can access all batch endpoints  
**DEPARTMENT**: Cannot access batch endpoints (403 Forbidden)

---

## Success Criteria

You've successfully completed the quick start if:

✅ Verification script passes all checks  
✅ Backend starts without errors  
✅ You can create a batch  
✅ You can retrieve batches  
✅ You can update batch status  
✅ Phase 1 endpoints still work  
✅ DEPARTMENT users get 403 on batch endpoints  
✅ Swagger docs show new endpoints  

---

## Help & Support

### Documentation

- `README.md` - Updated with Phase 2.1 info
- `PHASE_2_1_IMPLEMENTATION_REPORT.md` - Complete implementation details
- `API_CHANGELOG.md` - API reference
- http://localhost:8000/api/docs - Interactive API docs

### Troubleshooting

1. Check backend logs for detailed errors
2. Verify database file exists: `data/compliance.db`
3. Confirm Python version: `python --version` (3.8+)
4. Check dependencies: `pip list | grep fastapi`

---

**Time to Complete**: ~5 minutes  
**Difficulty**: Easy  
**Status**: ✅ Ready to Use

Happy testing! 🚀
