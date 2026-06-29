# Product Specification - Data Architecture & Roadmap

---

## 7. Backend Service Architecture

### 7.1 Service Layers

```
┌────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                  │
│  Routers handle HTTP requests, auth, validation        │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│  Business logic, orchestration, complex operations     │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│               Repository/CRUD Layer                     │
│  Database queries, ORM operations, data access         │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│                  Data Layer                             │
│  PostgreSQL/SQLite + ChromaDB                          │
└────────────────────────────────────────────────────────┘
```

### 7.2 Routers (API Endpoints)

- **auth_router.py** - Authentication (login, token refresh)
- **admin_router.py** - Document upload, dashboard, user management
- **requirement_router.py** - Requirement search, details
- **map_router.py** - MAP browsing, details
- **assignment_center_router.py** - Assignment review, publishing
- **department_workspace_router.py** - Department user tasks
- **graph_router.py** - Knowledge graph queries
- **search_router.py** - Semantic search
- **report_router.py** - Export reports

### 7.3 Services

- **auth_service.py** - JWT generation, password hashing, authorization
- **pipeline_service.py** - Orchestrates AI pipeline
- **notification_service.py** - Email/alerts (future)
- **analytics_service.py** - Complex metrics computation
- **export_service.py** - Report generation

### 7.4 Repositories/CRUD

- **document_crud.py** - Document operations
- **requirement_crud.py** - Requirement operations
- **map_crud.py** - MAP operations
- **assignment_crud.py** - Assignment operations
- **graph_crud.py** - Graph operations
- **user_crud.py** - User operations

### 7.5 AI Pipeline Modules

- **text_extractor.py** - PDF text extraction
- **chunker.py** - Text chunking
- **requirement_extractor.py** - NLP requirement extraction
- **classifier.py** - Domain/priority classification
- **embedder.py** - Vector embedding generation
- **cross_ref_extractor.py** - Cross-reference detection
- **map_generator.py** - MAP generation (template or LLM)
- **graph_builder.py** - Knowledge graph construction
- **dept_assigner.py** - Department assignment logic
- **orchestrator.py** - Pipeline coordination

### 7.6 Background Tasks

- **Celery workers** for async pipeline processing
- **Redis** for task queue and caching
- **Scheduled jobs** (future): Deadline reminders, report generation

---

## 8. Data Architecture (ER Model)

### 8.1 Core Entity Relationships

```
users                          departments
  |                               |
  | uploaded_by                  | (seed data)
  ↓                               ↓
documents ─────────┐        assignments
  |                │              |
  | defines        │              | (links MAP → Dept)
  ↓                │              |
requirements       │            maps
  |                │              |
  | generates      │              | (1:1 with requirement)
  ↓                │              |
  └────────────────┴──────────────┘

Cardinalities:
• 1 User → Many Documents (uploaded_by)
• 1 Document → Many Requirements (defines)
• 1 Requirement → 1 MAP (generates)
• 1 MAP → Many Assignments (can be assigned to multiple depts)
• 1 Department → Many Assignments
• 1 User → 1 Department (nullable for HEAD_OFFICE)
```

### 8.2 Graph Tables

```
graph_nodes                graph_edges
  |                          |
  | (Document,              | (defines, generates,
  |  Requirement,            |  assigned_to, refers_to)
  |  MAP, Department)        |
  └──────────────────────────┘

Cardinalities:
• 1 Entity → 1 Graph Node (1:1)
• 1 Node → Many Edges (as source)
• 1 Node → Many Edges (as target)
```

### 8.3 Audit Tables

```
status_history               audit_logs
  |                            |
  | (tracks assignment         | (tracks all actions)
  |  status changes)           |
  |                            |
assignments                  users
```

### 8.4 Complete ER Diagram

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │
│ username    │
│ email       │
│ password    │
│ role        │
│ dept_id (FK)│
└─────────────┘
       │
       │ uploaded_by
       ↓
┌─────────────┐        ┌──────────────┐
│  documents  │────────│requirements  │
├─────────────┤1     N├──────────────┤
│ id (PK)     │        │ id (PK)      │
│ doc_id      │        │ req_id       │
│ filename    │        │ doc_id (FK)  │
│ file_path   │        │ text         │
│ processed   │        │ domain       │
└─────────────┘        │ priority     │
                       │ deadline     │
                       └──────────────┘
                              │
                              │ 1:1
                              ↓
                       ┌──────────────┐
                       │     maps     │
                       ├──────────────┤
                       │ id (PK)      │
                       │ map_id       │
                       │ req_id (FK)  │
                       │ title        │
                       │ description  │
                       │ actions      │
                       │ priority     │
                       └──────────────┘
                              │
                              │ 1:N
                              ↓
┌─────────────┐        ┌──────────────┐
│departments  │────────│ assignments  │
├─────────────┤1     N├──────────────┤
│ id (PK)     │        │ id (PK)      │
│ code        │        │ map_id (FK)  │
│ name        │        │ dept_id (FK) │
└─────────────┘        │ assigned_by  │
                       │ is_published │
                       │ status       │
                       │ due_date     │
                       └──────────────┘
                              │
                              │ 1:N
                              ↓
                       ┌──────────────┐
                       │status_history│
                       ├──────────────┤
                       │ id (PK)      │
                       │ assign_id(FK)│
                       │ old_status   │
                       │ new_status   │
                       │ changed_at   │
                       └──────────────┘

┌──────────────┐       ┌──────────────┐
│ graph_nodes  │───────│ graph_edges  │
├──────────────┤1    N├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ node_id      │       │ source (FK)  │
│ node_type    │       │ target (FK)  │
│ label        │       │ edge_type    │
│ metadata     │       │ label        │
└──────────────┘       └──────────────┘

┌─────────────────┐
│cross_references │
├─────────────────┤
│ id (PK)         │
│ source_doc (FK) │
│ target_circular │
│ reference_type  │
│ context         │
└─────────────────┘
```

---

## 9. Knowledge Graph Architecture

### 9.1 Graph Scope

**Represents:** Entire organizational regulatory corpus

**Nodes:**
- All circulars ever uploaded
- All requirements extracted
- All MAPs generated  
- All 9 departments (static)

**Edges:**
- Document → Requirements (defines)
- Requirement → MAP (generates)
- MAP → Department (assigned_to)
- Document → Document (refers_to, supersedes, amends)

### 9.2 Graph Persistence

**Storage:** PostgreSQL `graph_nodes` and `graph_edges` tables

**Updates:**
- **On document upload:** Add document node
- **On requirement extraction:** Add requirement nodes + defines edges
- **On MAP generation:** Add MAP nodes + generates edges
- **On assignment creation:** Add assigned_to edges
- **On cross-reference detection:** Add refers_to/supersedes/amends edges

**Incremental:** Graph grows with each document, never reset

### 9.3 Graph Queries

**Global Graph:**
- All nodes and edges
- Filtered by node type, domain, time period
- Paginated for performance

**Document-Scoped Graph:**
- Subgraph for specific document
- Document + its requirements + its MAPs + assigned departments
- Cross-references to/from this document

**Requirement Lineage:**
- Trace requirement evolution (superseded requirements)
- Find related requirements
- See department assignments

### 9.4 Graph Visualization

**Technology:** Cytoscape.js

**Layout:** Force-directed (automatic clustering by type/domain)

**Interaction:**
- Zoom, pan, search
- Click node → See details
- Filter by type, domain
- Export subgraph

---

## 10. Production Roadmap

### Milestone 1: Stable CRUD Platform ✅ (CURRENT STATE)

**Goal:** Establish foundation infrastructure

**Deliverables:**
- ✅ FastAPI backend with authentication
- ✅ SQLite/PostgreSQL database with core tables
- ✅ User management (HEAD_OFFICE, DEPARTMENT roles)
- ✅ Document upload functionality
- ✅ Assignment workflow (create, publish, track)
- ✅ Basic frontend pages (Dashboard, Assignment Center, Dept Workspace)
- ✅ Audit logging

**Dependencies:** None

**Effort:** Complete (existing implementation)

**Risk:** Low - Already implemented and tested

**Status:** ✅ **COMPLETE**

**Next:** Migrate to Milestone 2

---

### Milestone 2: Real AI Pipeline

**Goal:** Implement actual document processing with AI

**Deliverables:**
- Text extraction from PDF (PyMuPDF)
- Semantic chunking
- Requirement extraction (pattern-based NLP)
- Domain classification (rule-based + ML)
- Priority assignment
- Deadline extraction
- Cross-reference detection
- Department auto-assignment
- MAP generation (template-based)
- Database persistence
- Remove hardcoded samples
- Real pipeline progress tracking

**Dependencies:** Milestone 1 complete

**Estimated Effort:** 3-4 weeks

**Components:**
```
backend/pipeline/
  ├── text_extractor.py       (3 days)
  ├── chunker.py              (2 days)
  ├── requirement_extractor.py(5 days)
  ├── classifier.py           (4 days)
  ├── cross_ref_extractor.py  (3 days)
  ├── dept_assigner.py        (2 days)
  ├── map_generator.py        (4 days)
  ├── orchestrator.py         (3 days)
  └── tests/                  (4 days)
```

**Risk:** Medium
- NLP accuracy may need tuning
- PDF parsing edge cases
- Performance with large documents

**Success Criteria:**
- Pipeline extracts 70%+ requirements accurately
- Zero hardcoded samples
- Real-time progress tracking
- Frontend shows actual pipeline results (not demo data)

---

### Milestone 3: Knowledge Graph & Persistence

**Goal:** Persistent knowledge graph with visualization

**Deliverables:**
- Database tables: graph_nodes, graph_edges
- Graph builder module
- Graph persistence during pipeline
- Graph API endpoints
- Frontend graph visualization (Cytoscape.js)
- Graph search and filtering
- Historical graph viewing

**Dependencies:** Milestone 2 complete (pipeline creates requirements/MAPs)

**Estimated Effort:** 2-3 weeks

**Components:**
```
backend/
  ├── models.py (add GraphNode, GraphEdge)
  ├── pipeline/graph_builder.py   (4 days)
  ├── routers/graph_router.py     (3 days)
  ├── crud/graph_crud.py          (2 days)

frontend/dashboard/src/pages/
  └── Graph.jsx (Cytoscape integration) (5 days)
```

**Risk:** Medium
- Graph size scalability (1000+ nodes)
- Visualization performance
- Edge case: circular dependencies

**Success Criteria:**
- All documents have graph representation
- Graph updates incrementally
- Users can visualize and explore relationships
- No session dependency for graph data

---

### Milestone 4: Semantic Search & Vector Database

**Goal:** Natural language search across requirements

**Deliverables:**
- ChromaDB setup and integration
- Embedding generation (Sentence Transformers)
- Vector database indexing
- Semantic search API
- Semantic search UI
- Similarity-based recommendations

**Dependencies:** Milestone 2 complete (requirements exist)

**Estimated Effort:** 2 weeks

**Components:**
```
backend/
  ├── pipeline/embedder.py         (3 days)
  ├── routers/search_router.py     (3 days)
  ├── services/vector_search.py    (3 days)

frontend/dashboard/src/pages/
  └── SemanticSearch.jsx           (3 days)
```

**Technology:**
- ChromaDB (persistent, offline)
- Sentence Transformers (all-MiniLM-L6-v2)

**Risk:** Low-Medium
- Embedding generation performance
- Vector DB size management
- Search accuracy tuning

**Success Criteria:**
- Users can search with natural language
- Top-K results ranked by similarity
- Filters by domain, priority work
- Search speed < 500ms

---

### Milestone 5: Executive Intelligence & Analytics

**Goal:** Advanced analytics and reporting

**Deliverables:**
- Department risk scoring algorithm
- Trend analysis (time-series metrics)
- Predictive analytics (deadline risk)
- Compliance gap analysis
- Executive report generation (PDF)
- Email notifications system
- Deadline reminder system
- Advanced dashboard charts

**Dependencies:** Milestones 2, 3, 4 complete

**Estimated Effort:** 3 weeks

**Components:**
```
backend/services/
  ├── analytics_service.py       (5 days)
  ├── risk_scoring.py            (3 days)
  ├── report_generator.py        (4 days)
  ├── notification_service.py    (3 days)

frontend/dashboard/src/pages/
  ├── Analytics.jsx              (4 days)
  └── Reports.jsx                (2 days)
```

**Risk:** Low
- Report generation complexity
- Email delivery (SMTP configuration)

**Success Criteria:**
- Executives get actionable insights
- Risk scores guide prioritization
- Automated reporting reduces manual work

---

### Milestone 6: Production Hardening (Future)

**Goal:** Production-ready deployment

**Deliverables:**
- PostgreSQL migration (from SQLite)
- Redis caching
- Celery background workers
- API rate limiting
- Security hardening
- Performance optimization
- Comprehensive test coverage (80%+)
- Load testing
- Deployment documentation
- Backup and recovery procedures
- Monitoring and alerting

**Dependencies:** Milestones 1-5 complete

**Estimated Effort:** 4 weeks

**Risk:** Medium
- Infrastructure setup
- Performance bottlenecks
- Security vulnerabilities

---

## Roadmap Timeline

```
Quarter 1 (Months 1-3):
  ├─ M1: Stable CRUD Platform        ✅ COMPLETE
  ├─ M2: Real AI Pipeline             [Weeks 1-4]
  └─ M3: Knowledge Graph              [Weeks 5-7]

Quarter 2 (Months 4-6):
  ├─ M4: Semantic Search              [Weeks 8-9]
  ├─ M5: Executive Intelligence       [Weeks 10-12]
  └─ Testing and Refinement           [Week 13]

Quarter 3 (Months 7-9):
  └─ M6: Production Hardening         [Weeks 14-17]
  └─ Pilot Deployment                 [Week 18]

Quarter 4 (Months 10-12):
  └─ Production Launch
  └─ User Training
  └─ Feedback and Iteration
```

**Critical Path:** M1 → M2 → M3 → M4 → M5 → M6

**Minimum Viable Product (MVP):** Milestones 1-4
**Full Production:** Milestones 1-6

---

## Implementation Priorities

### CRITICAL (Block subsequent work)
1. ✅ Milestone 1: Foundation infrastructure
2. ⏳ Milestone 2: Real AI pipeline (removes fake demo)

### HIGH (Core product value)
3. Milestone 3: Knowledge graph (key differentiator)
4. Milestone 4: Semantic search (AI-powered feature)

### MEDIUM (Enhanced capabilities)
5. Milestone 5: Advanced analytics

### LOW (Production readiness)
6. Milestone 6: Infrastructure hardening

---

## Success Metrics

**Technical Metrics:**
- Requirement extraction accuracy: >70%
- Pipeline processing time: <2 minutes per document
- Semantic search response time: <500ms
- System uptime: >99%
- Test coverage: >80%

**Business Metrics:**
- Departments using system: 9/9 (100%)
- Requirements processed: >100 circulars in first year
- User satisfaction: >4/5
- Time saved vs manual process: >60%
- Compliance tracking efficiency: >80% visibility

---

## Conclusion

This specification defines the target architecture unconstrained by current implementation. All future work must conform to this specification. The roadmap provides a clear path from current state (Milestone 1 complete) to full production (Milestone 6).

**Next Steps:**
1. Stakeholder review and approval of this specification
2. Begin Milestone 2 implementation (Real AI Pipeline)
3. Remove all demo data dependencies
4. Establish database as single source of truth

