# EVIDENCE COLLECTION READY

## Status: ✅ READY TO COLLECT EVIDENCE

---

## What Was Done

### 1. Added Diagnostic Logging (No Logic Changes)

**File:** `backend/routers/admin_router.py`

**Added:**
- Log document original_filename
- Log filename prefix (first 10 characters)
- Log each generated req_id
- Log whether duplicate was found
- Log existing requirement details if duplicate exists
- Log final created_count and assignment_count

**No business logic changed** - only print statements added for visibility.

---

### 2. Created SQL Diagnostic Script

**File:** `backend/diagnostic_queries.py`

**Purpose:** Execute SQL queries to inspect database state for document_id=22

**Queries:**
1. Document details for id=22
2. Count of requirements for document_id=22
3. All requirements ordered by requirement_id
4. Requirements grouped by filename prefix (to detect collisions)
5. All documents in database
6. Assignments analysis per document

---

### 3. Created Evidence Collection Instructions

**File:** `EVIDENCE_COLLECTION_INSTRUCTIONS.md`

**Contains:**
- Step-by-step instructions to run diagnostics
- How to collect backend logs
- Expected output for each scenario
- Template for evidence report

---

## How to Collect Evidence

### Quick Start

**Step 1: Run SQL Diagnostics**
```bash
cd d:\SuRaksha\backend
python diagnostic_queries.py
```

**Step 2: Check Current Database State**

This will show:
- What is document_id=22's original_filename?
- How many requirements exist for document_id=22?
- What requirement_ids exist in the database?
- Are there filename prefix collisions?

**Step 3: Process Document 22 (if not already processed)**

If document 22 was never processed, or you want to test with a new document:

```bash
# Start backend
cd d:\SuRaksha
python -m uvicorn backend.main:app --reload

# Watch for [PROCESS] logs in terminal
```

Then upload/process a document via frontend or API.

**Step 4: Capture Output**

Copy ALL lines that start with:
- `[PROCESS]` from backend terminal
- SQL query results from diagnostic script

---

## Evidence Needed for document_id=22

To prove the theory, we need:

### A. From Database (SQL Queries)

1. ✅ `original_filename` for document_id=22
2. ✅ Count of requirements WHERE `document_id=22`
3. ✅ All requirement_ids in database with their document_ids
4. ✅ Check if any requirement_id patterns conflict

### B. From Backend Logs (Runtime)

1. ✅ Document original_filename when processing started
2. ✅ All 14 generated req_id values
3. ✅ For each req_id: Was duplicate found? (YES/NO)
4. ✅ If duplicate: What was existing requirement.id and document_id?
5. ✅ Final created_count value
6. ✅ Final assignment_count value

---

## Expected Findings

### If Theory is Correct (Duplicate Protection Triggered)

**SQL Results:**
```
document_id=22 has original_filename "test.pdf"
COUNT(requirements WHERE document_id=22) = 0
REQ_TEST.PDF_0000 exists with document_id=18 (or another ID)
REQ_TEST.PDF_0001 exists with document_id=18
... (all 14 exist with different document_id)
```

**Backend Logs:**
```
[PROCESS] original_filename: test.pdf
[PROCESS] Generated req_id: REQ_TEST.PDF_0000
[PROCESS] ⚠️  DUPLICATE FOUND: Existing document_id: 18
[PROCESS] SKIPPING creation
... (repeated 14 times)
[PROCESS] FINAL created_count: 0
[PROCESS] FINAL assignment_count: 0
```

**Conclusion:** ✅ Theory confirmed - duplicate protection prevents creation

---

### If Theory is Wrong (Something Else Failed)

**SQL Results:**
```
document_id=22 has original_filename "unique.pdf"
COUNT(requirements WHERE document_id=22) = 0
No requirements exist with prefix REQ_UNIQUE.PD
```

**Backend Logs:**
```
[PROCESS] original_filename: unique.pdf
[PROCESS] Generated req_id: REQ_UNIQUE.PD_0000
[PROCESS] ✓ No duplicate found, creating requirement
[ERROR] <exception or unexpected behavior>
[PROCESS] FINAL created_count: 0
```

**Conclusion:** ❌ Theory disproven - different failure mode

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `backend/routers/admin_router.py` | Added print statements | Log processing flow |
| `backend/diagnostic_queries.py` | **NEW FILE** | SQL diagnostics |
| `EVIDENCE_COLLECTION_INSTRUCTIONS.md` | **NEW FILE** | How-to guide |
| `EVIDENCE_COLLECTION_READY.md` | **NEW FILE** | This summary |

---

## Important Notes

✅ **No business logic changed**  
✅ **No database schema changed**  
✅ **No fixes implemented**  
✅ **Read-only diagnostics only**  

The code still behaves EXACTLY the same way - we just added visibility into what it's doing.

---

## Next Steps

1. **User runs diagnostic script** → Collects SQL evidence
2. **User processes document** → Collects backend log evidence
3. **User provides evidence** → Logs + SQL results
4. **We analyze evidence** → Confirm or disprove theory
5. **Then implement fix** → Only after root cause proven

---

## Ready to Execute

All diagnostic tools are in place. No code changes needed before running diagnostics.

**To start:** Run `python backend/diagnostic_queries.py` from the project root.
