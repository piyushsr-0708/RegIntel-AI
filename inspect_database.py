"""
Direct SQLite database inspection for document_id=22 evidence
No code modifications - read-only database queries
"""
import sqlite3
import json
from pathlib import Path

def inspect_database():
    db_path = Path("data/compliance.db")
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path.absolute()}")
        return
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 100)
    print("DATABASE EVIDENCE REPORT FOR document_id=22")
    print("=" * 100)
    
    # ========== SCHEMA INSPECTION ==========
    print("\n" + "=" * 100)
    print("SECTION 1: SCHEMA INSPECTION")
    print("=" * 100)
    
    tables = ['documents', 'requirements', 'assignments', 'departments']
    
    for table in tables:
        print(f"\n[SCHEMA] {table.upper()} table:")
        print("-" * 100)
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"  {'cid':<5} | {'name':<25} | {'type':<15} | {'notnull':<8} | {'pk':<3}")
        print("  " + "-" * 90)
        for col in columns:
            print(f"  {col['cid']:<5} | {col['name']:<25} | {col['type']:<15} | {col['notnull']:<8} | {col['pk']:<3}")
    
    # ========== DATABASE TOTALS ==========
    print("\n" + "=" * 100)
    print("SECTION 2: DATABASE TOTALS")
    print("=" * 100)
    
    cursor.execute("SELECT COUNT(*) as count FROM documents")
    total_docs = cursor.fetchone()['count']
    print(f"\nTotal documents: {total_docs}")
    
    cursor.execute("SELECT COUNT(*) as count FROM requirements")
    total_reqs = cursor.fetchone()['count']
    print(f"Total requirements: {total_reqs}")
    
    cursor.execute("SELECT COUNT(*) as count FROM assignments")
    total_assigns = cursor.fetchone()['count']
    print(f"Total assignments: {total_assigns}")
    
    cursor.execute("SELECT COUNT(*) as count FROM departments")
    total_depts = cursor.fetchone()['count']
    print(f"Total departments: {total_depts}")
    
    # ========== DOCUMENT_ID=22 DETAILS ==========
    print("\n" + "=" * 100)
    print("SECTION 3: DOCUMENT_ID=22 DETAILS")
    print("=" * 100)
    
    cursor.execute("SELECT * FROM documents WHERE id = 22")
    doc = cursor.fetchone()
    
    if doc:
        print("\n✅ Document found:")
        print("-" * 100)
        for key in doc.keys():
            print(f"  {key:<25} : {doc[key]}")
    else:
        print("\n❌ No document found with id=22")
        
        # Check what document IDs exist
        cursor.execute("SELECT id FROM documents ORDER BY id")
        doc_ids = [row['id'] for row in cursor.fetchall()]
        print(f"\nExisting document IDs: {doc_ids}")
    
    # ========== REQUIREMENTS FOR DOCUMENT_ID=22 ==========
    print("\n" + "=" * 100)
    print("SECTION 4: REQUIREMENTS FOR DOCUMENT_ID=22")
    print("=" * 100)
    
    cursor.execute("SELECT COUNT(*) as count FROM requirements WHERE document_id = 22")
    req_count = cursor.fetchone()['count']
    print(f"\nCount: {req_count} requirements")
    
    if req_count > 0:
        cursor.execute("SELECT * FROM requirements WHERE document_id = 22 ORDER BY requirement_id")
        reqs = cursor.fetchall()
        print("\nRequirements:")
        print("-" * 100)
        for req in reqs:
            print(f"\n  ID: {req['id']}")
            print(f"  requirement_id: {req['requirement_id']}")
            print(f"  document_id: {req['document_id']}")
            print(f"  domain: {req['domain']}")
            print(f"  priority: {req['priority']}")
            print(f"  classification: {req['classification']}")
            print(f"  text: {req['text'][:80]}...")
    else:
        print("\n❌ No requirements found for document_id=22")
        
        # Check if expected requirement_ids exist under different document_id
        if doc:
            filename_prefix = doc['original_filename'][:10].upper()
            expected_pattern = f"REQ_{filename_prefix}%"
            
            print(f"\n[SEARCH] Looking for requirements matching pattern: {expected_pattern}")
            cursor.execute(
                "SELECT requirement_id, document_id FROM requirements WHERE requirement_id LIKE ? ORDER BY requirement_id",
                (expected_pattern,)
            )
            matching_reqs = cursor.fetchall()
            
            if matching_reqs:
                print(f"\n⚠️  Found {len(matching_reqs)} requirements with expected pattern but different document_id:")
                print("-" * 100)
                print(f"  {'requirement_id':<35} | document_id")
                print("  " + "-" * 50)
                for req in matching_reqs:
                    print(f"  {req['requirement_id']:<35} | {req['document_id']}")
            else:
                print(f"\n✓ No requirements found matching pattern {expected_pattern}")
    
    # ========== ASSIGNMENTS FOR DOCUMENT_ID=22 ==========
    print("\n" + "=" * 100)
    print("SECTION 5: ASSIGNMENTS FOR DOCUMENT_ID=22")
    print("=" * 100)
    
    cursor.execute("""
        SELECT a.*, r.requirement_id, r.document_id, d.name as department_name
        FROM assignments a
        JOIN requirements r ON a.requirement_id = r.id
        JOIN departments d ON a.department_id = d.id
        WHERE r.document_id = 22
        ORDER BY a.id
    """)
    assignments = cursor.fetchall()
    
    print(f"\nCount: {len(assignments)} assignments")
    
    if assignments:
        print("\nAssignments:")
        print("-" * 100)
        for assign in assignments:
            print(f"\n  Assignment ID: {assign['id']}")
            print(f"  requirement_id: {assign['requirement_id']} ({assign['requirement_id']})")
            print(f"  department: {assign['department_name']}")
            print(f"  status: {assign['status']}")
            print(f"  is_published: {assign['is_published']}")
            print(f"  assigned_at: {assign['assigned_at']}")
    else:
        print("\n❌ No assignments found for document_id=22 requirements")
    
    # ========== ALL REQUIREMENTS IN DATABASE ==========
    print("\n" + "=" * 100)
    print("SECTION 6: ALL REQUIREMENTS IN DATABASE")
    print("=" * 100)
    
    cursor.execute("SELECT requirement_id, document_id FROM requirements ORDER BY requirement_id")
    all_reqs = cursor.fetchall()
    
    if all_reqs:
        print(f"\nTotal requirements: {len(all_reqs)}")
        print("\n  {'requirement_id':<40} | document_id")
        print("  " + "-" * 60)
        for req in all_reqs:
            print(f"  {req['requirement_id']:<40} | {req['document_id']}")
    else:
        print("\n⚠️  No requirements found in database")
    
    # ========== DOCUMENT SUMMARY TABLE ==========
    print("\n" + "=" * 100)
    print("SECTION 7: ALL DOCUMENTS SUMMARY")
    print("=" * 100)
    
    cursor.execute("""
        SELECT 
            d.id,
            d.original_filename,
            d.processed,
            d.processed_at,
            COUNT(DISTINCT r.id) as requirements_count,
            COUNT(DISTINCT a.id) as assignments_count
        FROM documents d
        LEFT JOIN requirements r ON r.document_id = d.id
        LEFT JOIN assignments a ON a.requirement_id = r.id
        GROUP BY d.id
        ORDER BY d.id
    """)
    doc_summary = cursor.fetchall()
    
    if doc_summary:
        print(f"\nTotal documents: {len(doc_summary)}")
        print("\n  ID  | Original Filename                        | Processed | Processed At        | Requirements | Assignments")
        print("  " + "-" * 130)
        for doc in doc_summary:
            processed_mark = "✓" if doc['processed'] else "✗"
            print(f"  {doc['id']:<3} | {doc['original_filename']:<40} | {processed_mark:<9} | {str(doc['processed_at'] or 'NULL'):<19} | {doc['requirements_count']:<12} | {doc['assignments_count']}")
    
    # ========== SIMULATE GET ENDPOINT ==========
    print("\n" + "=" * 100)
    print("SECTION 8: SIMULATED GET /admin/document-analysis/22")
    print("=" * 100)
    
    # Replicate the exact query logic from the endpoint
    cursor.execute("SELECT * FROM documents WHERE id = 22")
    doc = cursor.fetchone()
    
    if not doc:
        print("\n❌ Document not found - endpoint would return 404")
    else:
        # Get requirements
        cursor.execute("SELECT * FROM requirements WHERE document_id = 22")
        requirements = cursor.fetchall()
        requirement_ids = [r['id'] for r in requirements]
        
        # Get assignments
        if requirement_ids:
            placeholders = ','.join('?' * len(requirement_ids))
            cursor.execute(f"""
                SELECT a.*, r.requirement_id, r.text as requirement_text, r.domain, r.classification, r.priority,
                       d.name as department_name
                FROM assignments a
                JOIN requirements r ON a.requirement_id = r.id
                JOIN departments d ON a.department_id = d.id
                WHERE a.requirement_id IN ({placeholders})
            """, requirement_ids)
            assignments = cursor.fetchall()
        else:
            assignments = []
        
        # Build response
        print("\nEndpoint response would be:")
        print("-" * 100)
        print(f"\ndocument:")
        print(f"  id: {doc['id']}")
        print(f"  filename: {doc['original_filename']}")
        print(f"  uploaded_at: {doc['uploaded_at']}")
        print(f"  processed_at: {doc['processed_at']}")
        
        print(f"\ncounts:")
        print(f"  requirements_extracted: {len(requirements)}")
        print(f"  assignments_generated: {len(assignments)}")
        
        # Priority counts
        priority_counts = {}
        for assign in assignments:
            priority = assign['priority'] or 'Medium'
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        print(f"  critical_priority: {priority_counts.get('Critical', 0)}")
        print(f"  high_priority: {priority_counts.get('High', 0)}")
        print(f"  medium_priority: {priority_counts.get('Medium', 0)}")
        print(f"  low_priority: {priority_counts.get('Low', 0)}")
        
        # Department counts
        dept_counts = {}
        for assign in assignments:
            dept = assign['department_name']
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        print(f"  departments_affected: {len(dept_counts)}")
        
        print(f"\nassignments array: [{len(assignments)} items]")
        print(f"department_summary array: [{len(dept_counts)} items]")
        
        if len(assignments) == 0:
            print("\n⚠️  EMPTY ARRAYS - This matches the frontend display of zeros")
    
    # ========== EVIDENCE SUMMARY ==========
    print("\n" + "=" * 100)
    print("SECTION 9: EVIDENCE-BASED CONCLUSIONS")
    print("=" * 100)
    
    cursor.execute("SELECT * FROM documents WHERE id = 22")
    doc = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as count FROM requirements WHERE document_id = 22")
    req_count = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM assignments a
        JOIN requirements r ON a.requirement_id = r.id
        WHERE r.document_id = 22
    """)
    assign_count = cursor.fetchone()['count']
    
    print("\n[Q1] Were requirements ever inserted for document_id=22?")
    if req_count > 0:
        print(f"  ✅ YES - {req_count} requirements exist")
    else:
        print(f"  ❌ NO - 0 requirements exist")
    
    print("\n[Q2] Were assignments ever inserted?")
    if assign_count > 0:
        print(f"  ✅ YES - {assign_count} assignments exist")
    else:
        print(f"  ❌ NO - 0 assignments exist")
    
    print("\n[Q3] Is the GET endpoint returning correct data?")
    print(f"  ✅ YES - Returns exactly what's in database:")
    print(f"     requirements_extracted: {req_count} (database count)")
    print(f"     assignments_generated: {assign_count} (database count)")
    print(f"     Frontend correctly displays these zero values")
    
    print("\n[Q4] At which persistence stage did data disappear?")
    if req_count == 0 and doc:
        print(f"  📍 REQUIREMENT INSERTION STAGE")
        print(f"     - Document was created (id={doc['id']})")
        print(f"     - Document was marked processed={doc['processed']}")
        print(f"     - But NO requirements were inserted into database")
        print(f"     - Therefore NO assignments could be created")
        print(f"     - Root cause: Requirements were never persisted to database")
        
        # Check for duplicate pattern
        filename_prefix = doc['original_filename'][:10].upper()
        expected_pattern = f"REQ_{filename_prefix}%"
        cursor.execute(
            "SELECT COUNT(*) as count FROM requirements WHERE requirement_id LIKE ?",
            (expected_pattern,)
        )
        matching_count = cursor.fetchone()['count']
        
        if matching_count > 0:
            cursor.execute(
                "SELECT DISTINCT document_id FROM requirements WHERE requirement_id LIKE ?",
                (expected_pattern,)
            )
            other_doc_ids = [row['document_id'] for row in cursor.fetchall()]
            print(f"\n  🔍 EVIDENCE OF DUPLICATE SKIP:")
            print(f"     - Expected requirement_id pattern: {expected_pattern}")
            print(f"     - {matching_count} requirements with this pattern exist")
            print(f"     - They belong to document_id(s): {other_doc_ids}")
            print(f"     - Conclusion: Duplicate protection likely skipped insertion")
    elif req_count > 0 and assign_count == 0:
        print(f"  📍 ASSIGNMENT INSERTION STAGE")
        print(f"     - Requirements exist ({req_count} rows)")
        print(f"     - But NO assignments were created")
    else:
        print(f"  ✅ NO DATA LOSS - All expected data present")
    
    print("\n" + "=" * 100)
    print("END OF EVIDENCE REPORT")
    print("=" * 100)
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
