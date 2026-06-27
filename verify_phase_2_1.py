#!/usr/bin/env python
"""
Phase 2.1 Verification Script
Tests Assignment Batch implementation and backward compatibility
"""

import sys
from sqlalchemy import create_engine, inspect
from pathlib import Path

def verify_database():
    """Verify database schema changes"""
    print("\n" + "="*60)
    print("DATABASE VERIFICATION")
    print("="*60)
    
    try:
        # Create engine
        db_path = Path(__file__).parent / "data" / "compliance.db"
        engine = create_engine(f"sqlite:///{db_path}")
        inspector = inspect(engine)
        
        # Check tables
        tables = inspector.get_table_names()
        print(f"\n✓ Total tables: {len(tables)}")
        
        # Check assignment_batches table
        if "assignment_batches" in tables:
            print("✓ assignment_batches table exists")
            
            # Check columns
            columns = [col['name'] for col in inspector.get_columns('assignment_batches')]
            expected_cols = [
                'id', 'batch_name', 'circular_name', 'uploaded_by', 
                'uploaded_at', 'status', 'total_requirements', 'total_maps',
                'completion_percentage', 'verification_percentage'
            ]
            
            missing_cols = set(expected_cols) - set(columns)
            if missing_cols:
                print(f"✗ Missing columns: {missing_cols}")
                return False
            else:
                print(f"✓ All columns present: {len(columns)}")
        else:
            print("✗ assignment_batches table NOT found")
            return False
        
        # Check batch_id columns
        for table in ['documents', 'requirements', 'assignments']:
            cols = [col['name'] for col in inspector.get_columns(table)]
            if 'batch_id' in cols:
                print(f"✓ {table}.batch_id exists")
            else:
                print(f"✗ {table}.batch_id NOT found")
                return False
        
        # Check indexes
        indexes = inspector.get_indexes('assignment_batches')
        print(f"✓ Indexes on assignment_batches: {len(indexes)}")
        
        print("\n✅ DATABASE VERIFICATION PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_backend_imports():
    """Verify backend imports work correctly"""
    print("\n" + "="*60)
    print("BACKEND IMPORTS VERIFICATION")
    print("="*60)
    
    try:
        # Import models
        from backend.models import AssignmentBatch, BatchStatus
        print("✓ AssignmentBatch model imported")
        print("✓ BatchStatus enum imported")
        
        # Check enum values
        statuses = [s.value for s in BatchStatus]
        expected = ['draft', 'pending_approval', 'published', 'in_progress', 'completed', 'closed']
        if statuses == expected:
            print(f"✓ BatchStatus has all 6 values: {statuses}")
        else:
            print(f"✗ BatchStatus mismatch. Expected: {expected}, Got: {statuses}")
            return False
        
        # Import schemas
        from backend.schemas import (
            AssignmentBatchCreate, 
            AssignmentBatchResponse, 
            AssignmentBatchSummary,
            AssignmentBatchStatusUpdate
        )
        print("✓ AssignmentBatch schemas imported")
        
        # Import CRUD
        from backend.crud import (
            create_assignment_batch,
            get_assignment_batch_by_id,
            get_all_assignment_batches,
            update_assignment_batch_status,
            update_assignment_batch_metrics
        )
        print("✓ AssignmentBatch CRUD functions imported")
        
        # Import router
        from backend.routers import assignment_batch_router
        print("✓ assignment_batch_router imported")
        
        print("\n✅ BACKEND IMPORTS VERIFICATION PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Backend imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_backward_compatibility():
    """Verify Phase 1 functionality still works"""
    print("\n" + "="*60)
    print("BACKWARD COMPATIBILITY VERIFICATION")
    print("="*60)
    
    try:
        # Import Phase 1 models
        from backend.models import User, Department, Document, Requirement, Assignment
        print("✓ Phase 1 models imported")
        
        # Import Phase 1 routers
        from backend.routers import auth_router, admin_router, department_router
        print("✓ Phase 1 routers imported")
        
        # Import Phase 1 CRUD
        from backend.crud import (
            get_user_by_username,
            get_all_departments,
            get_all_documents,
            get_all_requirements,
            get_all_assignments
        )
        print("✓ Phase 1 CRUD functions imported")
        
        print("\n✅ BACKWARD COMPATIBILITY VERIFICATION PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Backward compatibility check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verifications"""
    print("\n" + "="*60)
    print("PHASE 2.1 VERIFICATION SCRIPT")
    print("="*60)
    print("\nThis script verifies:")
    print("1. Database schema changes")
    print("2. Backend imports (models, schemas, CRUD)")
    print("3. Backward compatibility with Phase 1")
    
    results = []
    
    # Run verifications
    results.append(("Database Schema", verify_database()))
    results.append(("Backend Imports", verify_backend_imports()))
    results.append(("Backward Compatibility", verify_backward_compatibility()))
    
    # Print summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    # Overall result
    all_passed = all(result[1] for result in results)
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED")
        print("="*60)
        print("\nPhase 2.1 is ready for testing!")
        print("\nNext steps:")
        print("1. Start backend: python run_backend.py")
        print("2. Open API docs: http://localhost:8000/api/docs")
        print("3. Test batch endpoints")
        print("4. Verify Phase 1 endpoints still work")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("="*60)
        print("\nPlease check the errors above and fix issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
