# Architecture Intent Validation Pass

**Date:** June 28, 2026  
**Purpose:** Determine what this system is **supposed to be**, not merely what it currently does  
**Approach:** Critical evaluation against stated product vision

---

## Executive Summary

After comparing the **stated product vision** against the **actual implementation**, I have identified **fundamental architectural contradictions** that indicate the current system is in a **transitional state**, not a coherent production architecture.

### Critical Finding

**The README describes an AI-powered regulatory intelligence platform. The actual implementation is a basic CRUD workflow system with disconnected demo visualizations.**

**Confidence:** This is **NOT intentional hybrid architecture**. This is incomplete migration.

---

## Part 1: Product Vision vs Reality

### Stated Product Vision (README.md)

**"RegIntel AI - Offline Agentic Regulatory Intelligence Platform"**

**Core Value Proposition:**
- AI-powered semantic search over 2,941 RBI requirements
- Knowledge graph with relationship mapping
- Automated requirement extraction from PDFs
- Department risk analysis
- Vector database (ChromaDB) with offline-first operation

**Expected Workflow (README Section):**
```
Document Upload → Text Extraction → Requirement Extraction → 
Requirement Classification → Department Assignment → MAP Generation → 
Persistence → Dashboard / Search / Graph / Reports
```

### Actual Implementation (Validated)

**Backend Reality:**
```python
# admin_router.py Line 76-187
Document Upload → Create 14 hardcoded sample requirements → 
Create 14 assignments → END
```

**No AI processing. No text extraction. No classification. No MAP generation.**


---

## Part 2: Component Classification

### Backend FastAPI Application

**Status:** ✅ **Production Implementation**

**Evidence:**
- Complete REST API with authentication
- SQLite database with proper schema
- CRUD operations functional
- JWT token security
- Role-based access control

**Purpose:** Operational workflow management

**Assessment:** This is real, functioning production code for assignment tracking.

---

### Python AI Pipeline Scripts

**Status:** ❌ **MISSING - Documentation Only**

**Expected (per README):**
- `extract_text.py` - PDF text extraction
- `chunk_documents.py` - Document chunking
- `extract_requirements_v2.py` - Requirement extraction
- `taxonomy_builder.py` - Classification
- `build_vector_db.py` - Vector database creation
- `cross_reference_parser.py` - Cross-reference extraction
- `reference_graph_v2.py` - Knowledge graph building
- `map_generator.py` - MAP generation
- `map_dashboard_feed.py` - Dashboard data generation

**Reality:**
```bash
# File search results:
No files found matching: extract_requirements, taxonomy_builder, map_generator
```

**Assessment:** These scripts **DO NOT EXIST** in the repository. README is outdated or aspirational.

---

### Demo JSON Files (2,941 items)

**Status:** ⚠️ **Legacy Demo Data / Proof of Concept Artifact**

**Files:**
- `requirements_taxonomy.json` (2,941 items)
- `maps_output.json` (2,941 items)
- `map_details.json` (metadata)
- `dashboard_metrics.json`
- `department_heatmap.json`

**Evidence:**
1. **Pre-generated:** Static JSON files, no generation pipeline exists
2. **Not updated:** Pipeline creates 14 DB records but JSON unchanged
3. **Disconnected:** No code synchronizes DB → JSON
4. **High quality:** Production-grade RBI data suggests prior work

**Most Likely Origin:**
- **Phase 0** (Pre-backend): AI pipeline generated these files
- **Phase 1** (Backend): Added FastAPI + Database + Auth
- **Phase 2**: Integrated UI with backend
- **Current State**: JSON left over from Phase 0, never migrated

**Assessment:** This is **legacy proof-of-concept data**, not production taxonomy.


---

### Frontend Analysis Session

**Status:** ❌ **Demo/Placeholder Implementation**

**Code:** `AnalysisSession.jsx` Lines 11-138

**What it does:**
- Filters demo JSON based on filename hash
- Generates fake "analysis" from pre-generated data
- Creates artificial statistics
- Simulates AI processing without calling any AI

**Evidence:**
```javascript
// Line 15: Deterministic demo data generation
let hash = 0;
for (let i = 0; i < fileName.length; i++) 
    hash = ((hash << 5) - hash + fileName.charCodeAt(i)) | 0;
// Picks demo data based on hash, not actual processing
```

**Assessment:** This is a **placeholder visualization** simulating future AI functionality.

---

### Pipeline Processing UI

**Status:** ❌ **Visual Theater / Demo Simulation**

**Code:** `Pipeline.jsx` Lines 250-350

**What it does:**
1. Shows 9 stages: "Text Extraction", "Requirement Extraction", "MAP Generation", etc.
2. Displays progress bars and timers
3. Shows "205 Requirements Extracted", "9 Departments Impacted"
4. **Reality:** Creates 14 hardcoded assignments in background

**Evidence:**
```javascript
// Line 280: Visual stages (9 stages shown)
const STAGES = [
  "Circular Loaded", "Text Extraction", "Requirement Extraction",
  "Requirement Classification", "Cross-reference Analysis",
  "Knowledge Graph Construction", "Department Assignment",
  "MAP Generation", "Dashboard Ready"
];

// But actual backend call:
const processResponse = await api.post(`/admin/process-document/${documentId}`);
// Creates 14 hardcoded sample requirements only
```

**Assessment:** This is **misleading UI** that simulates AI processing without performing it.

---

### Knowledge Graph Visualization

**Status:** ⚠️ **Demo Data Visualization (Static)**

**Code:** `Graph.jsx`, `AnalysisSession.jsx`

**What it shows:**
- Nodes: Circulars, Requirements, MAPs, Departments
- Edges: defines, generates, assigned
- Built from demo JSON files

**What's missing:**
- No database persistence
- No actual cross-reference extraction
- No graph generation from uploaded documents
- Uses pre-generated graph from Phase 0

**Assessment:** This is a **static visualization** of pre-computed demo graph, not dynamic graph generation.


---

### Assignment Center & Department Workflow

**Status:** ✅ **Production Implementation**

**Evidence:**
- Real database queries
- Publish workflow functional
- Status tracking works
- Department users can update tasks

**Assessment:** This is **genuine operational functionality**.

---

### Requirements Search Page

**Status:** ❌ **Demo Mode Only**

**Code:** `Requirements.jsx` Line 11

```javascript
import { requirementsTaxonomy } from "../data/demo";
// Uses static JSON, no API
```

**Assessment:** This is **read-only demo data browsing**, not production search.

---

### MAP Management Page

**Status:** ❌ **Demo Mode Only**

**Code:** `Maps.jsx` Line 40

```javascript
const mapsOutput = isDocumentScoped && hasSession 
  ? session.analysis.maps      // Filtered demo
  : globalMapsOutput;          // Full demo (2941 items)
```

**Assessment:** This is **demo data browser**, disconnected from assignments database.

---

## Part 3: Architectural Contradictions

### Contradiction 1: Pipeline Claims vs Reality

**README Claims:**
> "Automated requirement extraction from PDFs"
> "AI-powered semantic search"
> "Knowledge graph construction"

**Code Reality:**
```python
# admin_router.py Lines 100-145
sample_requirements = [
    {"domain": "KYC", "text": "Banks must implement...", ...},
    {"domain": "AML", "text": "Suspicious transaction...", ...},
    # ... 14 hardcoded requirements
]
```

**Verdict:** ❌ **FALSE ADVERTISING**. No AI processing exists.


---

### Contradiction 2: Two Parallel Realities

**Demo Reality (Frontend):**
- 2,941 requirements available
- Knowledge graph with relationships
- Risk heatmaps
- MAP proposals
- Department impact analysis

**Operational Reality (Backend):**
- 14 requirements created per upload
- No graph persistence
- No risk calculation from graph
- No MAPs generated
- Department assignments are basic task links

**Verdict:** ❌ **DISCONNECTED SYSTEMS**. UI shows demo data, backend operates independently.

---

### Contradiction 3: Metrics from Unrelated Datasets

**Dashboard displays:**
- "2,941 Total Requirements" (from demo JSON)
- "36 Published Assignments" (from database)
- "Departments Impacted: 5" (from database published assignments)

**Pipeline displays:**
- "205 Requirements Extracted" (filtered demo JSON)
- "14 Requirements Created" (actual backend insert)

**Same page, different realities simultaneously.**

**Verdict:** ❌ **INCOHERENT DATA MODEL**. No single source of truth.

---

### Contradiction 4: Session State for Business Data

**Code:** `AnalysisSession.jsx` stores:
- Requirements text
- MAP details
- Department assignments
- Knowledge graph

**These are business entities that should be:**
- Persisted in database
- Queryable via API
- Accessible historically
- Not cleared on session end

**Verdict:** ❌ **ARCHITECTURAL ERROR**. Business data stored in ephemeral UI state.

---

### Contradiction 5: Static JSON Presented as Live Operational Data

**Requirements Search shows:** "2,941 Requirements"  
**User uploads circular and processes it**  
**Requirements Search still shows:** "2,941 Requirements" (unchanged)

**New requirements created in database are invisible in search.**

**Verdict:** ❌ **BROKEN CONTRACT**. Users believe they're searching operational data, actually browsing static demo library.

---

## Part 4: Internal Coherence Assessment

### Question: Is the current architecture internally coherent?

**Answer:** ❌ **NO**

**Evidence:**

1. **Documentation contradicts implementation**
   - README describes AI pipeline that doesn't exist
   - README shows 42 Python scripts, none found
   - README claims "offline vector database", no vector operations in backend

2. **UI promises features backend doesn't deliver**
   - Pipeline shows "MAP Generation" stage, no MAP generation code
   - Graph shows "Cross-reference Analysis", no cross-reference extraction
   - Search shows 2,941 requirements, database has <100

3. **Multiple sources of truth conflict**
   - Dashboard queries database AND demo JSON
   - Pipeline creates DB records, displays demo data
   - Different pages show different entity counts

4. **Business workflow incomplete**
   - Expected: Upload → Extract → Classify → Assign → Track
   - Actual: Upload → Insert hardcoded samples → Track

**Conclusion:** Current architecture is **fundamentally incoherent**.


---

## Part 5: Implementation Artifacts vs Intended Design

### Implementation Artifacts (Should be removed):

1. **Hardcoded Sample Requirements**
   - `admin_router.py` Lines 100-145
   - 14 hardcoded requirements for demo purposes
   - Should be: Real PDF extraction + NLP processing

2. **Demo JSON Files as Primary Data Source**
   - `requirements_taxonomy.json` used by Dashboard
   - Should be: Database queries

3. **Analysis Session Demo Data Generation**
   - `AnalysisSession.jsx` filtering demo JSON
   - Should be: API calls to fetch actual processing results

4. **Static Graph Visualization**
   - Pre-generated graph from JSON
   - Should be: Dynamic graph built from database relationships

5. **Fake Pipeline Stages**
   - 9 stages displayed, only 1 actually executes
   - Should be: Real processing stages with actual output

### Intended Design (From product vision):

1. **AI-Powered PDF Processing**
   - Text extraction (PyMuPDF)
   - Chunking with embeddings
   - Requirement extraction via NLP
   - Classification by domain/obligation

2. **Vector Database**
   - ChromaDB for semantic search
   - Offline embeddings
   - Similarity-based retrieval

3. **Knowledge Graph**
   - Cross-reference extraction
   - Relationship mapping
   - Circular dependencies
   - Persisted in database

4. **Risk Analysis**
   - Department workload calculation
   - Priority-based risk scoring
   - Deadline tracking

5. **Compliance Workflow**
   - Assignment to departments
   - Status tracking
   - Evidence upload
   - Audit trail


---

## Part 6: Critical Assumptions Re-evaluation

### Assumption 1: Is requirements_taxonomy.json production taxonomy?

**Initial Hypothesis:** Could be intentional production reference

**Critical Re-evaluation:**
- README states: "2,941 classified regulatory requirements" from AI pipeline
- Pipeline scripts that generate it: **DON'T EXIST**
- Database has schema for requirements: **EXISTS**
- New uploads don't update JSON: **NEVER SYNCS**
- Dashboard code has fallback: `try JSON, except DB`

**Verdict:** ❌ **NOT PRODUCTION TAXONOMY**

**Actual Status:** **Legacy POC artifact** from Phase 0 AI development, never migrated to database.

**Evidence:** If it were production, it would be:
1. Updated by pipeline (it's not)
2. Primary source without fallback (it has fallback)
3. Documented as permanent (README describes pipeline generation)

---

### Assumption 2: Is maps_output.json production dataset?

**Initial Hypothesis:** Could be pre-generated MAP library

**Critical Re-evaluation:**
- README: "MAP Generation" is a pipeline stage
- 2,941 items = 1:1 with requirements
- No MAP generation code exists
- Database has `assignments` table, not `maps` table
- Pipeline creates assignments, not MAPs

**Verdict:** ❌ **NOT PRODUCTION DATASET**

**Actual Status:** **Demonstration output** from Phase 0, showing what MAPs could look like.

**Evidence:**
- If MAPs were real entities, there would be a `maps` table
- If generation was real, there would be generation code
- 1:1 mapping with requirements suggests automated transformation, not genuine analysis

---

### Assumption 3: Is hybrid JSON + database deliberate?

**Initial Hypothesis:** Could be intentional dual-system architecture

**Critical Re-evaluation:**

**Evidence AGAINST Intentional Design:**
1. README never mentions dual-system architecture
2. README describes unified pipeline: "Pipeline → Persistence → Dashboard"
3. Database has schema for ALL entities (requirements, assignments)
4. No synchronization code exists
5. New data only goes to database, not JSON
6. Dashboard has try-except fallback pattern (not dual-query)

**Evidence FOR Incomplete Migration:**
1. Phase 1 docs mention "added authentication to existing system"
2. Phase 2 docs mention "integrated backend with frontend"
3. Demo JSON matches pre-backend POC structure
4. Frontend pages were built for demo data, not adapted for API

**Verdict:** ❌ **NOT DELIBERATE DESIGN**

**Actual Status:** **Incomplete migration** from Phase 0 (demo JSON) to Phase 1 (database).


---

### Assumption 4: Pipeline intentionally produces 14 assignments while showing 205?

**Initial Hypothesis:** Could be demo vs operational separation

**Critical Re-evaluation:**

**Logic Test:**
- If intentional, documentation would explain it
- If intentional, UI would clarify "Demo Data" vs "Your Data"
- If intentional, two separate views would exist

**Reality:**
- No documentation mentions this duality
- UI presents demo data as pipeline output
- User believes "205 Requirements Extracted" is their circular
- No indication demo data is being shown

**Verdict:** ❌ **NOT INTENTIONAL**

**Actual Status:** **Broken integration**. Frontend built for demo data, backend built for real operations, never reconciled.

---

### Assumption 5: Should Knowledge Graph be active-session only?

**Initial Hypothesis:** Maybe graph is analysis-specific

**Critical Re-evaluation:**

**Product Vision (README):**
> "Knowledge Graphs: Visual relationship mapping between circulars, notifications, and master directions"
> "Graph Processing: NetworkX"
> "Knowledge Graph: 14 nodes, 19 cross-reference edges"

This describes a **persistent, cumulative graph** across all documents, not session-specific.

**Expected Behavior:**
- Upload Circular A → Graph has nodes for Circular A
- Upload Circular B → Graph adds nodes for Circular B
- Circular B references Circular A → Edge created
- View graph anytime → See all circulars and relationships

**Actual Behavior:**
- Upload Circular → Creates demo-filtered graph in session
- Exit analysis → Graph cleared
- No historical graph available
- Each upload generates isolated demo graph

**Verdict:** ❌ **NOT INTENTIONAL**

**Actual Status:** **Missing feature**. Graph persistence never implemented.

---

## Part 7: Business Workflow Comparison

### Expected Workflow (from README + Product Vision):

```
1. Document Upload
   ↓
2. Text Extraction (PyMuPDF)
   ↓
3. Chunking (Semantic segmentation)
   ↓
4. Requirement Extraction (NLP/Pattern matching)
   ↓
5. Classification (Domain, Obligation Type, Priority)
   ↓
6. Vector Embedding (Sentence Transformers)
   ↓
7. Department Assignment (Rule-based or ML)
   ↓
8. MAP Generation (Mitigation action proposals)
   ↓
9. Knowledge Graph Update (Cross-reference extraction)
   ↓
10. Persistence (Database + Vector DB)
    ↓
11. Dashboard/Search/Graph (Query persisted data)
```

### Actual Workflow (validated):

```
1. Document Upload ✅
   ↓
2. Save to uploads/ directory ✅
   ↓
3. Create document record in DB ✅
   ↓
4. Generate 14 hardcoded sample requirements ❌ (Should be: Extract from PDF)
   ↓
5. Insert requirements into DB ✅
   ↓
6. Map requirements to departments via static rules ✅
   ↓
7. Create assignments in DB ✅
   ↓
8. Return success ✅
   ↓
9. Frontend displays demo data from JSON ❌ (Should be: Query actual results)
```

### Missing Stages:

❌ Text extraction from uploaded PDF  
❌ Semantic chunking  
❌ AI-powered requirement extraction  
❌ Classification  
❌ Vector embedding  
❌ MAP generation  
❌ Cross-reference extraction  
❌ Knowledge graph construction  
❌ Vector database update

**Implementation: 30% of expected workflow**


---

## Part 8: Canonical Architecture Recommendation

### Based on Product Vision: "AI-Powered RBI Compliance Intelligence Platform"

### Core Business Entities - Ultimate Destination

| Entity | Database | Session | Generated | Static Taxonomy |
|--------|----------|---------|-----------|-----------------|
| **Document** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **Requirement** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **Assignment** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **MAP** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **Department** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **Knowledge Graph** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **Cross-Reference** | ✅ PRIMARY | ❌ | ❌ | ❌ |
| **Vector Embeddings** | ✅ ChromaDB | ❌ | ✅ (on demand) | ❌ |
| **Dashboard Metrics** | ❌ | ❌ | ✅ (computed) | ❌ |
| **Analysis Session** | ❌ | ✅ (progress only) | ❌ | ❌ |

### What Should Remain:

✅ **Backend FastAPI Application**
- Authentication system
- REST API structure
- Role-based access
- Audit logging

✅ **Database Schema**
- Users, departments, documents tables
- Requirements table
- Assignments table
- Status tracking

✅ **Frontend React Application**
- Dashboard layouts
- Component structure
- Routing
- UI/UX design

✅ **Workflow Design**
- Draft → Review → Publish pattern
- Department isolation
- Status progression

### What Should Be Migrated:

**FROM: Demo JSON → TO: Database + AI Pipeline**

1. **Requirements** (2,941 items)
   - Migrate to database as seed data
   - OR: Keep as reference taxonomy (read-only)
   - Build AI pipeline to extract NEW requirements from uploads

2. **Knowledge Graph** (nodes + edges)
   - Create database tables: `graph_nodes`, `graph_edges`
   - Migrate demo graph as seed data
   - Build cross-reference extractor for NEW documents

3. **Vector Embeddings** (1,410 chunks)
   - Set up ChromaDB or pgvector
   - Migrate existing embeddings
   - Generate embeddings for NEW requirements


### What Should Be Removed:

❌ **Hardcoded Sample Requirements**
- `admin_router.py` Lines 100-145
- Replace with AI extraction pipeline

❌ **Demo Data as Primary Source**
- Dashboard fallback to JSON
- Requirements Search JSON import
- MAP Management JSON browsing

❌ **Analysis Session Demo Generation**
- `AnalysisSession.jsx` fake analysis
- Replace with API calls to real pipeline results

❌ **Fake Pipeline Stages**
- Visual theater without execution
- Replace with real processing stages

❌ **Static Graph Files**
- Pre-generated graph JSON
- Replace with database-generated graph

### What Should Become Single Source of Truth:

**For Operational Data:**
→ **PostgreSQL/SQLite Database**

All business entities:
- Documents (uploaded circulars)
- Requirements (extracted rules)
- Assignments (department tasks)
- MAPs (mitigation proposals)
- Knowledge Graph (nodes + edges)
- Cross-References (relationships)

**For Vector Search:**
→ **ChromaDB or pgvector**

All embeddings:
- Requirement embeddings
- Circular text embeddings
- Semantic search index

**For Reference Data:**
→ **Seed Data Scripts**

One-time loaded:
- Department taxonomy
- Domain classifications
- Obligation types

**For Analytics:**
→ **Computed on Demand**

Never stored:
- Dashboard metrics (COUNT queries)
- Risk scores (calculated from assignments)
- Completion percentages (derived)

---

## Part 9: Migration Strategy (No Code)

### Phase A: Establish Truth Foundation

**Goal:** Make database the authoritative source

**Actions:**

1. **Decide on Demo JSON Fate**
   - **Option 1 (Recommended):** Import as seed data, mark as "Legacy RBI Corpus"
   - **Option 2:** Discard entirely, start fresh
   - **Option 3:** Keep as read-only reference library (separate from operational data)

2. **Create Missing Database Tables**
   ```sql
   CREATE TABLE maps (
       id INTEGER PRIMARY KEY,
       map_id VARCHAR(100) UNIQUE,
       requirement_id INTEGER REFERENCES requirements(id),
       title TEXT,
       description TEXT,
       mitigation_actions TEXT,
       impact_score DECIMAL(3,1),
       priority VARCHAR(50),
       department_id INTEGER REFERENCES departments(id)
   );
   
   CREATE TABLE graph_nodes (
       id INTEGER PRIMARY KEY,
       node_id VARCHAR(100) UNIQUE,
       node_type VARCHAR(50),  -- circular, requirement, map, department
       label VARCHAR(200),
       metadata JSON
   );
   
   CREATE TABLE graph_edges (
       id INTEGER PRIMARY KEY,
       source_node_id VARCHAR(100) REFERENCES graph_nodes(node_id),
       target_node_id VARCHAR(100) REFERENCES graph_nodes(node_id),
       edge_type VARCHAR(50),  -- defines, generates, assigned, refers_to
       label VARCHAR(100)
   );
   
   CREATE TABLE cross_references (
       id INTEGER PRIMARY KEY,
       source_document_id INTEGER REFERENCES documents(id),
       target_circular_name VARCHAR(200),
       reference_type VARCHAR(50),
       context TEXT
   );
   ```

3. **Import Legacy Data as Seed**
   - Run one-time migration script
   - Import 2,941 requirements from JSON → DB
   - Import 2,941 MAPs from JSON → DB
   - Link requirements → MAPs via requirement_id
   - Mark all with `source = 'LEGACY_IMPORT'`
   - Users can browse legacy corpus


---

### Phase B: Build AI Processing Pipeline

**Goal:** Implement actual document processing

**Actions:**

1. **Text Extraction Module**
   ```python
   # backend/pipeline/text_extractor.py
   def extract_text_from_pdf(file_path):
       # Use PyMuPDF or pdfplumber
       # Return raw text
   ```

2. **Chunking Module**
   ```python
   # backend/pipeline/chunker.py
   def chunk_text(text, chunk_size=512):
       # Semantic chunking or sliding window
       # Return list of chunks
   ```

3. **Requirement Extraction Module**
   ```python
   # backend/pipeline/requirement_extractor.py
   def extract_requirements(chunks):
       # Pattern matching: "shall", "must", "required to"
       # Or: Use NLP model (spaCy, transformers)
       # Return list of requirement texts
   ```

4. **Classification Module**
   ```python
   # backend/pipeline/classifier.py
   def classify_requirement(req_text):
       # Domain: KYC, AML, Cybersecurity (rule-based or ML)
       # Priority: Critical, High, Medium, Low
       # Obligation: Mandatory, Recommended, etc.
       # Return classification dict
   ```

5. **MAP Generation Module**
   ```python
   # backend/pipeline/map_generator.py
   def generate_map(requirement):
       # Could be rule-based template
       # Or: LLM-powered (GPT, Llama)
       # Return MAP with title, description, actions
   ```

6. **Cross-Reference Extractor**
   ```python
   # backend/pipeline/cross_ref_extractor.py
   def extract_cross_references(text):
       # Pattern: "RBI/2024/123", "Circular dated..."
       # Return list of references
   ```

7. **Knowledge Graph Builder**
   ```python
   # backend/pipeline/graph_builder.py
   def build_graph_from_document(document_id, requirements, refs):
       # Create nodes: document, requirements
       # Create edges: defines, refers_to
       # Insert into graph_nodes, graph_edges
   ```

8. **Department Assigner**
   ```python
   # backend/pipeline/dept_assigner.py
   def assign_to_departments(requirement):
       # Rule-based: domain → department mapping
       # Or: ML model trained on historical data
       # Return list of department_ids
   ```

9. **Pipeline Orchestrator**
   ```python
   # backend/pipeline/orchestrator.py
   async def process_document_pipeline(document_id):
       # 1. Extract text
       # 2. Chunk
       # 3. Extract requirements
       # 4. Classify each
       # 5. Generate MAPs
       # 6. Extract cross-refs
       # 7. Build graph
       # 8. Assign departments
       # 9. Create DB records
       # 10. Return results
   ```

10. **Integrate with Existing Endpoint**
    ```python
    # backend/routers/admin_router.py
    @router.post("/process-document/{document_id}")
    async def process_document(document_id: int, ...):
        # Remove hardcoded samples
        # Call: results = await orchestrator.process_document_pipeline(document_id)
        # Return actual results
    ```


---

### Phase C: Connect Frontend to Reality

**Goal:** Remove demo data dependencies

**Actions:**

1. **Requirements Search API**
   ```python
   # backend/routers/requirement_router.py (NEW)
   @router.get("/requirements/search")
   def search_requirements(
       q: Optional[str] = None,
       domain: Optional[str] = None,
       source: Optional[str] = None,  # "LEGACY" or "EXTRACTED"
       ...
   ):
       # Query database, not JSON
       # Support full-text search
       # Return paginated results
   ```

2. **Update Requirements.jsx**
   - Remove `import { requirementsTaxonomy } from "../data/demo"`
   - Add API call: `const results = await api.get('/requirements/search', { params: filters })`
   - Display database results
   - Add filter for "Legacy Corpus" vs "Extracted Requirements"

3. **MAP Management API**
   ```python
   # backend/routers/map_router.py (NEW)
   @router.get("/maps")
   def get_maps(
       department_id: Optional[int] = None,
       priority: Optional[str] = None,
       source: Optional[str] = None,
       ...
   ):
       # Query maps table
       # Return paginated MAPs
   
   @router.get("/maps/{map_id}")
   def get_map_detail(map_id: str):
       # Fetch MAP with full details
       # Return MAP object
   ```

4. **Update Maps.jsx**
   - Remove demo JSON import
   - Add API calls
   - Display database MAPs (legacy + extracted)

5. **Knowledge Graph API**
   ```python
   # backend/routers/graph_router.py (NEW)
   @router.get("/graph/global")
   def get_global_graph():
       # Query graph_nodes, graph_edges
       # Return full graph (or paginated)
   
   @router.get("/graph/document/{document_id}")
   def get_document_graph(document_id: int):
       # Query graph for specific document
       # Return subgraph
   ```

6. **Update Graph.jsx**
   - Remove demo data generation
   - Add API call: `const graph = await api.get('/graph/global')`
   - Render from API response
   - Support document-scoped view via different endpoint

7. **Update AnalysisSession.jsx**
   - Remove `generateDocumentAnalysis()` demo function
   - Store only: processing progress, elapsed times
   - After pipeline completes, store `document_id`
   - Analysis Results page queries: `GET /documents/{id}/analysis-results`

8. **Analysis Results API**
   ```python
   # backend/routers/admin_router.py
   @router.get("/documents/{document_id}/analysis-results")
   def get_analysis_results(document_id: int):
       # Query requirements created for this document
       # Query MAPs generated for these requirements
       # Query departments assigned
       # Query graph subgraph for this document
       # Return structured results
   ```

9. **Update Pipeline.jsx Analysis Results Component**
   - Remove session dependency
   - Query API: `/documents/{documentId}/analysis-results`
   - Display actual extraction results
   - Show real counts from database


---

### Phase D: Implement Vector Search

**Goal:** Enable semantic search capability

**Actions:**

1. **Setup Vector Database**
   - Option 1: ChromaDB (offline, embedded)
   - Option 2: pgvector (PostgreSQL extension)
   - Option 3: Qdrant (server mode)

2. **Embedding Generator**
   ```python
   # backend/pipeline/embedder.py
   from sentence_transformers import SentenceTransformer
   
   model = SentenceTransformer('all-MiniLM-L6-v2')
   
   def generate_embedding(text):
       return model.encode(text)
   ```

3. **Index Requirements on Creation**
   ```python
   # backend/crud.py - create_requirement()
   def create_requirement(db, requirement_data):
       # Insert into requirements table
       req = models.Requirement(...)
       db.add(req)
       db.commit()
       
       # Generate embedding and store
       embedding = embedder.generate_embedding(req.text)
       vector_db.insert(id=req.id, embedding=embedding, metadata={"text": req.text, ...})
       
       return req
   ```

4. **Semantic Search API**
   ```python
   # backend/routers/search_router.py (NEW)
   @router.get("/search/semantic")
   def semantic_search(
       query: str,
       domain: Optional[str] = None,
       top_k: int = 10
   ):
       # Generate query embedding
       query_embedding = embedder.generate_embedding(query)
       
       # Vector similarity search
       results = vector_db.query(query_embedding, top_k=top_k)
       
       # Fetch full requirement details from DB
       requirement_ids = [r.id for r in results]
       requirements = db.query(Requirement).filter(
           Requirement.id.in_(requirement_ids)
       ).all()
       
       # Add similarity scores
       return [{"requirement": req, "score": score} for req, score in zip(requirements, results.scores)]
   ```

5. **Semantic Search UI**
   ```javascript
   // frontend/dashboard/src/pages/SemanticSearch.jsx (NEW)
   // Natural language query input
   // Results with similarity scores
   // Filters: domain, priority, source
   ```

---

### Phase E: Remove Legacy Artifacts

**Goal:** Clean up transitional code

**Actions:**

1. **Delete Demo JSON Files** (after migration)
   - `requirements_taxonomy.json` → migrated to DB
   - `maps_output.json` → migrated to DB
   - `map_details.json` → migrated to DB
   - Keep backups in `archive/` directory

2. **Remove Hardcoded Samples**
   - `admin_router.py` Lines 100-145 → delete

3. **Remove Demo Data Imports**
   - `demo.js` → delete or mark as archived
   - All `import { X } from "../data/demo"` → remove

4. **Remove Fake Pipeline Stages**
   - `Pipeline.jsx` visual stages → replace with real stage tracking from backend

5. **Clean Up Dashboard Fallback Logic**
   - `crud.py` Lines 270-278: Remove `try JSON except DB`
   - Make database the only source

6. **Update Documentation**
   - README.md: Remove references to missing Python scripts
   - Or: Actually create those scripts per migration
   - Document new architecture clearly

7. **Archive Phase 0 Artifacts**
   - Move demo JSON to `archive/phase0_poc/`
   - Add README explaining historical context
   - Preserve for reference, not operational use

---

## Part 10: Final Architecture Vision

### Production-Grade Architecture

```
┌────────────────────────────────────────────────────────┐
│                   User Interface                        │
│  (React Dashboard - Vite)                              │
│                                                         │
│  Pages:                                                │
│  • Executive Dashboard (metrics from DB)               │
│  • Pipeline Upload & Results (real processing status)  │
│  • Semantic Search (vector DB queries)                 │
│  • Requirements Browser (DB queries)                   │
│  • MAP Management (DB queries)                         │
│  • Knowledge Graph (DB-generated graph)                │
│  • Assignment Center (workflow management)             │
│  • Department Workspace (user tasks)                   │
└────────────────────┬───────────────────────────────────┘
                     │ REST API
                     ↓
┌────────────────────────────────────────────────────────┐
│              FastAPI Backend                            │
│                                                         │
│  Authentication: JWT + bcrypt                          │
│  Authorization: Role-based (HEAD_OFFICE, DEPARTMENT)   │
│                                                         │
│  Routers:                                              │
│  • /auth                  (login, token)               │
│  • /admin                 (upload, manage)             │
│  • /requirements          (search, detail)             │
│  • /maps                  (browse, detail)             │
│  • /search                (semantic, faceted)          │
│  • /graph                 (global, document-scoped)    │
│  • /departments           (workspace, tasks)           │
│  • /assignment-center     (review, publish)            │
│                                                         │
│  AI Pipeline (async tasks):                            │
│  • Text Extraction        (PyMuPDF)                    │
│  • Chunking               (semantic segmentation)      │
│  • Requirement Extraction (NLP patterns)               │
│  • Classification         (domain, priority)           │
│  • MAP Generation         (template or LLM)            │
│  • Cross-ref Extraction   (regex patterns)             │
│  • Graph Building         (NetworkX)                   │
│  • Department Assignment  (rule-based)                 │
│  • Embedding Generation   (Sentence Transformers)      │
└────────────────────┬───────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  Data Layer                              │
│                                                          │
│  ┌──────────────────┐  ┌─────────────────────────┐    │
│  │  PostgreSQL/     │  │  ChromaDB /             │    │
│  │  SQLite          │  │  pgvector               │    │
│  │                  │  │                         │    │
│  │  Tables:         │  │  Collections:           │    │
│  │  • users         │  │  • requirement_embeddings│   │
│  │  • departments   │  │  • circular_embeddings  │    │
│  │  • documents     │  │                         │    │
│  │  • requirements  │  │  Indexes:               │    │
│  │  • assignments   │  │  • Vector similarity    │    │
│  │  • maps          │  │  • Metadata filters     │    │
│  │  • graph_nodes   │  │                         │    │
│  │  • graph_edges   │  │                         │    │
│  │  • cross_refs    │  │                         │    │
│  │  • audit_logs    │  │                         │    │
│  └──────────────────┘  └─────────────────────────┘    │
│                                                          │
│  Single Source of Truth:                                │
│  • All business entities in PostgreSQL/SQLite          │
│  • All vector embeddings in ChromaDB/pgvector          │
│  • All metrics computed on demand                       │
│  • No static JSON files for operational data           │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

**Upload & Process:**
```
User uploads PDF
  ↓
POST /admin/upload → Save to uploads/, create document record
  ↓
POST /admin/process-document/{id}
  ↓
AI Pipeline (async background task):
  1. Extract text from PDF
  2. Chunk text
  3. Extract requirements (NLP)
  4. Classify each (domain, priority)
  5. Generate MAPs for each
  6. Extract cross-references
  7. Build knowledge graph
  8. Assign to departments
  9. Generate embeddings
  10. Insert all into database & vector DB
  ↓
Return processing results
  ↓
Frontend displays actual extraction results
```

**Search & Browse:**
```
User searches "KYC requirements"
  ↓
GET /search/semantic?query="KYC requirements"
  ↓
Backend:
  1. Generate query embedding
  2. Vector similarity search (ChromaDB)
  3. Fetch top-K requirement IDs
  4. Query database for full details
  5. Return ranked results with scores
  ↓
Frontend displays semantic search results
```

**Workflow:**
```
HEAD_OFFICE reviews assignments
  ↓
GET /assignment-center/summary → Unpublished assignments
  ↓
POST /assignment-center/publish → Publish department assignments
  ↓
Department user logs in
  ↓
GET /departments/workspace/my-tasks → Published assignments for their dept
  ↓
PATCH /departments/workspace/tasks/{id}/status → Update to "completed"
  ↓
GET /admin/dashboard → Show updated metrics
```


---

## Part 11: Conclusion

### Current State Assessment

**The current implementation is:** ❌ **TRANSITIONAL / INCOMPLETE**

**Not:** Intentional hybrid architecture  
**Not:** Production-ready system  
**Not:** Coherent design

**Characteristics:**
- Backend workflow foundation: **Complete**
- AI processing pipeline: **Missing**
- Demo visualization layer: **Complete but disconnected**
- Data integration: **Incomplete**

### What This System Actually Is

**Phase 0 (Historical - Inferred):**
- Python AI scripts processed PDFs
- Generated 2,941 requirements JSON
- Generated 2,941 MAPs JSON
- Built demo dashboard with static data
- **Status:** POC successful, demonstrated AI capabilities

**Phase 1 (Current - Validated):**
- Added FastAPI backend with authentication
- Added SQLite database with proper schema
- Integrated assignment workflow
- **Status:** Operational workflow complete

**Phase 1.5 (Current - Incomplete):**
- Connected frontend to some backend APIs
- Left demo data in place for visualization
- Hardcoded samples to simulate pipeline
- **Status:** Partially integrated, incoherent

**Phase 2 (Missing):**
- AI processing pipeline
- Vector database integration
- Knowledge graph persistence
- **Status:** Not started

### Migration Priority

**CRITICAL (Without these, system misrepresents capabilities):**

1. ✅ Remove hardcoded sample requirements
2. ✅ Build real PDF text extraction
3. ✅ Build requirement extraction (even basic pattern matching)
4. ✅ Connect frontend to database, not demo JSON
5. ✅ Fix Pipeline UI to show actual processing

**HIGH (Core product value):**

6. ✅ Implement MAP generation (even template-based)
7. ✅ Build semantic search with vector DB
8. ✅ Persist knowledge graph in database
9. ✅ Requirements Search queries database
10. ✅ MAP Management queries database

**MEDIUM (Enhanced features):**

11. ⚠️ Advanced NLP classification
12. ⚠️ LLM-powered MAP generation
13. ⚠️ Cross-reference extraction
14. ⚠️ Risk analysis algorithms

**LOW (Nice to have):**

15. ⚪ Import legacy JSON as seed data
16. ⚪ Advanced graph visualization
17. ⚪ Evidence upload
18. ⚪ Reporting

### Single Source of Truth - Final Answer

**For ALL business entities:**
→ **Database** (PostgreSQL or SQLite)

**For ALL vector embeddings:**
→ **Vector Database** (ChromaDB or pgvector)

**For ALL metrics:**
→ **Computed on demand** from database

**For NO operational data:**
→ ~~Static JSON files~~

**For reference/seed data only:**
→ Migration scripts (run once)

---

## Part 12: Recommendation

### Do NOT preserve existing behavior merely because it works

The current system "works" in the sense that:
- You can log in ✅
- You can upload documents ✅
- You can create assignments ✅
- You can track status ✅
- You can see a dashboard ✅

But it **fundamentally misrepresents what it does:**
- Claims "AI-powered" → Uses hardcoded samples
- Shows "205 Requirements Extracted" → Displays demo data
- Presents "Knowledge Graph" → Static visualization
- Offers "Semantic Search" → Browses JSON file
- Displays "MAP Generation" → Shows pre-generated demos

### Core Problem

**The system presents a demo of AI capabilities as if they were operational.**

This is acceptable for a prototype or POC presentation, but **NOT** for a production system where users believe their uploaded documents are being intelligently processed.

### Recommended Path Forward

**Option A: Complete the AI Integration (Recommended)**
- Build the AI pipeline (Phases B, C, D)
- Remove demo data dependencies
- Achieve the product vision
- **Timeline:** 4-8 weeks of focused development

**Option B: Reduce Scope to What Exists**
- Remove AI claims from documentation
- Simplify to "Compliance Task Management System"
- Remove demo visualizations
- Keep only working features (upload, assign, track)
- **Timeline:** 1-2 weeks of cleanup

**Option C: Hybrid Approach**
- Clearly separate "Demo Mode" from "Operational Mode"
- Add visual indicators when showing demo data
- Build minimal AI pipeline (text extraction + pattern-based requirement extraction)
- **Timeline:** 2-4 weeks

### My Strong Recommendation

**Choose Option A.** The product vision is sound. The demo data proves the concept works. The backend foundation is solid. What's needed is to connect them properly.

**Do NOT settle for Option B.** The differentiator is AI intelligence, not basic task management.

**The gap is bridgeable** with focused engineering effort on the AI pipeline.

---

## Summary

✅ **Current architecture is NOT coherent**  
✅ **Demo JSON is legacy POC artifact, not production taxonomy**  
✅ **Hybrid JSON + DB is NOT deliberate, it's incomplete migration**  
✅ **Pipeline intentionally showing different numbers: NO, it's broken integration**  
✅ **Knowledge Graph should be persistent, not session-only**  
✅ **Business workflow expected: Only 30% implemented**  

**The system needs completion, not preservation of current state.**

