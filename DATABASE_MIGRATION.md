# Database Migration - Phase 2.1

## Overview

This migration adds Assignment Batch support to the RegIntel AI Compliance Backend.

**Migration ID**: 002_add_assignment_batches  
**Date**: 2026-06-27  
**Phase**: 2.1 - Assignment Batch Foundation

---

## Changes Summary

### New Tables

#### 1. `assignment_batches`

Central workflow object representing a compliance campaign from a single RBI circular.

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

CREATE INDEX idx_assignment_batches_status ON assignment_batches(status);
CREATE INDEX idx_assignment_batches_uploaded_by ON assignment_batches(uploaded_by);
```

**Status Values**:
- `draft` - Initial state after upload
- `pending_approval` - AI processing complete, awaiting Head Office review
- `published` - Approved and visible to departments
- `in_progress` - Departments executing
- `completed` - All MAPs completed
- `closed` - Archived, no further changes

### Modified Tables

#### 1. `documents` - Added `batch_id`

```sql
ALTER TABLE documents ADD COLUMN batch_id INTEGER;
CREATE INDEX idx_documents_batch ON documents(batch_id);
ALTER TABLE documents ADD CONSTRAINT fk_documents_batch 
    FOREIGN KEY (batch_id) REFERENCES assignment_batches(id);
```

**Purpose**: Link uploaded documents to their batch.

#### 2. `requirements` - Added `batch_id`

```sql
ALTER TABLE requirements ADD COLUMN batch_id INTEGER;
CREATE INDEX idx_requirements_batch ON requirements(batch_id);
ALTER TABLE requirements ADD CONSTRAINT fk_requirements_batch 
    FOREIGN KEY (batch_id) REFERENCES assignment_batches(id);
```

**Purpose**: Link extracted requirements to their batch.

#### 3. `assignments` - Added `batch_id`

```sql
ALTER TABLE assignments ADD COLUMN batch_id INTEGER;
CREATE INDEX idx_assignments_batch ON assignments(batch_id);
ALTER TABLE assignments ADD CONSTRAINT fk_assignments_batch 
    FOREIGN KEY (batch_id) REFERENCES assignment_batches(id);
```

**Purpose**: Link MAP assignments to their batch.

---

## Migration Script

### SQLite Migration (Automatic via SQLAlchemy)

The migration is handled automatically by SQLAlchemy ORM when the application starts:

```python
# Backend startup (backend/main.py)
Base.metadata.create_all(bind=engine)
```

SQLAlchemy will:
1. Detect new `assignment_batches` table and create it
2. Detect new `batch_id` columns and add them to existing tables
3. Create all foreign key relationships
4. Create all indexes

### Manual Migration (If Needed)

If you need to run migration manually:

```bash
# Using Python interpreter
python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

---

## Backward Compatibility

### Existing Data

**All existing data remains intact.**

New columns (`batch_id`) are nullable, so existing records will have `NULL` values:
- Existing documents: `batch_id = NULL`
- Existing requirements: `batch_id = NULL`
- Existing assignments: `batch_id = NULL`

### Legacy Data Batch (Optional)

To organize existing data, you can create a "Legacy Data Batch":

```python
# Run after migration
from backend.database import get_db
from backend.models import AssignmentBatch, Document, Requirement, Assignment

db = next(get_db())

# Create legacy batch
legacy_batch = AssignmentBatch(
    batch_name="Legacy Data Batch",
    circular_name="LEGACY/2024/00",
    uploaded_by=1,  # admin user
    status="published"
)
db.add(legacy_batch)
db.commit()

# Update existing records
db.execute("UPDATE documents SET batch_id = :id WHERE batch_id IS NULL", {"id": legacy_batch.id})
db.execute("UPDATE requirements SET batch_id = :id WHERE batch_id IS NULL", {"id": legacy_batch.id})
db.execute("UPDATE assignments SET batch_id = :id WHERE batch_id IS NULL", {"id": legacy_batch.id})
db.commit()

# Update metrics
from backend import crud
crud.update_assignment_batch_metrics(db, legacy_batch.id)
```

---

## Verification Steps

### 1. Verify Table Creation

```sql
-- Check assignment_batches table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='assignment_batches';

-- Verify columns
PRAGMA table_info(assignment_batches);
```

### 2. Verify Column Additions

```sql
-- Check documents.batch_id
PRAGMA table_info(documents);

-- Check requirements.batch_id
PRAGMA table_info(requirements);

-- Check assignments.batch_id
PRAGMA table_info(assignments);
```

### 3. Verify Indexes

```sql
-- List all indexes
SELECT name, tbl_name FROM sqlite_master WHERE type='index';
```

Expected indexes:
- `idx_assignment_batches_status`
- `idx_assignment_batches_uploaded_by`
- `idx_documents_batch`
- `idx_requirements_batch`
- `idx_assignments_batch`

### 4. Verify Foreign Keys

```sql
-- Check foreign keys
PRAGMA foreign_key_list(assignment_batches);
PRAGMA foreign_key_list(documents);
PRAGMA foreign_key_list(requirements);
PRAGMA foreign_key_list(assignments);
```

---

## Rollback Plan

### Option 1: Drop Columns (SQLite Limitation)

SQLite does not support `ALTER TABLE DROP COLUMN` natively. To rollback:

1. Create backup: `cp data/compliance.db data/compliance.db.backup`
2. Export data: Use SQLite `.dump` command
3. Drop tables: `DROP TABLE assignment_batches;`
4. Remove references from code
5. Restart application

### Option 2: Database Restore

1. Stop backend application
2. Restore from backup: `cp data/compliance.db.backup data/compliance.db`
3. Revert code to Phase 1
4. Restart application

---

## Testing

### Test Migration Success

```bash
# Start backend
cd backend
python -m backend.main

# Check logs for successful table creation
# Should see: "✓ Creating database tables..."
```

### Test API Endpoints

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Save token
TOKEN="<access_token_from_login>"

# Test batch endpoints
curl -X GET http://localhost:8000/api/assignment-batches \
  -H "Authorization: Bearer $TOKEN"

# Create batch
curl -X POST http://localhost:8000/api/assignment-batches/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch_name":"Test Batch","circular_name":"RBI/2024/TEST"}'
```

---

## Performance Impact

### Database Size

- New table: ~50 bytes per batch record
- New columns: ~4 bytes per existing record (batch_id as INTEGER)
- Indexes: ~50-100 bytes per index entry

**Estimated Impact**: Negligible for typical workloads (<100 batches).

### Query Performance

New indexes improve query performance:
- Filtering batches by status: O(log n) with index
- Finding documents/requirements/assignments by batch: O(log n) with index

**Expected Impact**: Improved performance for batch-related queries.

---

## Notes

1. **NULL Values**: Existing records will have `batch_id = NULL`. This is intentional and maintains backward compatibility.

2. **No Breaking Changes**: All existing API endpoints continue to work exactly as before.

3. **Gradual Migration**: New batches will use batch_id linking. Old data can remain NULL or be migrated to a legacy batch.

4. **Future-Proof**: Schema supports all Phase 2.2+ features (notifications, evidence, verification).

---

## Support

If you encounter issues during migration:

1. Check backend logs for detailed error messages
2. Verify SQLite version: `sqlite3 --version` (requires 3.7.0+)
3. Verify database file permissions
4. Ensure no other processes are accessing the database
5. Try manual migration script if automatic fails

---

**Migration Status**: ✅ Ready for Production

