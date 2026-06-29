"""
Clean test data and reset database to clean state
Preserves departments and admin user, removes all documents/requirements/assignments
"""
import sqlite3
from pathlib import Path

def clean_database():
    db_path = Path("data/compliance.db")
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path.absolute()}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("=" * 80)
    print("CLEANING TEST DATA")
    print("=" * 80)
    
    # Check current counts
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requirements")
    req_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assignments")
    assign_count = cursor.fetchone()[0]
    
    print(f"\nCurrent state:")
    print(f"  Documents: {doc_count}")
    print(f"  Requirements: {req_count}")
    print(f"  Assignments: {assign_count}")
    
    # Delete all test data
    print(f"\nDeleting test data...")
    
    cursor.execute("DELETE FROM assignments")
    deleted_assigns = cursor.rowcount
    print(f"  ✓ Deleted {deleted_assigns} assignments")
    
    cursor.execute("DELETE FROM requirements")
    deleted_reqs = cursor.rowcount
    print(f"  ✓ Deleted {deleted_reqs} requirements")
    
    cursor.execute("DELETE FROM documents")
    deleted_docs = cursor.rowcount
    print(f"  ✓ Deleted {deleted_docs} documents")
    
    cursor.execute("DELETE FROM audit_logs WHERE entity_type IN ('document', 'requirement', 'assignment')")
    deleted_logs = cursor.rowcount
    print(f"  ✓ Deleted {deleted_logs} audit logs")
    
    # Reset autoincrement (skip if table doesn't exist)
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('documents', 'requirements', 'assignments')")
        print(f"  ✓ Reset autoincrement counters")
    except sqlite3.OperationalError:
        print(f"  ⚠️  Skipping autoincrement reset (table not found)")
    
    conn.commit()
    
    # Verify clean state
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requirements")
    req_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assignments")
    assign_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    print(f"\nClean state:")
    print(f"  Documents: {doc_count}")
    print(f"  Requirements: {req_count}")
    print(f"  Assignments: {assign_count}")
    print(f"  Departments: {dept_count} (preserved)")
    print(f"  Users: {user_count} (preserved)")
    
    print("\n" + "=" * 80)
    print("✅ DATABASE CLEANED SUCCESSFULLY")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    clean_database()
