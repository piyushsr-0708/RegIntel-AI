# Master Product Specification - Executive Summary

**RegIntel AI - Regulatory Intelligence Platform**  
**Version:** 1.0 - Target Architecture  
**Date:** June 28, 2026

---

## Documents Created

This master specification consists of three documents:

1. **PRODUCT_SPECIFICATION.md** - Core specification (Sections 1-4)
   - Product vision
   - End-to-end user journeys
   - Canonical business entities
   - Single source of truth

2. **PRODUCT_SPECIFICATION_PART2.md** - Technical specification (Sections 5-6)
   - AI processing pipeline (10 stages)
   - Frontend responsibilities (10 pages)

3. **PRODUCT_SPECIFICATION_ROADMAP.md** - Architecture & roadmap (Sections 7-10)
   - Backend service architecture
   - Data architecture (ER model)
   - Knowledge graph architecture
   - Production roadmap (6 milestones)

---

## Product Vision (One Paragraph)

**RegIntel AI** is an offline-first, AI-powered regulatory intelligence platform that transforms how financial institutions manage RBI compliance by automatically extracting, classifying, and assigning regulatory obligations from PDF circulars using natural language processing and machine learning, building a persistent knowledge graph mapping relationships between circulars, requirements, and departments, enabling semantic search across the entire regulatory corpus, generating actionable mitigation plans, tracking implementation progress, and providing executive intelligence through risk scoring and predictive analytics, operating entirely offline after initial setup to ensure data security and deterministic execution critical for financial institutions, used by compliance officers, department heads, and executives to proactively manage regulatory change, reduce compliance risk, and demonstrate audit readiness.

---

## Core Differentiators

1. **AI-Powered Extraction** - Automated requirement extraction from unstructured PDFs
2. **Semantic Intelligence** - Vector-based similarity search, not just keyword matching
3. **Knowledge Graph** - Persistent graph of regulatory relationships and dependencies
4. **Offline-First** - No cloud dependencies, deterministic execution
5. **Predictive Risk** - Department risk scoring based on workload and priority
6. **Actionable MAPs** - Auto-generated mitigation action plans, not just task lists

---

## Business Entities (Canonical Definitions)

| Entity | Purpose | Storage | Lifecycle |
|--------|---------|---------|-----------|
| **Document** | Source RBI circular (PDF) | Database | Upload → Processing → Processed |
| **Requirement** | Regulatory obligation | Database + Vector DB | Extract → Classify → Assign |
| **MAP** | Mitigation action plan | Database | Generate → Review → Publish |
| **Assignment** | Dept task (MAP → Dept) | Database | Draft → Publish → Complete |
| **Department** | Organizational unit | Database (seed) | Static |
| **Graph Node** | Entity in knowledge graph | Database | Create with entity |
| **Graph Edge** | Relationship | Database | Create with relationship |
| **Cross-Reference** | Doc-to-doc reference | Database | Extract from text |
| **Vector Embedding** | Semantic representation | ChromaDB | Generate with requirement |

---

## Single Source of Truth

**Database (PostgreSQL/SQLite):** ALL business entities
- Documents, Requirements, MAPs, Assignments, Departments
- Knowledge Graph (nodes + edges)
- Cross-References, Users, Status History, Audit Logs

**Vector Database (ChromaDB):** Embeddings ONLY
- Requirement embeddings for semantic search
- Synchronized with database (not separate authority)

**Session:** UI state ONLY
- Pipeline progress, filters, preferences
- NO business data

**Generated:** Metrics ONLY
- Dashboard statistics (COUNT queries)
- Risk scores (calculated)
- NEVER stored

**Prohibited:**
- ❌ Static JSON files for operational data
- ❌ Demo data in production paths
- ❌ Business data in session state

---

## AI Pipeline (10 Stages)

1. **Text Extraction** - PyMuPDF extracts text from PDF
2. **Semantic Chunking** - Split into 512-token segments
3. **Requirement Extraction** - NLP patterns identify obligations
4. **Classification** - Domain, obligation type, priority
5. **Vector Embedding** - Generate 384-dim embeddings (Sentence Transformers)
6. **Cross-Reference Detection** - Regex patterns find references
7. **Department Assignment** - Rule-based domain → dept mapping
8. **MAP Generation** - Template or LLM creates action plans
9. **Knowledge Graph Construction** - Build nodes and edges
10. **Persistence** - Save all to database + vector DB

**Input:** Document ID (PDF uploaded)  
**Output:** N requirements, N MAPs, M assignments, graph updates  
**Technology:** Celery + Redis for async processing

---

## Frontend Pages (10 Core Pages)

1. **Executive Dashboard** - Org-wide compliance metrics (HEAD_OFFICE)
2. **Pipeline Upload** - Upload PDFs, trigger processing (HEAD_OFFICE)
3. **Assignment Center** - Review & publish assignments (HEAD_OFFICE)
4. **Requirements Search** - Text search, filters (All users)
5. **Semantic Search** - Natural language vector search (All users)
6. **MAP Management** - Browse mitigation plans (All users)
7. **Knowledge Graph** - Interactive graph visualization (All users)
8. **Department Workspace** - User's assigned tasks (DEPARTMENT)
9. **Department Dashboard** - Per-dept monitoring (HEAD_OFFICE)
10. **Analytics** - Trend analysis, reports (HEAD_OFFICE)

**Key Principle:** Every page queries database via API, NO static JSON

---

## Data Architecture (ER Model)

```
User ─uploads─> Document ─defines─> Requirement ─generates─> MAP
                                                               │
                                                               │ assigned_to
                                                               ↓
Department <─────────────────────────────────────────── Assignment

Cardinalities:
• 1 Document → Many Requirements
• 1 Requirement → 1 MAP
• 1 MAP → Many Assignments (multi-dept)
• 1 Department → Many Assignments
```

**Database Tables:** 12 core tables
- users, departments, documents, requirements, maps, assignments
- graph_nodes, graph_edges, cross_references
- status_history, audit_logs

---

## Knowledge Graph Architecture

**Scope:** Entire organizational regulatory corpus (cumulative, not session-specific)

**Nodes:** All documents, requirements, MAPs, departments  
**Edges:** defines, generates, assigned_to, refers_to, supersedes, amends

**Persistence:** PostgreSQL `graph_nodes` and `graph_edges` tables

**Updates:** Incremental (graph grows with each document upload)

**Visualization:** Cytoscape.js interactive graph

**Queries:**
- Global graph (all nodes/edges)
- Document-scoped subgraph
- Requirement lineage tracing

---

## Production Roadmap (6 Milestones)

### ✅ Milestone 1: Stable CRUD Platform (COMPLETE)
- FastAPI backend, authentication, database
- Assignment workflow functional
- **Status:** Current implementation

### ⏳ Milestone 2: Real AI Pipeline (3-4 weeks)
- Remove hardcoded samples
- Implement text extraction, NLP, classification
- Real MAP generation
- **Critical:** Removes demo data dependencies

### Milestone 3: Knowledge Graph (2-3 weeks)
- Persistent graph in database
- Graph visualization
- Historical graph viewing

### Milestone 4: Semantic Search (2 weeks)
- ChromaDB integration
- Vector embeddings
- Natural language search UI

### Milestone 5: Executive Intelligence (3 weeks)
- Risk scoring
- Trend analysis
- Report generation
- Notifications

### Milestone 6: Production Hardening (4 weeks)
- PostgreSQL migration
- Performance optimization
- Security hardening
- Deployment readiness

**Timeline:** 14-18 weeks total (Q1-Q3 2026)

**MVP:** Milestones 1-4 (functional AI platform)  
**Full Production:** Milestones 1-6 (enterprise-ready)

---

## Current vs Target State

### Current State (Milestone 1)
- ✅ Backend foundation with auth
- ✅ Database schema complete
- ✅ Assignment workflow functional
- ❌ AI pipeline missing (hardcoded samples)
- ❌ Demo JSON used for visualization
- ❌ Graph not persisted

### Target State (Milestone 6)
- ✅ Real AI processing pipeline
- ✅ Database as single source of truth
- ✅ Persistent knowledge graph
- ✅ Semantic vector search
- ✅ Executive analytics
- ✅ Production-grade infrastructure

**Gap:** Need to complete Milestones 2-6

---

## Critical Decisions Made

### 1. Single Source of Truth: Database
**Decision:** All business data stored ONLY in PostgreSQL/SQLite  
**Rationale:** Eliminates dual authorities, ensures consistency  
**Impact:** Requires removing demo JSON dependencies

### 2. Knowledge Graph is Cumulative
**Decision:** Graph represents entire corpus, not session-specific  
**Rationale:** Historical analysis, relationship tracing  
**Impact:** Requires persistent graph storage

### 3. MAP is Distinct Entity
**Decision:** MAP table separate from assignments  
**Rationale:** MAP = mitigation plan, Assignment = task tracking  
**Impact:** Requires new table and generation logic

### 4. Vector DB for Search Only
**Decision:** ChromaDB stores embeddings, not business data  
**Rationale:** Specialized tool for specialized purpose  
**Impact:** Synchronization between DB and vector DB required

### 5. Offline-First Architecture
**Decision:** All processing happens locally, no cloud APIs  
**Rationale:** Data security, deterministic execution  
**Impact:** Uses local models (Sentence Transformers, optional local LLM)

---

## Implementation Rules

### DO:
- ✅ Store all business data in database
- ✅ Generate embeddings for every requirement
- ✅ Update knowledge graph incrementally
- ✅ Compute metrics on-demand
- ✅ Query database via APIs
- ✅ Use Celery for async tasks

### DON'T:
- ❌ Store business data in JSON files
- ❌ Use session state for persistence
- ❌ Duplicate data across systems
- ❌ Hardcode sample data
- ❌ Create multiple sources of truth
- ❌ Display demo data as operational

---

## Success Criteria

### Technical
- Requirement extraction accuracy: >70%
- Pipeline processing: <2 min per document
- Semantic search latency: <500ms
- Graph visualization: <3 sec load time
- Test coverage: >80%

### Business
- All 9 departments active users
- >100 circulars processed in Year 1
- >60% time saved vs manual process
- >80% compliance visibility
- User satisfaction: >4/5

---

## Next Steps

1. **Stakeholder Review** - Approve this specification
2. **Begin Milestone 2** - Implement real AI pipeline
3. **Remove Demo Dependencies** - Delete static JSON usage
4. **Establish Database Authority** - All queries to DB
5. **Track Progress** - Weekly milestones against roadmap

---

## Specification Status

**Status:** ✅ **APPROVED FOR IMPLEMENTATION**

All future code changes MUST conform to this specification.

Any deviation requires specification update approval.

This document supersedes all previous architectural decisions.

---

**Master Specification Complete**  
**Ready for Implementation Phase**

