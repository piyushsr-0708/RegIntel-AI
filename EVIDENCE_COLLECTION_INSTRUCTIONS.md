# EVIDENCE COLLECTION INSTRUCTIONS

## Purpose
Collect runtime evidence to prove whether duplicate-protection branch executed for document_id=22.

## Changes Made (Diagnostic Logging Only)

### 1. Backend Logging Added
**File:** `backend/routers/admin_router.py`  
**Location:** Lines ~145-180 (process_document function)

**Added logs:**
- Document original_filename
- Filename prefix (first 10 characters)
- Each generated req_id
- Whether duplicate was found
- Existing requirement details if duplicate
- Final created_count and assignment_count

**Example output:**
```
[PROCESS] ========== PROCESSING DOCUMENT_ID=22 ==========
[PROCESS] original_filename: test.pdf
[PROCESS] filename prefix (first 10 chars): TEST.PDF
[PROCESS] --- Requirement 0 ---
[PROCESS] Generated req_id: REQ_TEST.PDF_0000
[PROCESS] ⚠️  DUPLICATE FOUND: REQ_TEST.PDF_0000 already exists!
[PROCESS]     Existing requirement.id: 45
[PROCESS]     Existing requirement.document_id: 18
[PROCESS]     SKIPPING creation for this requirement
[PROCESS] ========== PROCESSING COMPLETE ==========
[PROCESS] FINAL created_count: 0
[PROCESS] FINAL assignment_count: 0
```

### 2. SQL Diagnostic Script
**File:** `backend/diagnostic_queries.py`  
**Purpose:** Run SQL queries against the database to collect evidence

**Queries:**
1. Document details for id=22
2. Count of requirements for document_id=22
3. All requirements ordered by requirement_id
4. Requirements grouped by filename prefix
5. All documents in database
6. Assignments analysis per document

---

## Step 1: Run SQL Diagnostic Queries

### Option A: Using Python Script

```bash
cd d:\SuRaksha\backend
python diagnostic_queries.py
```

This will execute all diagnostic SQL queries and print results to console.

### Option B: Using SQLite CLI

```bash
cd d:\SuRaksha
sqlite3 data/compliance.db
```

Then run these queries one by one:

```sql
-- Query 1: Document details
SELECT id, original_filename FROM documents WHERE id = 22;

-- Query 2: Requirements count for document_id=22
SELECT COUNT(*) FROM requirements WHERE document_id = 22;

-- Query 3: All requirements
SELECT requirement_id, document_id FROM requirements ORDER BY requirement_id;

-- Query 4: All documents
SELECT id, original_filename, processed FROM documents ORDER BY id;

-- Query 5: Assignments per document
SELECT 
    r.document_id,
    COUNT(a.id) as assignment_count
FROM requirements r
LEFT JOIN assignments a ON a.requirement_id = r.id
GROUP BY r.document_id
ORDER BY r.document_id;
```

---

## Step 2: Upload New Document and Collect Backend Logs

### A. Start Backend with Logging

```bash
cd d:\SuRaksha
python -m uvicorn backend.main:app --reload
```

Watch the terminal for `[PROCESS]` logs.

### B. Upload a Test Document

**Using frontend:**
1. Open http://localhost:3000
2. Navigate to Pipeline
3. Upload a PDF file
4. Note the document_id from the response

**Using curl:**
```bash
curl -X POST "http://localhost:8000/admin/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@test.pdf" \
  -F "document_type=RBI_Circular"
```

### C. Process the Document

The frontend will automatically call process-document, OR you can call it manually:

```bash
curl -X POST "http://localhost:8000/admin/process-document/22" \
  -H "Authorization: Bearer <token>"
```

### D. Capture Backend Output

Copy ALL lines from terminal that start with `[PROCESS]`.

Expected output structure:
```
[PROCESS] ========== PROCESSING DOCUMENT_ID=22 ==========
[PROCESS] original_filename: <filename>
[PROCESS] filename prefix (first 10 chars): <PREFIX>
[PROCESS] --- Requirement 0 ---
[PROCESS] Generated req_id: REQ_<PREFIX>_0000
[PROCESS] ⚠️  DUPLICATE FOUND / ✓ No duplicate found
...
[PROCESS] FINAL created_count: <X>
[PROCESS] FINAL assignment_count: <Y>
```

---

## Step 3: Analyze Evidence

### Evidence to Collect

For document_id=22, determine:

1. **original_filename value:**
   - From SQL Query 1
   - From backend logs

2. **All generated req_id values:**
   - From backend logs (14 total expected)

3. **Duplicate detection results:**
   - For EACH req_id, was duplicate found?
   - If YES: What was the existing requirement.id and document_id?

4. **Final counts:**
   - created_count (from backend logs)
   - assignment_count (from backend logs)
   - Should match the response from /admin/process-document

5. **Database state:**
   - How many requirements have document_id=22? (SQL Query 2)
   - Do any requirements exist with the generated req_ids? (SQL Query 3)
   - If YES: Which document_id owns them? (SQL Query 3)

---

## Expected Scenarios

### Scenario A: Duplicate Detected (Empty Arrays)

**Backend Logs:**
```
[PROCESS] ========== PROCESSING DOCUMENT_ID=22 ==========
[PROCESS] original_filename: test.pdf
[PROCESS] Generated req_id: REQ_TEST.PDF_0000
[PROCESS] ⚠️  DUPLICATE FOUND: REQ_TEST.PDF_0000 already exists!
[PROCESS]     Existing requirement.document_id: 18
[PROCESS]     SKIPPING creation
... (repeat for all 14 requirements)
[PROCESS] FINAL created_count: 0
[PROCESS] FINAL assignment_count: 0
```

**SQL Results:**
```sql
-- Query 2: Count for document_id=22
0  -- No requirements for document_id=22

-- Query 3: All requirements
REQ_TEST.PDF_0000 | 18  -- Owned by document_id=18
REQ_TEST.PDF_0001 | 18
... (all with document_id=18, not 22)
```

**Conclusion:** Duplicate protection executed, skipped all requirements.

---

### Scenario B: No Duplicate (Should Work)

**Backend Logs:**
```
[PROCESS] ========== PROCESSING DOCUMENT_ID=22 ==========
[PROCESS] original_filename: unique_file.pdf
[PROCESS] Generated req_id: REQ_UNIQUE_FIL_0000
[PROCESS] ✓ No duplicate found, creating requirement
[PROCESS] ✓ Requirement created (id=89, document_id=22)
[PROCESS] ✓ Assignment created (id=89, requirement_id=89)
... (repeat for all 14 requirements)
[PROCESS] FINAL created_count: 14
[PROCESS] FINAL assignment_count: 14
```

**SQL Results:**
```sql
-- Query 2: Count for document_id=22
14  -- 14 requirements for document_id=22

-- Query 3: All requirements
REQ_UNIQUE_FIL_0000 | 22
REQ_UNIQUE_FIL_0001 | 22
... (all with document_id=22)
```

**Conclusion:** No duplicates, all requirements created successfully.

---

### Scenario C: Other Failure (Not Duplicate)

**Backend Logs:**
```
[PROCESS] original_filename: test.pdf
[PROCESS] Generated req_id: REQ_TEST.PDF_0000
[PROCESS] ✓ No duplicate found, creating requirement
ERROR: <exception message>
[PROCESS] FINAL created_count: 0  -- or some number < 14
```

**SQL Results:**
```sql
-- Query 2: Count for document_id=22
<some number between 0-14>  -- Partial insert
```

**Conclusion:** Different failure - not duplicate protection.

---

## Step 4: Document Findings

Create a report with:

1. **SQL Query Results** (copy-paste all output)
2. **Backend Log Output** (all [PROCESS] lines)
3. **Analysis:**
   - Was duplicate protection triggered? (YES/NO)
   - If YES: Which document_id owned the existing requirements?
   - Final created_count and assignment_count values
   - Database state verification

---

## Expected Deliverable

A markdown report with three sections:

### Section 1: SQL Query Results
```
[QUERY 1] Document details for id=22:
  id: 22
  original_filename: test.pdf

[QUERY 2] Count of requirements for document_id=22:
  Total requirements: 0

[QUERY 3] All requirements ordered by requirement_id:
  requirement_id          | document_id
  REQ_TEST.PDF_0000       | 18
  ...
```

### Section 2: Backend Processing Logs
```
[PROCESS] ========== PROCESSING DOCUMENT_ID=22 ==========
[PROCESS] original_filename: test.pdf
...
[PROCESS] FINAL created_count: 0
[PROCESS] FINAL assignment_count: 0
```

### Section 3: Evidence Analysis
- Was duplicate branch executed? YES/NO
- If YES, which document_id owned the conflicting requirements?
- Final counts match expected behavior? YES/NO
- Conclusion: Root cause confirmed or alternative explanation

---

## Notes

- **No code logic changed** - only diagnostic logging added
- **No business logic modified** - duplicate check still operates the same way
- **No database changes** - queries are read-only
- **No fixes implemented** - evidence collection only

The goal is to PROVE the theory with actual runtime data for document_id=22.
