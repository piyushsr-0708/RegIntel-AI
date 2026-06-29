"""
Diagnostic SQL queries for document_id=22 investigation
Run this script to collect evidence about why document_id=22 returns empty arrays
"""
from database import SessionLocal
from sqlalchemy import text

def run_diagnostics():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("DIAGNOSTIC SQL QUERIES FOR DOCUMENT_ID=22")
        print("=" * 80)
        
        # Query 1: Get document details
        print("\n[QUERY 1] Document details for id=22:")
        print("-" * 80)
        result = db.execute(text("SELECT id, original_filename FROM documents WHERE id = 22"))
        row = result.fetchone()
        if row:
            print(f"  id: {row[0]}")
            print(f"  original_filename: {row[1]}")
        else:
            print("  ⚠️  No document found with id=22")
        
        # Query 2: Count requirements for document_id=22
        print("\n[QUERY 2] Count of requirements for document_id=22:")
        print("-" * 80)
        result = db.execute(text("SELECT COUNT(*) FROM requirements WHERE document_id = 22"))
        count = result.fetchone()[0]
        print(f"  Total requirements: {count}")
        
        # Query 3: All requirements ordered by requirement_id
        print("\n[QUERY 3] All requirements ordered by requirement_id:")
        print("-" * 80)
        result = db.execute(text("SELECT requirement_id, document_id FROM requirements ORDER BY requirement_id"))
        rows = result.fetchall()
        print(f"  Total requirements in database: {len(rows)}")
        if rows:
            print("\n  requirement_id                    | document_id")
            print("  " + "-" * 50)
            for row in rows:
                print(f"  {row[0]:<35} | {row[1]}")
        else:
            print("  ⚠️  No requirements found in database")
        
        # Query 4: Check for duplicate requirement_id patterns
        print("\n[QUERY 4] Requirements grouped by filename prefix:")
        print("-" * 80)
        result = db.execute(text("""
            SELECT 
                SUBSTR(requirement_id, 1, 14) as prefix,
                COUNT(*) as count,
                GROUP_CONCAT(DISTINCT document_id) as document_ids
            FROM requirements 
            GROUP BY SUBSTR(requirement_id, 1, 14)
            ORDER BY prefix
        """))
        rows = result.fetchall()
        if rows:
            print(f"  Found {len(rows)} unique prefixes:")
            print("\n  prefix             | count | document_ids")
            print("  " + "-" * 60)
            for row in rows:
                print(f"  {row[0]:<18} | {row[1]:<5} | {row[2]}")
        else:
            print("  ⚠️  No requirements found")
        
        # Query 5: All documents
        print("\n[QUERY 5] All documents in database:")
        print("-" * 80)
        result = db.execute(text("SELECT id, original_filename, processed FROM documents ORDER BY id"))
        rows = result.fetchall()
        if rows:
            print(f"  Total documents: {len(rows)}")
            print("\n  id  | original_filename                        | processed")
            print("  " + "-" * 70)
            for row in rows:
                print(f"  {row[0]:<3} | {row[1]:<40} | {row[2]}")
        else:
            print("  ⚠️  No documents found")
        
        # Query 6: Assignments count
        print("\n[QUERY 6] Assignments analysis:")
        print("-" * 80)
        result = db.execute(text("""
            SELECT 
                r.document_id,
                COUNT(a.id) as assignment_count
            FROM requirements r
            LEFT JOIN assignments a ON a.requirement_id = r.id
            GROUP BY r.document_id
            ORDER BY r.document_id
        """))
        rows = result.fetchall()
        if rows:
            print("  document_id | assignment_count")
            print("  " + "-" * 35)
            for row in rows:
                print(f"  {row[0]:<11} | {row[1]}")
        else:
            print("  ⚠️  No assignments found")
        
        print("\n" + "=" * 80)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error executing diagnostic queries: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_diagnostics()
