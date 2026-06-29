# Product Specification and Target Architecture
## RegIntel AI - Regulatory Intelligence Platform

**Version:** 1.0  
**Date:** June 28, 2026  
**Status:** Master Specification

---

## 1. Product Vision

**RegIntel AI** is an offline-first, AI-powered regulatory intelligence platform that transforms how financial institutions manage RBI compliance. Unlike traditional compliance management systems that require manual requirement extraction and assignment, RegIntel AI automatically extracts, classifies, and assigns regulatory obligations from PDF circulars using natural language processing and machine learning. The system builds a persistent knowledge graph mapping relationships between circulars, requirements, and departments, enabling semantic search across the entire regulatory corpus. It generates actionable mitigation plans, tracks implementation progress, and provides executive intelligence through risk scoring and predictive analytics. The platform operates entirely offline after initial setup, ensuring data security and deterministic execution critical for financial institutions. RegIntel AI is used by compliance officers, department heads, and executives to proactively manage regulatory change, reduce compliance risk, and demonstrate audit readiness.

**Key Differentiators:**
- **AI-Powered Extraction:** Automated requirement extraction from unstructured PDFs
- **Semantic Intelligence:** Vector-based similarity search across requirements
- **Knowledge Graph:** Persistent graph of regulatory relationships and dependencies
- **Offline-First:** No cloud dependencies, deterministic execution
- **Predictive Risk:** Department risk scoring based on workload and priority
- **Actionable MAPs:** Auto-generated mitigation action plans, not just task lists

---

## 2. End-to-End User Journey

### 2.1 Document Processing Journey

```
┌─────────────────────────────────────────────────────────────┐
│ HEAD_OFFICE User: Regulatory Analyst                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Upload RBI Circular (PDF)                           │
│ • User uploads new RBI circular via web interface           │
│ • System validates file (PDF, max 50MB)                     │
│ • Creates document record in database                        │
│ • Stores file in uploads/ directory                         │
│ • Assigns unique document ID                                │
│ • Triggers async AI pipeline                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: AI Pipeline Processing (Background)                 │
│                                                              │
│ 2.1 Text Extraction                                         │
│     • PyMuPDF extracts raw text from PDF                    │
│     • Preserves structure (headings, lists, tables)         │
│     • Output: Plain text with metadata                      │
│                                                              │
│ 2.2 Semantic Chunking                                       │
│     • Splits text into logical segments (512 tokens)        │
│     • Preserves sentence boundaries                         │
│     • Output: List of text chunks with positions            │
│                                                              │
│ 2.3 Requirement Extraction                                  │
│     • NLP patterns: "shall", "must", "required to"          │
│     • Contextual analysis: obligation vs description        │
│     • Extracts timelines and deadlines                      │
│     • Output: List of candidate requirements                │
│                                                              │
│ 2.4 Requirement Classification                              │
│     • Domain: KYC, AML, Cybersecurity, Risk, Treasury, etc. │
│     • Obligation Type: Mandatory, Recommended, Prohibited   │
│     • Priority: Critical, High, Medium, Low                 │
│     • Rule-based + ML classifier                            │
│     • Output: Classified requirements                       │
│                                                              │
│ 2.5 Vector Embedding Generation                             │
│     • Sentence Transformers (all-MiniLM-L6-v2)              │
│     • Generate embeddings for each requirement              │
│     • Store in vector database (ChromaDB)                   │
│     • Output: Vector embeddings with IDs                    │
│                                                              │
│ 2.6 Cross-Reference Detection                               │
│     • Regex patterns: "RBI/2024/123", "Circular dated..."   │
│     • Identify references to other circulars                │
│     • Extract reference context                             │
│     • Output: List of cross-references                      │
│                                                              │
│ 2.7 Department Assignment                                   │
│     • Rule-based mapping: Domain → Departments              │
│     • KYC → Compliance department                           │
│     • Cybersecurity → IT + Cyber Security departments       │
│     • Multi-department assignment supported                 │
│     • Output: Requirement-Department mappings               │
│                                                              │
│ 2.8 MAP Generation                                          │
│     • For each requirement, generate mitigation action plan │
│     • Template-based or LLM-powered                         │
│     • Includes: Title, Description, Actions, Timeline       │
│     • Estimated effort and resources                        │
│     • Output: Mitigation Action Plans                       │
│                                                              │
│ 2.9 Knowledge Graph Construction                            │
│     • Create document node                                  │
│     • Create requirement nodes                              │
│     • Create "defines" edges (document → requirements)      │
│     • Create "refers_to" edges (cross-references)           │
│     • Update global knowledge graph                         │
│     • Output: Graph nodes and edges                         │
│                                                              │
│ 2.10 Persistence                                            │
│     • Insert document record (already exists)               │
│     • Insert requirements into database                     │
│     • Insert MAPs into database                             │
│     • Create assignments (requirement + department links)   │
│     • Insert graph nodes and edges                          │
│     • Insert cross-references                               │
│     • Mark document as "processed"                          │
│     • Generate processing report                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Review Pipeline Results                             │
│ • HEAD_OFFICE views processing report                       │
│ • Statistics: N requirements extracted, M MAPs generated    │
│ • Department impact summary                                 │
│ • Knowledge graph updated with X new nodes                  │
│ • Can drill down into specific requirements/MAPs            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Assignment Review (Assignment Center)               │
│ • HEAD_OFFICE reviews auto-generated assignments            │
│ • Grouped by department                                     │
│ • Can modify: priority, due date, assigned department       │
│ • Can reassign or split assignments                         │
│ • Assignments initially in "Draft" status                   │
│ • Can add remarks or context                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Publish Assignments                                 │
│ • HEAD_OFFICE publishes assignments per department          │
│ • Status changes: Draft → Published                         │
│ • Departments can now see their assignments                 │
│ • Email/notification sent (future: notification system)     │
│ • Audit log records publication                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Executive Dashboard Updated                         │
│ • Real-time metrics updated automatically                   │
│ • Total requirements: +N from this circular                 │
│ • Published assignments: +M                                 │
│ • Department risk scores recalculated                       │
│ • Compliance gaps identified                                │
│ • Upcoming deadlines added                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ DEPARTMENT User: Compliance Officer                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 7: View Department Workspace                           │
│ • Logs in with department credentials                       │
│ • Sees only their department's assignments                  │
│ • Filtered by status: Pending, In Progress, Completed       │
│ • Sorted by priority and due date                           │
│ • Can view full requirement text and MAP details            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 8: Work on Assignment                                  │
│ • Opens specific assignment                                 │
│ • Views: Requirement text, MAP recommendations, deadline    │
│ • Searches similar requirements (semantic search)           │
│ • Explores knowledge graph (what else references this?)     │
│ • Updates status: Pending → In Progress                     │
│ • Adds progress notes                                       │
│ • Uploads evidence documents (future)                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 9: Mark as Completed                                   │
│ • Department user marks assignment complete                 │
│ • Status: In Progress → Completed                           │
│ • Completion timestamp recorded                             │
│ • Audit trail updated                                       │
│ • Dashboard metrics updated in real-time                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ EXECUTIVE User: Chief Compliance Officer                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 10: Monitor Compliance (Executive Dashboard)           │
│ • Views organization-wide compliance status                 │
│ • Key metrics: Total requirements, completion %, risk score │
│ • Department heatmap: Which departments are overloaded?     │
│ • Upcoming deadlines and overdue items                      │
│ • Trend analysis: Compliance trajectory over time           │
│ • Exports executive reports for board meetings              │
└─────────────────────────────────────────────────────────────┘

### 2.2 Semantic Search Journey

```
┌─────────────────────────────────────────────────────────────┐
│ User: Any authenticated user                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Enter Natural Language Query                        │
│ • Example: "What are KYC requirements for customer onboarding?" │
│ • System generates query embedding using same model         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Vector Similarity Search                            │
│ • ChromaDB performs similarity search                       │
│ • Returns top-K most similar requirements (K=20)            │
│ • Includes similarity scores (0-1)                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Metadata Filtering                                  │
│ • User applies filters: Domain, Priority, Obligation Type   │
│ • System refines results based on metadata                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: View Results                                        │
│ • Ranked list of requirements with similarity scores        │
│ • Highlights matching terms                                 │
│ • Shows source circular, domain, priority                   │
│ • Can click to view full requirement details                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Explore Relationships (Optional)                    │
│ • From requirement detail, view knowledge graph             │
│ • See what circulars reference this requirement             │
│ • See related MAPs and assignments                          │
│ • Understand compliance context                             │
└─────────────────────────────────────────────────────────────┘

### 2.3 Knowledge Graph Journey

```
┌─────────────────────────────────────────────────────────────┐
│ User: Any authenticated user                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Open Global Knowledge Graph                         │
│ • Interactive visualization of entire regulatory corpus     │
│ • Nodes: All circulars, requirements, MAPs, departments     │
│ • Edges: defines, refers_to, generates, assigned_to         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Navigate and Filter                                 │
│ • Filter by domain (show only KYC nodes)                    │
│ • Filter by time period (show 2024 circulars)               │
│ • Search for specific circular or requirement               │
│ • Zoom and pan to explore clusters                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Click Node for Details                              │
│ • View full text (requirement, circular excerpt)            │
│ • See connected nodes (what references this?)               │
│ • View MAP details if applicable                            │
│ • See assignment status (who's working on this?)            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Trace Regulatory Lineage                            │
│ • Understand how requirements evolved over time             │
│ • Identify superseded vs active requirements                │
│ • See which departments are impacted                        │
│ • Export subgraph for documentation                         │
└─────────────────────────────────────────────────────────────┘

---

## 3. Canonical Business Entities

### 3.1 Document

**Business Definition:**  
An RBI regulatory document (circular, notification, master direction, or guideline) uploaded for compliance processing.

**Purpose:**  
Source of regulatory requirements. Container for extracted obligations.

**Lifecycle:**
1. **Uploaded** - File received, metadata recorded
2. **Processing** - AI pipeline extracting requirements
3. **Processed** - Extraction complete, requirements available
4. **Archived** - Historical reference, no longer active (future)

**Attributes:**
- `id` (integer, PK)
- `document_id` (string, semantic ID, e.g., "RBI_2024_123")
- `original_filename` (string)
- `file_path` (string, storage location)
- `file_size` (integer, bytes)
- `document_type` (enum: Circular, Notification, Master_Direction, Guideline)
- `uploaded_by` (FK: users.id)
- `uploaded_at` (timestamp)
- `processed` (boolean)
- `processed_at` (timestamp, nullable)
- `processing_status` (enum: Pending, Processing, Completed, Failed)
- `processing_error` (text, nullable)
- `circular_number` (string, extracted, nullable, e.g., "RBI/2024/123")
- `issue_date` (date, extracted, nullable)
- `subject` (text, extracted, nullable)

**Relationships:**
- 1 Document → Many Requirements (one-to-many)
- 1 Document → 1 Knowledge Graph Node (one-to-one)
- 1 Document → Many Cross-References (one-to-many, as source)
- 1 Document → 1 User (uploaded_by)

**Database:** `documents` table in PostgreSQL/SQLite

---

### 3.2 Requirement

**Business Definition:**  
A specific regulatory obligation, rule, or guideline extracted from an RBI document that mandates, recommends, or prohibits a specific action or condition.

**Purpose:**  
Atomic unit of compliance. Assigned to departments for implementation. Searchable via semantic search.

**Lifecycle:**
1. **Extracted** - AI pipeline identifies requirement text
2. **Classified** - Domain, obligation type, priority assigned
3. **Assigned** - Linked to one or more departments
4. **Active** - Current compliance obligation
5. **Superseded** - Replaced by newer requirement (future)
6. **Archived** - No longer applicable (future)

**Attributes:**
- `id` (integer, PK)
- `requirement_id` (string, semantic ID, unique, e.g., "REQ_RBI2024123_0042")
- `document_id` (FK: documents.id)
- `text` (text, full requirement text, NOT NULL)
- `context` (text, surrounding text for clarity, nullable)
- `domain` (enum: KYC, AML, Cybersecurity, Risk_Management, Treasury, Operations, Legal, Governance, Reporting, Data_Privacy, General)
- `obligation_type` (enum: Mandatory, Recommended, Conditional, Prohibited, Informational)
- `priority` (enum: Critical, High, Medium, Low)
- `deadline_text` (text, extracted deadline phrase, nullable)
- `deadline_date` (date, parsed deadline, nullable)
- `source_section` (string, section/clause reference, nullable)
- `page_number` (integer, nullable)
- `extracted_at` (timestamp)
- `confidence_score` (float, extraction confidence, 0-1)

**Relationships:**
- Many Requirements → 1 Document (many-to-one)
- 1 Requirement → Many Assignments (one-to-many, can be assigned to multiple departments)
- 1 Requirement → 1 MAP (one-to-one, each requirement generates one MAP)
- 1 Requirement → 1 Knowledge Graph Node (one-to-one)
- 1 Requirement → 1 Vector Embedding (one-to-one, in vector DB)

**Database:** `requirements` table in PostgreSQL/SQLite  
**Vector DB:** ChromaDB collection `requirement_embeddings`

---

### 3.3 Mitigation Action Plan (MAP)

**Business Definition:**  
A structured action plan describing how to implement or comply with a specific regulatory requirement, including recommended steps, resources, and timeline.

**Purpose:**  
Transform regulatory obligation into actionable implementation guidance. Provides departments with concrete steps beyond just the requirement text.

**Lifecycle:**
1. **Generated** - AI/template generates MAP from requirement
2. **Draft** - Awaiting review
3. **Reviewed** - Validated by compliance analyst
4. **Published** - Available to departments
5. **Active** - Being implemented
6. **Completed** - Implementation finished

**Attributes:**
- `id` (integer, PK)
- `map_id` (string, semantic ID, unique, e.g., "MAP_REQ_RBI2024123_0042")
- `requirement_id` (FK: requirements.id, unique, NOT NULL)
- `title` (string, concise action title)
- `description` (text, detailed explanation)
- `mitigation_actions` (JSON array, list of specific actions)
  ```json
  [
    {"action": "Update KYC policy document", "owner": "Compliance Team", "timeline": "2 weeks"},
    {"action": "Train branch staff", "owner": "Training Dept", "timeline": "4 weeks"}
  ]
  ```
- `estimated_effort` (string, e.g., "40 person-hours", "2 weeks")
- `resources_required` (text, people, tools, budget)
- `impact_score` (float, business impact assessment, 0-10)
- `complexity` (enum: Low, Medium, High, Very_High)
- `priority` (enum: Critical, High, Medium, Low, inherits from requirement)
- `generated_by` (enum: AI_Template, AI_LLM, Manual)
- `generated_at` (timestamp)
- `reviewed_by` (FK: users.id, nullable)
- `reviewed_at` (timestamp, nullable)
- `status` (enum: Draft, Reviewed, Published, Active, Completed)

**Relationships:**
- 1 MAP → 1 Requirement (one-to-one, each MAP implements one requirement)
- 1 MAP → Many Assignments (one-to-many, MAP can be assigned to multiple departments)
- 1 MAP → 1 Knowledge Graph Node (one-to-one)

**Database:** `maps` table in PostgreSQL/SQLite

---

### 3.4 Assignment

**Business Definition:**  
The operational task linking a specific requirement (via its MAP) to a department for implementation, with ownership, status tracking, and completion metadata.

**Purpose:**  
Workflow management. Tracks who is responsible for implementing what, current status, and completion.

**Lifecycle:**
1. **Draft** - Auto-generated, awaiting publication
2. **Published** - Visible to department, ready to work
3. **Pending** - Department has not started
4. **In Progress** - Department actively working
5. **Completed** - Department finished implementation
6. **Verified** - HEAD_OFFICE verified completion (future)

**Attributes:**
- `id` (integer, PK)
- `map_id` (FK: maps.id)
- `department_id` (FK: departments.id)
- `assigned_by` (FK: users.id, HEAD_OFFICE user)
- `assigned_at` (timestamp)
- `is_published` (boolean, draft vs published)
- `published_at` (timestamp, nullable)
- `status` (enum: Pending, In_Progress, Completed, Verified)
- `priority` (enum: Critical, High, Medium, Low, can override MAP priority)
- `due_date` (date, operational deadline)
- `started_at` (timestamp, nullable)
- `completed_at` (timestamp, nullable)
- `completed_by` (FK: users.id, nullable)
- `remarks` (text, notes from department or HEAD_OFFICE)
- `updated_at` (timestamp)

**Relationships:**
- Many Assignments → 1 MAP (many-to-one)
- Many Assignments → 1 Department (many-to-one)
- Many Assignments → 1 User (assigned_by)
- 1 Assignment → Many Status History (one-to-many, audit trail)

**Business Rules:**
- One MAP can be assigned to multiple departments (e.g., KYC requirement impacts both Compliance and Operations)
- One department can have many assignments
- Assignment can only be modified by HEAD_OFFICE or owning department

**Database:** `assignments` table in PostgreSQL/SQLite

---

### 3.5 Department

**Business Definition:**  
An organizational unit within the financial institution responsible for compliance with specific regulatory domains.

**Purpose:**  
Organize compliance responsibilities. Route assignments. Calculate risk. Provide isolation between department users.

**Lifecycle:**  
Static (created during setup, rarely changes)

**Attributes:**
- `id` (integer, PK)
- `code` (string, unique, short code, e.g., "COMP", "RISK", "IT")
- `name` (string, unique, display name, e.g., "Compliance Department")
- `description` (text, nullable)
- `primary_domains` (JSON array, main focus areas)
  ```json
  ["KYC", "AML", "Reporting"]
  ```
- `head_email` (string, department head contact, nullable)
- `is_active` (boolean, for future soft-deletion)

**Relationships:**
- 1 Department → Many Assignments (one-to-many)
- 1 Department → Many Users (one-to-many, department members)
- 1 Department → 1 Knowledge Graph Node (one-to-one)

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

**Database:** `departments` table in PostgreSQL/SQLite (seed data)

---

### 3.6 Knowledge Graph Node

**Business Definition:**  
A vertex in the regulatory knowledge graph representing a document, requirement, MAP, or department with its metadata.

**Purpose:**  
Enable relationship mapping and traversal. Support visual graph exploration. Facilitate impact analysis.

**Lifecycle:**  
Created when entity is created, updated when entity changes, never deleted (soft delete for traceability)

**Attributes:**
- `id` (integer, PK)
- `node_id` (string, semantic ID, unique, matches entity ID)
  - Documents: `document_id` (e.g., "RBI_2024_123")
  - Requirements: `requirement_id` (e.g., "REQ_RBI2024123_0042")
  - MAPs: `map_id` (e.g., "MAP_REQ_RBI2024123_0042")
  - Departments: `dept_{code}` (e.g., "dept_COMP")
- `node_type` (enum: Document, Requirement, MAP, Department)
- `entity_id` (integer, FK to corresponding table)
- `label` (string, display label for graph)
- `metadata` (JSON, type-specific metadata)
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `is_active` (boolean, for historical nodes)

**Relationships:**
- 1 Node → Many Edges (as source)
- 1 Node → Many Edges (as target)

**Database:** `graph_nodes` table in PostgreSQL/SQLite

---

### 3.7 Knowledge Graph Edge

**Business Definition:**  
A directed relationship between two nodes in the knowledge graph, representing semantic or operational connections.

**Purpose:**  
Model regulatory relationships: which circular defines which requirement, which requirement generates which MAP, cross-references between circulars.

**Lifecycle:**  
Created when relationship is established, can be updated if relationship changes, never deleted (audit trail)

**Attributes:**
- `id` (integer, PK)
- `source_node_id` (string, FK: graph_nodes.node_id)
- `target_node_id` (string, FK: graph_nodes.node_id)
- `edge_type` (enum: defines, generates, assigned_to, refers_to, supersedes, amends, consolidates)
- `label` (string, display label for graph)
- `metadata` (JSON, relationship-specific context)
- `created_at` (timestamp)
- `is_active` (boolean)

**Edge Types:**
- **defines**: Document → Requirement (circular defines requirement)
- **generates**: Requirement → MAP (requirement generates mitigation plan)
- **assigned_to**: MAP → Department (MAP assigned to department for implementation)
- **refers_to**: Document → Document (circular references another circular)
- **supersedes**: Document → Document (newer circular replaces older)
- **amends**: Document → Document (circular modifies another)
- **consolidates**: Document → Many Documents (master circular consolidates multiple)

**Relationships:**
- Many Edges → 1 Node (as source)
- Many Edges → 1 Node (as target)

**Database:** `graph_edges` table in PostgreSQL/SQLite

---

### 3.8 Cross-Reference

**Business Definition:**  
An explicit textual reference from one RBI document to another, capturing regulatory dependencies and evolution.

**Purpose:**  
Track document relationships. Enable traceability. Support impact analysis when referenced documents change.

**Lifecycle:**  
Extracted during document processing, persisted permanently for historical analysis

**Attributes:**
- `id` (integer, PK)
- `source_document_id` (FK: documents.id)
- `target_circular_number` (string, referenced circular, e.g., "RBI/2024/99")
- `target_document_id` (FK: documents.id, nullable if not in system)
- `reference_type` (enum: General_Reference, Supersedes, Amends, Consolidates, Refers_To_Section)
- `context` (text, surrounding text of reference)
- `page_number` (integer, nullable)
- `extracted_at` (timestamp)
- `confidence_score` (float, extraction confidence)

**Relationships:**
- Many Cross-References → 1 Document (source)
- Many Cross-References → 1 Document (target, nullable)

**Database:** `cross_references` table in PostgreSQL/SQLite

---

### 3.9 User

**Business Definition:**  
An authenticated person with access to the platform, belonging to either HEAD_OFFICE (admin) or a specific department.

**Purpose:**  
Authentication, authorization, audit trail, ownership tracking

**Lifecycle:**  
Created during onboarding, active, can be deactivated

**Attributes:**
- `id` (integer, PK)
- `username` (string, unique)
- `email` (string, unique)
- `hashed_password` (string, bcrypt)
- `full_name` (string)
- `role` (enum: HEAD_OFFICE, DEPARTMENT)
- `department_id` (FK: departments.id, nullable for HEAD_OFFICE)
- `is_active` (boolean)
- `last_login` (timestamp, nullable)
- `created_at` (timestamp)

**Relationships:**
- 1 User → 1 Department (nullable for HEAD_OFFICE)
- 1 User → Many Assignments (assigned_by)
- 1 User → Many Documents (uploaded_by)
- 1 User → Many Audit Logs (actor)

**Database:** `users` table in PostgreSQL/SQLite

---

### 3.10 Status History

**Business Definition:**  
Audit trail of assignment status changes over time.

**Purpose:**  
Compliance audit trail, performance tracking, historical analysis

**Lifecycle:**  
Append-only, never modified or deleted

**Attributes:**
- `id` (integer, PK)
- `assignment_id` (FK: assignments.id)
- `old_status` (enum: Pending, In_Progress, Completed, Verified, nullable)
- `new_status` (enum: Pending, In_Progress, Completed, Verified)
- `changed_by` (FK: users.id)
- `changed_at` (timestamp)
- `remarks` (text, nullable)

**Database:** `status_history` table in PostgreSQL/SQLite

---

### 3.11 Audit Log

**Business Definition:**  
System-wide audit trail of all significant actions for security and compliance.

**Purpose:**  
Security monitoring, compliance audit, forensic analysis

**Lifecycle:**  
Append-only, never modified or deleted

**Attributes:**
- `id` (integer, PK)
- `user_id` (FK: users.id, nullable for system actions)
- `action` (string, e.g., "upload_document", "publish_assignments", "login")
- `entity_type` (string, e.g., "document", "assignment", "user")
- `entity_id` (integer, nullable)
- `details` (text, human-readable description)
- `ip_address` (string, nullable)
- `timestamp` (timestamp)

**Database:** `audit_logs` table in PostgreSQL/SQLite

---

### 3.12 Vector Embedding

**Business Definition:**  
Numerical vector representation of requirement text for semantic similarity search.

**Purpose:**  
Enable semantic search, find similar requirements, support AI features

**Lifecycle:**  
Generated when requirement is created, indexed immediately, updated if requirement text changes

**Attributes:**
- `id` (string, matches requirement.id)
- `embedding` (float array, 384 dimensions for all-MiniLM-L6-v2)
- `metadata` (JSON)
  ```json
  {
    "requirement_id": "REQ_RBI2024123_0042",
    "text": "Banks must implement...",
    "domain": "KYC",
    "priority": "High"
  }
  ```

**Relationships:**
- 1 Embedding → 1 Requirement (one-to-one)

**Storage:** ChromaDB collection `requirement_embeddings` (separate from main database)

---

### 3.13 Dashboard Metrics (Computed, Not Stored)

**Business Definition:**  
Real-time aggregated statistics computed on-demand from database for executive dashboards.

**Purpose:**  
Provide insights without storing redundant data

**Examples:**
- Total requirements count
- Published vs draft assignments
- Completion percentage
- Department risk scores
- Upcoming deadlines
- Priority distribution

**Lifecycle:**  
Computed via SQL aggregation queries, never persisted

**Storage:** NOT STORED, computed on-demand from database

---

## 4. Single Source of Truth

### Database (Primary Storage)

**PostgreSQL or SQLite**

All business entities:
- ✅ Users
- ✅ Departments
- ✅ Documents
- ✅ Requirements
- ✅ MAPs (mitigation_action_plans)
- ✅ Assignments
- ✅ Knowledge Graph Nodes (graph_nodes)
- ✅ Knowledge Graph Edges (graph_edges)
- ✅ Cross-References
- ✅ Status History
- ✅ Audit Logs

**Rationale:** Business data must be persistent, queryable, transactional, and auditable.

---

### Vector Database (Specialized Storage)

**ChromaDB or pgvector**

Embeddings only:
- ✅ Requirement embeddings (384-dim vectors)
- ✅ Semantic search indexes

**Rationale:** Optimized for vector similarity search, not suitable for structured business data.

**Synchronization:** Every requirement insert/update triggers embedding generation and vector DB upsert.

---

### Session Storage (Temporary UI State)

**React Context / Redux**

UI state only:
- ✅ Pipeline processing progress (percentage, current stage)
- ✅ Current user info (after login)
- ✅ Active filters (search, graph)
- ✅ UI preferences (theme, layout)
- ✅ Form draft state (before submission)

**Rationale:** Ephemeral state that doesn't need persistence.

**NOT ALLOWED in Session:**
- ❌ Business data (requirements, MAPs, assignments)
- ❌ Graph structure
- ❌ Metrics

---

### Generated Artifacts (Computed on Demand)

**Never Stored, Always Computed**

Analytics and reports:
- ✅ Dashboard metrics (COUNT queries)
- ✅ Risk scores (weighted calculation)
- ✅ Completion percentages (derived)
- ✅ Department rankings (sorted query)
- ✅ Trend charts (time-series aggregation)

**Rationale:** Always up-to-date, no stale data, no sync issues.

---

### Static Taxonomy (Seed Data)

**Migration Scripts / Seed Files**

Reference data loaded once:
- ✅ Department definitions (9 departments)
- ✅ Domain taxonomy (KYC, AML, etc.)
- ✅ Obligation types (Mandatory, Recommended, etc.)
- ✅ Priority levels (Critical, High, Medium, Low)

**Rationale:** Configuration data, rarely changes, loaded at deployment.

**NOT ALLOWED:**
- ❌ Operational requirements as seed data
- ❌ MAPs as static files
- ❌ Knowledge graph as JSON

---

### Legacy Data Migration (One-Time Import)

**Optional: Import Historical Corpus**

If organization has historical requirements:
- Import 2,941 requirements from legacy system
- Mark with `source = 'LEGACY_IMPORT'`
- Maintain as read-only reference corpus
- Enable semantic search across historical + new

**Status:** One-time migration script, not operational data source

---

## Summary: Entity Storage Location

| Entity | Database | Vector DB | Session | Generated | Seed Data |
|--------|----------|-----------|---------|-----------|-----------|
| Documents | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Requirements | ✅ PRIMARY | ✅ (embeddings) | ❌ | ❌ | ⚠️ (optional legacy) |
| MAPs | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Assignments | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Departments | ✅ PRIMARY | ❌ | ❌ | ❌ | ✅ (9 departments) |
| Graph Nodes | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Graph Edges | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Cross-References | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Users | ✅ PRIMARY | ❌ | ✅ (current user) | ❌ | ❌ |
| Status History | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Audit Logs | ✅ PRIMARY | ❌ | ❌ | ❌ | ❌ |
| Vector Embeddings | ❌ | ✅ PRIMARY | ❌ | ✅ (on insert) | ❌ |
| Dashboard Metrics | ❌ | ❌ | ❌ | ✅ (COUNT queries) | ❌ |
| Risk Scores | ❌ | ❌ | ❌ | ✅ (calculated) | ❌ |
| Pipeline Progress | ❌ | ❌ | ✅ (temporary) | ❌ | ❌ |

**Rule:** Every business entity has exactly ONE primary storage location. No dual authorities.

---

