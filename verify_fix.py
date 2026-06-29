"""
Verification script for duplicate requirement fix
Tests that documents with same filename create separate requirements
"""
import sqlite3
from pathlib import Path

def verify_fix():
    db_path = Path("data/compliance.db")
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path.absolute()}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 100)
    print("POST-FIX VERIFICATION REPORT")
    print("=" * 100)
    
    # Get all documents
    cursor.execute("SELECT id, original_filename, processed FROM documents ORDER BY id")
    documents = cursor.fetchall()
    
    if not documents:
        print("\n⚠️  No documents found. Please upload a circular to verify the fix.")
        conn.close()
        return False
    
    print(f"\n[DOCUMENTS] Total: {len(documents)}")
    print("-" * 100)
    
    all_passed = True
    
    for doc in documents:
        doc_id = doc['id']
        filename = doc['original_filename']
        processed = doc['processed']
        
        # Get requirements for this document
        cursor.execute("SELECT COUNT(*) as count FROM requirements WHERE document_id = ?", (doc_id,))
        req_count = cursor.fetchone()['count']
        
        # Get assignments for this document
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM assignments a
            JOIN requirements r ON a.requirement_id = r.id
            WHERE r.document_id = ?
        """, (doc_id,))
        assign_count = cursor.fetchone()['count']
        
        # Get requirement_ids for this document
        cursor.execute("SELECT requirement_id FROM requirements WHERE document_id = ? ORDER BY requirement_id", (doc_id,))
        req_ids = [row['requirement_id'] for row in cursor.fetchall()]
        
        # Check for expected pattern
        expected_pattern = f"REQ_DOC{doc_id}_"
        pattern_match = all(req_id.startswith(expected_pattern) for req_id in req_ids) if req_ids else True
        
        status = "✅ PASS" if (req_count > 0 and assign_count > 0 and pattern_match) else "❌ FAIL"
        if req_count == 0 or assign_count == 0:
            all_passed = False
        
        print(f"\n{status} Document ID {doc_id}")
        print(f"  Filename: {filename}")
        print(f"  Processed: {'✓' if processed else '✗'}")
        print(f"  Requirements: {req_count}")
        print(f"  Assignments: {assign_count}")
        print(f"  Pattern Check: {'✓' if pattern_match else '✗'} (expected: REQ_DOC{doc_id}_XXXX)")
        
        if req_ids:
            print(f"  Sample requirement_ids:")
            for req_id in req_ids[:3]:
                print(f"    - {req_id}")
            if len(req_ids) > 3:
                print(f"    ... and {len(req_ids) - 3} more")
    
    # Check for duplicate requirement_ids across documents
    print("\n" + "=" * 100)
    print("[DUPLICATE CHECK] Checking for requirement_id collisions across documents")
    print("-" * 100)
    
    cursor.execute("""
        SELECT requirement_id, COUNT(DISTINCT document_id) as doc_count, GROUP_CONCAT(document_id) as doc_ids
        FROM requirements
        GROUP BY requirement_id
        HAVING doc_count > 1
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n❌ FAIL: Found {len(duplicates)} requirement_ids shared across multiple documents:")
        for dup in duplicates:
            print(f"  {dup['requirement_id']} -> documents: {dup['doc_ids']}")
        all_passed = False
    else:
        print(f"\n✅ PASS: No requirement_id collisions found")
    
    # Summary statistics
    print("\n" + "=" * 100)
    print("[SUMMARY] Database Statistics")
    print("-" * 100)
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requirements")
    total_reqs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM assignments")
    total_assigns = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT document_id) FROM requirements")
    docs_with_reqs = cursor.fetchone()[0]
    
    print(f"\nTotal documents: {total_docs}")
    print(f"Total requirements: {total_reqs}")
    print(f"Total assignments: {total_assigns}")
    print(f"Documents with requirements: {docs_with_reqs}/{total_docs}")
    
    if total_docs > 0:
        avg_reqs = total_reqs / total_docs
        avg_assigns = total_assigns / total_docs
        print(f"Average requirements per document: {avg_reqs:.1f}")
        print(f"Average assignments per document: {avg_assigns:.1f}")
    
    # Final verdict
    print("\n" + "=" * 100)
    print("[VERDICT]")
    print("=" * 100)
    
    if all_passed and total_docs > 0 and total_reqs > 0:
        print("\n✅ FIX VERIFIED SUCCESSFULLY")
        print("   - All documents have requirements")
        print("   - All documents have assignments")
        print("   - No requirement_id collisions across documents")
        print("   - requirement_id pattern uses document_id (REQ_DOC{id}_XXXX)")
    else:
        print("\n❌ VERIFICATION FAILED")
        if total_docs == 0:
            print("   - No documents found (upload a circular to test)")
        if total_reqs == 0:
            print("   - No requirements created")
        if not all_passed:
            print("   - One or more documents failed checks")
    
    print("\n" + "=" * 100)
    
    conn.close()
    return all_passed

if __name__ == "__main__":
    verify_fix()
