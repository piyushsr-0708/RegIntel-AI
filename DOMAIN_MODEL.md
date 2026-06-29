# Domain Model - Canonical Entity Definitions

**Critical Finding:** The term "MAP" is used inconsistently throughout the codebase, creating semantic drift.

---

## Core Entities

### 1. Document / Circular

**Definition:** An uploaded RBI regulatory document (PDF)

**Database:**
- Table: `documents`
- Primary Key: `id` (integer, auto-increment)
- Semantic ID: None
- Lifecycle: Upload → Processing → Processed

**Fields:**
- `filename`: Storage filename
- `original_filename`: User-uploaded filename
- `file_path`: Filesystem location
- `document_type`: e.g., "RBI_Circular"
- `uploaded_by`: User ID
- `processed`: Boolean flag
- `batch_id`: Foreign key to assignment_batches

**Created By:** `POST /admin/upload` → `create_document()`

**Consumed By:**
- Pipeline processing
- Document list views
- Batch tracking

**Relationships:**
- 1 Document → Many Requirements
- 1 Document → 1 Batch (optional)

---

### 2. Requirement

**Definition:** An extracted compliance requirement from a regulatory document

**Database:**
- Table: `requirements`
- Primary Key: `id` (integer, auto-increment)
- Semantic ID: `requirement_id` (string, e.g., "REQ_41YC0107_0022")
- Lifecycle: Extract from Document → Classify → Assign to Department

**Fields:**
- `requirement_id`: Unique semantic identifier
- `document_id`: Foreign key to documents
- `text`: Full requirement text (BUSINESS DATA - must persist)
- `classification`: Mandatory/Recommended/Informational
- `domain`: AML/KYC/Cybersecurity/etc.
- `priority`: Critical/High/Medium/Low
- `deadline`: Extracted deadline text
- `source_reference`: Circular reference
- `batch_id`: Foreign key to assignment_batches

**Created By:** `POST /admin/process-document/{id}` → `create_requirement()`

**Consumed By:**
- Requirement Search page (demo data from JSON)
- Assignment creation
- Knowledge Graph (demo data from JSON)
- Dashboard metrics (database)

**Relationships:**
- 1 Requirement → Many Assignments (one requirement can be assigned to multiple departments)
- 1 Document → Many Requirements

**⚠️ CRITICAL ISSUE:** 
- Backend database stores persistent requirements
- Frontend Requirement Search uses demo JSON file (requirementsTaxonomy)
- These are NOT synchronized

---

### 3. Assignment

**Definition:** The assignment of a requirement to a specific department for compliance action

**Database:**
- Table: `assignments`
- Primary Key: `id` (integer, auto-increment)
- Semantic ID: None
- Lifecycle: Create → Publish → In Progress → Complete

**Fields:**
- `requirement_id`: Foreign key to requirements
- `department_id`: Foreign key to departments
- `assigned_by`: User ID
- `status`: pending/in_progress/completed
- `is_published`: Boolean (draft vs published)
- `priority`: Can override requirement priority
- `due_date`: Operational deadline
- `remarks`: Notes
- `batch_id`: Foreign key to assignment_batches

**Created By:** `POST /admin/process-document/{id}` → `create_assignment()`

**Consumed By:**
- Dashboard (Published Assignments, Draft Assignments, Pending/Completed Tasks)
- Assignment Center (review before publishing)
- Department Workspace (published tasks for department users)
- Department Dashboard (completion tracking)

**Relationships:**
- 1 Assignment → 1 Requirement
- 1 Assignment → 1 Department
- Many Assignments → 1 Requirement (possible)
- Many Assignments → 1 Department

**⚠️ SEMANTIC DRIFT DETECTED:**
Backend code and schemas refer to assignments as:
- "maps" in `total_maps` field
- "MAPs" in comments
- "assignments" in table/model name
- "tasks" in UI labels

---

### 4. Mitigation Action Plan (MAP)

**Definition:** **⚠️ DOMAIN MODEL ERROR**

**Current State:** MAP is NOT a separate entity in the database

**What Exists:**
- `assignments` table (relationship between requirement and department)
- `requirements` table (extracted compliance requirements)

**What Does NOT Exist:**
- No `maps` table
- No MAP-specific business logic
- No MAP generation process

**Actual Reality:**
```
Requirement → Assigned to Department = Assignment
```

**Terminology Used:**
- Backend calls assignments "MAPs" (semantic error)
- Frontend demo data has mapsOutput.json
- UI displays "Total MAPs" but counts assignments
- No actual "mitigation action plan" generation occurs

**⚠️ CRITICAL FINDING:**
The application does NOT generate MAPs. It creates assignments of requirements to departments. The term "MAP" is a misnomer throughout the codebase.

**Expected vs Actual:**

Expected:
```
1 Requirement → Analysis → 1 MAP (mitigation plan) → Assigned to Department
```

Actual:
```
1 Requirement → Assigned to Department → 1 Assignment (called "MAP" in code)
```

---

### 5. Department

**Definition:** An organizational unit responsible for compliance

**Database:**
- Table: `departments`
- Primary Key: `id` (integer, auto-increment)
- Semantic ID: `code` (string, e.g., "COMP", "RISK")
- Lifecycle: Static (created during setup)

**Fields:**
- `name`: Department name
- `code`: Short code
- `description`: Optional description

**Created By:** Database seeding / admin setup

**Consumed By:**
- All pages that display department information
- Assignment routing
- User authentication (department users)
- Risk calculations

**Relationships:**
- 1 Department → Many Assignments
- 1 Department → Many Users

**Standard Departments:**
1. Compliance
2. Risk Management  
3. Treasury Operations
4. Cyber Security
5. IT
6. Finance
7. Operations
8. AML Compliance Cell
9. Legal

---

### 6. AssignmentBatch

**Definition:** A workflow container for a compliance campaign (circular processing)

**Database:**
- Table: `assignment_batches`
- Primary Key: `id` (integer, auto-increment)
- Semantic ID: None
- Lifecycle: Draft → Published → In Progress → Completed → Closed

**Fields:**
- `batch_name`: User-defined name
- `circular_name`: Source circular name
- `uploaded_by`: User ID
- `status`: Batch lifecycle status
- `total_requirements`: Count of requirements
- `total_maps`: **⚠️ Should be "total_assignments"**
- `completion_percentage`: Progress metric
- `verification_percentage`: QA metric

**Created By:** `POST /assignment-batches/create`

**Consumed By:**
- Batch management UI (future)
- Progress tracking (future)

**Relationships:**
- 1 Batch → Many Documents
- 1 Batch → Many Requirements
- 1 Batch → Many Assignments

**⚠️ SEMANTIC DRIFT:**
- Field name `total_maps` perpetuates incorrect terminology
- Should be `total_assignments`

---

### 7. Analysis Session

**Definition:** **Frontend-only** temporary state for pipeline analysis

**Storage:** React Context state (AnalysisSession.jsx)

**Lifecycle:**
1. Pipeline upload → Create session
2. Processing complete → Store results in session
3. Exit analysis → Clear session
4. **NO DATABASE PERSISTENCE**

**Contents:**
- file metadata
- processing elapsed time
- analysis results (requirements, maps, departments, graph)
- AI briefing

**⚠️ CRITICAL ISSUE:**
- Session data is DEMO DATA ONLY
- Uses demo JSON files for requirements and maps
- NOT connected to database
- Graph viewer requires active session
- Business data (requirements, MAPs) should NOT depend on session

---

### 8. Knowledge Graph

**Definition:** Visual representation of regulatory relationships

**Components:**
- **Nodes:** Circulars, Requirements, MAPs (assignments), Departments
- **Edges:** defines, generates, assigned

**Storage:**
- **Demo Mode:** Generated from demo JSON files in AnalysisSession
- **No Database:** Graph is NOT persisted

**Node Types:**
1. **Circular**: RBI regulatory document
2. **Requirement**: Extracted compliance requirement
3. **MAP**: Assignment (misnomer)
4. **Department**: Organizational unit

**Edge Types:**
1. **defines**: Circular → Requirement
2. **generates**: Requirement → MAP
3. **assigned**: MAP → Department

**⚠️ CRITICAL ISSUE:**
- Graph uses semantic IDs (REQ-XXX, MAP-XXX)
- Database uses integer IDs
- No mapping between them
- Cannot retrieve full text from database using graph node IDs

---

### 9. Risk Score

**Definition:** Calculated department risk metric

**Calculation:**
```python
raw_score = Critical*40 + High*20 + Medium*5 + Low*1
risk_score = (raw_score / max_raw_score) * 100  # Normalized to 0-100
```

**Storage:** NOT persisted, calculated on demand

**Computed From:**
- Department assignments
- Priority distribution
- Completion status

**Used By:**
- Departments Risk page
- Dashboard risk metrics

---

### 10. Priority

**Definition:** Urgency classification for requirements and assignments

**Values:** Critical, High, Medium, Low

**Storage Locations:**
- `requirements.priority` - Priority of the requirement itself
- `assignments.priority` - Can override requirement priority for operational needs

**Logic:**
```python
# Display priority uses this hierarchy:
priority = assignment.priority if assignment.priority else requirement.priority
```

**⚠️ SEMANTIC DRIFT:**
- Dashboard counts "Critical MAPs" but means "Critical Priority Assignments"
- "High Priority MAPs" means "High Priority Assignments"

---

### 11. Impact Score

**Definition:** Numeric measure of requirement/assignment severity

**Range:** 0.0 - 10.0

**Storage:** 
- **Demo Data Only** - mapsOutput.json has `impact_score` field
- **NOT in database**

**Usage:**
- MAP Detail display
- Sorting/filtering in UI
- Demo feature only

---

## Entity Relationship Summary

```
Document
  ├─> Requirements (1:many)
  │     └─> Assignments (1:many per requirement)
  │           └─> Department (many:1)
  │
  └─> AssignmentBatch (1:1 optional)

AssignmentBatch
  ├─> Documents (1:many)
  ├─> Requirements (1:many)
  └─> Assignments (1:many)

User
  ├─> Department (many:1)
  └─> AuditLogs (1:many)

Assignment
  ├─> Requirement (many:1)
  ├─> Department (many:1)
  ├─> Batch (many:1 optional)
  └─> StatusHistory (1:many)
```

---

## Database Tables

| Table | Purpose | Primary Key | Foreign Keys |
|-------|---------|-------------|--------------|
| users | Authentication | id (int) | department_id |
| departments | Org units | id (int) | None |
| documents | Uploaded PDFs | id (int) | uploaded_by, batch_id |
| requirements | Extracted rules | id (int) | document_id, batch_id |
| assignments | Dept tasks | id (int) | requirement_id, department_id, assigned_by, batch_id |
| assignment_batches | Campaigns | id (int) | uploaded_by |
| compliance_status_history | Audit trail | id (int) | assignment_id, changed_by |
| audit_logs | System audit | id (int) | user_id |

---

## Critical Findings

### 1. MAP is NOT a Real Entity
- No `maps` table exists
- "MAP" terminology refers to assignments
- No mitigation plan generation occurs
- Semantic drift throughout codebase

### 2. Requirements Have Dual Sources
- Database: Persistent requirements from pipeline
- Demo JSON: requirementsTaxonomy.json for search
- These are NOT synchronized

### 3. Graph is Session-Dependent
- Knowledge Graph only works during active analysis session
- Uses demo data, not database
- Cannot retrieve business data outside session

### 4. Mixed Terminology
- "maps", "MAPs", "assignments", "tasks" all refer to same entity
- Backend: `total_maps` field in schemas
- Frontend: "Total MAPs" in UI
- Database: `assignments` table
- Correct term: **Assignments**

### 5. No True MAP Generation
Expected workflow:
```
Requirement → AI Analysis → Generate MAP → Assign to Department
```

Actual workflow:
```
Requirement → Direct Assignment to Department (called "MAP")
```

---

## Recommended Terminology

| Current (Incorrect) | Correct | Database Table |
|---------------------|---------|----------------|
| MAP | Assignment | assignments |
| Total MAPs | Total Assignments | assignments |
| Generated MAPs | Created Assignments | assignments |
| MAP ID | Assignment ID | assignments.id |
| Critical MAPs | Critical Priority Assignments | assignments |

