# Product Specification - Part 2
## AI Pipeline, Architecture, and Roadmap

---

## 5. AI Processing Pipeline

### Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   AI Processing Pipeline                      │
│               (Async Background Tasks)                        │
└──────────────────────────────────────────────────────────────┘

Input: Document ID (PDF already uploaded)
Output: Requirements, MAPs, Assignments, Graph Updates
```

### 5.1 Text Extraction Module

**Purpose:** Extract structured text from PDF

**Input:**
- Document ID (integer)
- File path (string, location of PDF)

**Processing:**
```python
import fitz  # PyMuPDF

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        # Preserve structure: headings, lists, tables
        text_blocks.append({
            "page": page_num + 1,
            "text": text,
            "fonts": page.get_fonts(),  # For identifying headings
        })
    
    return text_blocks
```

**Output:**
```json
{
  "document_id": 123,
  "total_pages": 45,
  "text_blocks": [
    {"page": 1, "text": "...", "fonts": [...]},
    {"page": 2, "text": "...", "fonts": [...]}
  ],
  "metadata": {
    "circular_number": "RBI/2024/123",
    "issue_date": "2024-06-15",
    "subject": "Guidelines on KYC..."
  }
}
```

**Technology:** PyMuPDF (fitz)

---

### 5.2 Semantic Chunking Module

**Purpose:** Split text into meaningful segments for processing

**Input:**
- Extracted text (list of page blocks)

**Processing:**
```python
def semantic_chunk(text_blocks, chunk_size=512, overlap=50):
    chunks = []
    current_chunk = ""
    current_page = 1
    
    for block in text_blocks:
        sentences = nltk.sent_tokenize(block["text"])
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size:
                chunks.append({
                    "text": current_chunk,
                    "page": current_page,
                    "char_start": ...,
                    "char_end": ...
                })
                # Overlap: keep last N characters
                current_chunk = current_chunk[-overlap:] + sentence
            else:
                current_chunk += " " + sentence
    
    return chunks
```

**Output:**
```json
{
  "chunks": [
    {
      "chunk_id": 0,
      "text": "Banks must implement...",
      "page": 3,
      "char_start": 1250,
      "char_end": 1762
    }
  ]
}
```

**Technology:** NLTK or spaCy for sentence tokenization

---

### 5.3 Requirement Extraction Module

**Purpose:** Identify regulatory obligations within text

**Input:**
- Text chunks

**Processing:**
```python
import re
from transformers import pipeline

# Pattern-based extraction
OBLIGATION_PATTERNS = [
    r'\b(shall|must|required to|need to|obliged to)\b',
    r'\b(should|recommended to|advised to)\b',
    r'\b(prohibited|not permitted|shall not|must not)\b'
]

def extract_requirements(chunks):
    requirements = []
    
    for chunk in chunks:
        # Method 1: Pattern matching
        for pattern in OBLIGATION_PATTERNS:
            matches = re.finditer(pattern, chunk["text"], re.IGNORECASE)
            for match in matches:
                # Extract sentence containing obligation
                requirement_text = extract_sentence_context(chunk["text"], match.start())
                
                # Validate it's a genuine requirement (not description)
                if is_genuine_requirement(requirement_text):
                    requirements.append({
                        "text": requirement_text,
                        "page": chunk["page"],
                        "obligation_indicator": match.group(0),
                        "confidence": calculate_confidence(requirement_text)
                    })
        
        # Method 2: NLP-based (future: fine-tuned transformer)
        # ner_results = ner_model(chunk["text"])
        # requirements.extend(extract_from_ner(ner_results))
    
    # Deduplication
    requirements = deduplicate_requirements(requirements)
    
    return requirements
```

**Output:**
```json
{
  "requirements": [
    {
      "text": "Banks must implement enhanced due diligence for high-risk customers",
      "page": 5,
      "section": "3.2.1",
      "obligation_indicator": "must",
      "confidence": 0.92
    }
  ]
}
```

**Technology:**
- Regex patterns (MVP)
- spaCy NER (enhanced)
- Fine-tuned BERT (future)

---

### 5.4 Classification Module

**Purpose:** Categorize requirements by domain, obligation type, priority

**Input:**
- Extracted requirements

**Processing:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
# Or use zero-shot classification with transformers

DOMAIN_KEYWORDS = {
    "KYC": ["customer", "identification", "kyc", "cdd", "due diligence"],
    "AML": ["money laundering", "aml", "suspicious transaction", "str", "ctr"],
    "Cybersecurity": ["cyber", "security", "breach", "incident", "firewall"],
    # ... etc
}

def classify_requirement(requirement_text):
    # Domain classification (rule-based + ML)
    domain = classify_domain(requirement_text, DOMAIN_KEYWORDS)
    
    # Obligation type (pattern-based)
    obligation_type = classify_obligation(requirement_text)
    
    # Priority (heuristic + keywords)
    priority = classify_priority(requirement_text, domain)
    
    # Deadline extraction
    deadline = extract_deadline(requirement_text)
    
    return {
        "domain": domain,
        "obligation_type": obligation_type,
        "priority": priority,
        "deadline_text": deadline["text"],
        "deadline_date": deadline["date"]
    }
```

**Classification Logic:**

**Domain:** 
- Rule-based keyword matching (MVP)
- TF-IDF + Naive Bayes (enhanced)
- BERT zero-shot classification (future)

**Obligation Type:**
- "must", "shall" → Mandatory
- "should", "recommended" → Recommended
- "must not", "prohibited" → Prohibited
- "if", "in case" → Conditional
- No obligation indicator → Informational

**Priority:**
- "Critical" if: domain=AML/KYC/Cybersecurity AND obligation=Mandatory AND deadline < 30 days
- "High" if: obligation=Mandatory AND deadline < 90 days
- "Medium" if: obligation=Recommended
- "Low" if: obligation=Informational

**Output:**
```json
{
  "requirement_id": "REQ_RBI2024123_0042",
  "text": "...",
  "domain": "KYC",
  "obligation_type": "Mandatory",
  "priority": "Critical",
  "deadline_text": "within 3 months",
  "deadline_date": "2024-09-15"
}
```

---

### 5.5 Vector Embedding Generation

**Purpose:** Generate semantic embeddings for similarity search

**Input:**
- Classified requirements

**Processing:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(requirements):
    embeddings = []
    
    for req in requirements:
        # Generate 384-dim embedding
        embedding = model.encode(req["text"])
        
        embeddings.append({
            "requirement_id": req["requirement_id"],
            "embedding": embedding.tolist(),
            "metadata": {
                "text": req["text"],
                "domain": req["domain"],
                "priority": req["priority"]
            }
        })
    
    return embeddings
```

**Output:**
```json
{
  "embeddings": [
    {
      "requirement_id": "REQ_RBI2024123_0042",
      "embedding": [0.123, -0.456, 0.789, ...],  // 384 dimensions
      "metadata": {...}
    }
  ]
}
```

**Storage:** ChromaDB

```python
import chromadb

client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_or_create_collection("requirement_embeddings")

# Insert embeddings
collection.add(
    ids=[emb["requirement_id"] for emb in embeddings],
    embeddings=[emb["embedding"] for emb in embeddings],
    metadatas=[emb["metadata"] for emb in embeddings]
)
```

**Technology:** Sentence Transformers (all-MiniLM-L6-v2)

---

### 5.6 Cross-Reference Detection Module

**Purpose:** Identify references to other RBI circulars

**Input:**
- Original document text

**Processing:**
```python
import re

REFERENCE_PATTERNS = [
    r'RBI/\d{4}/\d+',  # RBI/2024/123
    r'Circular\s+dated\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
    r'Master\s+Circular\s+No\.\s*\w+',
    r'Notification\s+No\.\s*\w+'
]

def extract_cross_references(text):
    references = []
    
    for pattern in REFERENCE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            ref_text = match.group(0)
            context = extract_context(text, match.start(), window=100)
            
            # Determine reference type
            ref_type = determine_reference_type(context)
            
            references.append({
                "target_circular": ref_text,
                "reference_type": ref_type,
                "context": context,
                "page": get_page_number(text, match.start())
            })
    
    return references
```

**Reference Types:**
- "supersedes" if context contains "supersedes", "replaces"
- "amends" if context contains "amended", "modified"
- "consolidates" if context contains "consolidated", "combined"
- "refers_to" otherwise

**Output:**
```json
{
  "cross_references": [
    {
      "target_circular": "RBI/2023/99",
      "reference_type": "supersedes",
      "context": "This circular supersedes RBI/2023/99 dated...",
      "page": 1
    }
  ]
}
```

---

### 5.7 Department Assignment Module

**Purpose:** Auto-assign requirements to relevant departments

**Input:**
- Classified requirements

**Processing:**
```python
DOMAIN_DEPARTMENT_MAP = {
    "KYC": ["Compliance", "AML Compliance Cell"],
    "AML": ["AML Compliance Cell", "Compliance"],
    "Cybersecurity": ["Cyber Security", "IT"],
    "Risk_Management": ["Risk Management"],
    "Treasury": ["Treasury Operations"],
    "Operations": ["Operations"],
    "Legal": ["Legal"],
    "Reporting": ["Compliance", "Finance"],
    "Data_Privacy": ["IT", "Legal", "Compliance"],
    "General": ["Compliance"]
}

def assign_departments(requirement):
    domain = requirement["domain"]
    assigned_departments = DOMAIN_DEPARTMENT_MAP.get(domain, ["Compliance"])
    
    # Can apply ML model for more sophisticated assignment in future
    
    return assigned_departments
```

**Output:**
```json
{
  "requirement_id": "REQ_RBI2024123_0042",
  "assigned_departments": ["Compliance", "AML Compliance Cell"]
}
```

---

### 5.8 MAP Generation Module

**Purpose:** Generate actionable mitigation plans for requirements

**Input:**
- Classified requirement

**Processing:**

**Option 1: Template-Based (MVP)**
```python
def generate_map_template(requirement):
    domain = requirement["domain"]
    obligation_type = requirement["obligation_type"]
    
    # Template library
    if domain == "KYC" and "due diligence" in requirement["text"].lower():
        return {
            "title": "Update KYC Due Diligence Procedures",
            "description": f"Implement enhanced due diligence as per: {requirement['text']}",
            "mitigation_actions": [
                {"action": "Review current KYC policy", "owner": "Compliance Team", "timeline": "1 week"},
                {"action": "Update policy document", "owner": "Policy Team", "timeline": "2 weeks"},
                {"action": "Train staff on new procedures", "owner": "Training Dept", "timeline": "1 month"},
                {"action": "Implement system changes", "owner": "IT", "timeline": "6 weeks"}
            ],
            "estimated_effort": "40 person-hours",
            "complexity": "Medium"
        }
```

**Option 2: LLM-Powered (Future)**
```python
from openai import OpenAI

def generate_map_llm(requirement):
    client = OpenAI(api_key="...")
    
    prompt = f"""
    Given this regulatory requirement:
    "{requirement['text']}"
    
    Generate a detailed mitigation action plan including:
    1. Concise title
    2. Description
    3. Step-by-step actions with owners and timelines
    4. Estimated effort
    5. Complexity assessment
    
    Format as JSON.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)
```

**Output:**
```json
{
  "map_id": "MAP_REQ_RBI2024123_0042",
  "requirement_id": "REQ_RBI2024123_0042",
  "title": "Implement Enhanced Customer Due Diligence",
  "description": "Update KYC procedures to include enhanced due diligence for high-risk customers...",
  "mitigation_actions": [
    {"action": "Review current KYC policy", "owner": "Compliance", "timeline": "1 week"},
    {"action": "Draft policy amendments", "owner": "Compliance", "timeline": "2 weeks"},
    {"action": "IT system updates", "owner": "IT", "timeline": "6 weeks"},
    {"action": "Staff training", "owner": "Training", "timeline": "4 weeks"}
  ],
  "estimated_effort": "40 person-hours",
  "resources_required": "Compliance team, IT resources, training materials",
  "complexity": "Medium",
  "impact_score": 7.5
}
```

**Technology:**
- Template-based (MVP)
- GPT-4 or local Llama (production)

---

### 5.9 Knowledge Graph Construction Module

**Purpose:** Build/update persistent knowledge graph

**Input:**
- Document metadata
- Requirements
- MAPs
- Cross-references
- Department assignments

**Processing:**
```python
def build_graph(document, requirements, maps, cross_refs, assignments):
    graph_updates = {
        "nodes": [],
        "edges": []
    }
    
    # 1. Create document node
    graph_updates["nodes"].append({
        "node_id": document["document_id"],
        "node_type": "Document",
        "label": document["circular_number"],
        "metadata": {...}
    })
    
    # 2. Create requirement nodes + defines edges
    for req in requirements:
        graph_updates["nodes"].append({
            "node_id": req["requirement_id"],
            "node_type": "Requirement",
            "label": req["requirement_id"],
            "metadata": {...}
        })
        
        graph_updates["edges"].append({
            "source_node_id": document["document_id"],
            "target_node_id": req["requirement_id"],
            "edge_type": "defines",
            "label": "defines requirement"
        })
    
    # 3. Create MAP nodes + generates edges
    for map_obj in maps:
        graph_updates["nodes"].append({
            "node_id": map_obj["map_id"],
            "node_type": "MAP",
            "label": map_obj["title"],
            "metadata": {...}
        })
        
        graph_updates["edges"].append({
            "source_node_id": map_obj["requirement_id"],
            "target_node_id": map_obj["map_id"],
            "edge_type": "generates",
            "label": "generates MAP"
        })
    
    # 4. Create cross-reference edges
    for ref in cross_refs:
        # Check if target document exists in system
        target_doc = find_document_by_circular(ref["target_circular"])
        if target_doc:
            graph_updates["edges"].append({
                "source_node_id": document["document_id"],
                "target_node_id": target_doc["document_id"],
                "edge_type": ref["reference_type"],
                "label": ref["reference_type"]
            })
    
    # 5. Create assigned_to edges (MAP → Department)
    for assignment in assignments:
        dept_node_id = f"dept_{assignment['department_code']}"
        graph_updates["edges"].append({
            "source_node_id": assignment["map_id"],
            "target_node_id": dept_node_id,
            "edge_type": "assigned_to",
            "label": "assigned to"
        })
    
    return graph_updates
```

**Output:**
```json
{
  "nodes_created": 45,
  "edges_created": 78,
  "nodes": [...],
  "edges": [...]
}
```

**Storage:** PostgreSQL `graph_nodes` and `graph_edges` tables

---

### 5.10 Persistence Module

**Purpose:** Save all extracted data to database

**Input:**
- All pipeline outputs

**Processing:**
```python
async def persist_pipeline_results(document_id, pipeline_results):
    async with get_db_session() as db:
        # 1. Insert requirements
        for req_data in pipeline_results["requirements"]:
            requirement = Requirement(**req_data, document_id=document_id)
            db.add(requirement)
        await db.flush()  # Get IDs
        
        # 2. Insert MAPs
        for map_data in pipeline_results["maps"]:
            map_obj = MitigationActionPlan(**map_data)
            db.add(map_obj)
        await db.flush()
        
        # 3. Insert assignments (draft status)
        for assignment_data in pipeline_results["assignments"]:
            assignment = Assignment(**assignment_data, is_published=False)
            db.add(assignment)
        
        # 4. Insert cross-references
        for ref_data in pipeline_results["cross_references"]:
            cross_ref = CrossReference(**ref_data, source_document_id=document_id)
            db.add(cross_ref)
        
        # 5. Insert graph nodes and edges
        for node_data in pipeline_results["graph"]["nodes"]:
            node = GraphNode(**node_data)
            db.add(node)
        for edge_data in pipeline_results["graph"]["edges"]:
            edge = GraphEdge(**edge_data)
            db.add(edge)
        
        # 6. Insert embeddings into ChromaDB
        for embedding in pipeline_results["embeddings"]:
            collection.add(**embedding)
        
        # 7. Mark document as processed
        document = await db.get(Document, document_id)
        document.processed = True
        document.processed_at = datetime.utcnow()
        document.processing_status = "Completed"
        
        await db.commit()
```

---

### 5.11 Pipeline Orchestrator

**Purpose:** Coordinate all pipeline stages

**Implementation:**
```python
from celery import Celery

app = Celery('pipeline', broker='redis://localhost:6379')

@app.task
async def process_document_pipeline(document_id: int):
    try:
        # Update status: Processing
        update_document_status(document_id, "Processing")
        
        # Stage 1: Text Extraction
        text_blocks = extract_text(document_id)
        
        # Stage 2: Chunking
        chunks = semantic_chunk(text_blocks)
        
        # Stage 3: Requirement Extraction
        requirements = extract_requirements(chunks)
        
        # Stage 4: Classification
        classified_reqs = [classify_requirement(req) for req in requirements]
        
        # Stage 5: Embedding Generation
        embeddings = generate_embeddings(classified_reqs)
        
        # Stage 6: Cross-Reference Detection
        cross_refs = extract_cross_references(text_blocks)
        
        # Stage 7: Department Assignment
        assignments = []
        for req in classified_reqs:
            depts = assign_departments(req)
            for dept in depts:
                assignments.append({"requirement_id": req["id"], "department": dept})
        
        # Stage 8: MAP Generation
        maps = [generate_map(req) for req in classified_reqs]
        
        # Stage 9: Graph Construction
        graph_updates = build_graph(document_id, classified_reqs, maps, cross_refs, assignments)
        
        # Stage 10: Persistence
        await persist_pipeline_results(document_id, {
            "requirements": classified_reqs,
            "maps": maps,
            "assignments": assignments,
            "cross_references": cross_refs,
            "graph": graph_updates,
            "embeddings": embeddings
        })
        
        # Update status: Completed
        update_document_status(document_id, "Completed")
        
        return {
            "status": "success",
            "requirements_extracted": len(classified_reqs),
            "maps_generated": len(maps),
            "assignments_created": len(assignments),
            "departments_impacted": len(set(a["department"] for a in assignments))
        }
        
    except Exception as e:
        update_document_status(document_id, "Failed", error=str(e))
        raise
```

**Technology:** Celery + Redis for async task queue

---

## 6. Frontend Responsibilities

### 6.1 Login Page

**Purpose:** Authenticate users

**Displayed Entity:** None (authentication form)

**Source API:** `POST /api/auth/login`

**User Actions:**
- Enter username/password
- Submit credentials
- Receive JWT token
- Redirect to dashboard

**Components:**
- Login form
- Error messages
- Session management

---

### 6.2 Executive Dashboard

**Purpose:** Organization-wide compliance overview

**Displayed Entities:**
- Dashboard metrics (total requirements, assignments, completion %)
- Priority distribution
- Department risk scores
- Upcoming deadlines
- Trend charts

**Source APIs:**
- `GET /api/admin/dashboard` - Main metrics
- `GET /api/admin/trends?period=30days` - Time series data
- `GET /api/assignment-center/department-risk` - Risk scores

**User Actions:**
- View metrics
- Filter by time period
- Drill down into departments
- Export reports

**Components:**
- KPI cards
- Charts (Recharts)
- Department heatmap
- Deadline calendar

**Authorization:** HEAD_OFFICE only

---

### 6.3 Document Upload & Pipeline

**Purpose:** Upload circulars, trigger processing, view results

**Displayed Entities:**
- Document upload form
- Pipeline progress (realtime)
- Processing results summary

**Source APIs:**
- `POST /api/admin/upload` - Upload file
- `POST /api/admin/process-document/{id}` - Trigger pipeline
- `GET /api/admin/documents/{id}/status` - Poll processing status
- `GET /api/admin/documents/{id}/results` - Get results

**User Actions:**
- Select PDF file
- Upload document
- Monitor processing (WebSocket or polling)
- View extraction statistics
- Navigate to Assignment Center

**Components:**
- File upload with drag-drop
- Progress bar (real-time)
- Stage indicators
- Results summary

**Authorization:** HEAD_OFFICE only

---

### 6.4 Assignment Center

**Purpose:** Review and publish auto-generated assignments

**Displayed Entities:**
- Unpublished assignments
- Grouped by department
- Requirement details
- MAP recommendations

**Source APIs:**
- `GET /api/assignment-center/summary` - Unpublished assignments
- `GET /api/admin/assignments/{id}` - Assignment details
- `POST /api/assignment-center/publish` - Publish assignments
- `PATCH /api/admin/assignments/{id}` - Modify assignment

**User Actions:**
- Review assignments per department
- Modify priority, due date, department
- Add remarks
- Publish selected assignments
- Bulk publish all

**Components:**
- Department cards with task counts
- Assignment detail modal
- Edit forms
- Publish confirmation

**Authorization:** HEAD_OFFICE only

---

### 6.5 Requirements Search

**Purpose:** Search and browse all requirements

**Displayed Entities:**
- Requirements (from database)
- Search results
- Requirement details

**Source APIs:**
- `GET /api/requirements/search?q={query}&domain={domain}&...` - Search
- `GET /api/requirements/{id}` - Requirement details

**User Actions:**
- Enter search query (text or semantic)
- Apply filters (domain, priority, source)
- View results with highlighting
- Click to see full requirement
- Navigate to related MAP/assignments

**Components:**
- Search bar
- Filter panel
- Results list with pagination
- Requirement detail modal

**Authorization:** All authenticated users

---

### 6.6 Semantic Search

**Purpose:** Natural language semantic search across requirements

**Displayed Entities:**
- Search results ranked by similarity
- Similarity scores

**Source APIs:**
- `GET /api/search/semantic?query={text}&top_k=20` - Vector search

**User Actions:**
- Enter natural language query
- View results with similarity scores
- Apply metadata filters
- Click to see requirement details

**Components:**
- Natural language query input
- Results with similarity scores
- Highlighted matching terms

**Authorization:** All authenticated users

---

### 6.7 MAP Management

**Purpose:** Browse and view mitigation action plans

**Displayed Entities:**
- MAPs (from database)
- MAP details with actions

**Source APIs:**
- `GET /api/maps?department={id}&priority={...}` - List MAPs
- `GET /api/maps/{id}` - MAP details

**User Actions:**
- Browse MAPs
- Filter by department, priority, status
- View full MAP with action steps
- See linked requirement and assignments

**Components:**
- MAP list with filters
- MAP detail view
- Action checklist display

**Authorization:** All authenticated users

---

### 6.8 Knowledge Graph

**Purpose:** Visualize regulatory relationships

**Displayed Entities:**
- Graph nodes (documents, requirements, MAPs, departments)
- Graph edges (relationships)

**Source APIs:**
- `GET /api/graph/global` - Full graph
- `GET /api/graph/document/{id}` - Document-scoped graph
- `GET /api/graph/node/{id}` - Node details

**User Actions:**
- View interactive graph (Cytoscape.js)
- Zoom, pan, search
- Filter by node type, domain
- Click node to see details
- Trace relationships

**Components:**
- Cytoscape graph visualization
- Filter panel
- Node detail sidebar
- Legend

**Authorization:** All authenticated users

---

### 6.9 Department Workspace

**Purpose:** Department users view and work on their assignments

**Displayed Entities:**
- Published assignments for user's department
- Assignment details
- Status progression

**Source APIs:**
- `GET /api/departments/workspace/my-tasks` - User's department tasks
- `GET /api/departments/workspace/tasks/{id}` - Task details
- `PATCH /api/departments/workspace/tasks/{id}/status` - Update status

**User Actions:**
- View assigned tasks
- Filter by status (pending, in progress, completed)
- Click to see full requirement and MAP
- Update status
- Add progress notes

**Components:**
- Task list with status
- Task detail modal
- Status update form
- Progress notes

**Authorization:** DEPARTMENT role only (filtered by user's department)

---

### 6.10 Department Dashboard (Admin View)

**Purpose:** HEAD_OFFICE monitors department-level compliance

**Displayed Entities:**
- Per-department metrics
- Completion rates
- Risk scores
- Assignment distribution

**Source APIs:**
- `GET /api/assignment-center/admin-summary` - Per-department stats
- `GET /api/assignment-center/department-risk` - Risk analysis

**User Actions:**
- View department breakdown
- Sort by risk, completion
- Drill into department details
- Export department reports

**Components:**
- Department table
- Risk heatmap
- Completion charts
- Drill-down modals

**Authorization:** HEAD_OFFICE only

---

## Summary: Frontend Pages

| Page | Purpose | Primary API | User Role | Data Source |
|------|---------|-------------|-----------|-------------|
| Login | Auth | `/auth/login` | All | Auth service |
| Executive Dashboard | Overview | `/admin/dashboard` | HEAD_OFFICE | Database (computed) |
| Pipeline | Upload & process | `/admin/upload`, `/admin/process-document` | HEAD_OFFICE | Database + AI pipeline |
| Assignment Center | Review & publish | `/assignment-center/summary` | HEAD_OFFICE | Database |
| Requirements Search | Browse requirements | `/requirements/search` | All | Database |
| Semantic Search | NL search | `/search/semantic` | All | Vector DB + Database |
| MAP Management | Browse MAPs | `/maps` | All | Database |
| Knowledge Graph | Relationships | `/graph/global` | All | Database (graph tables) |
| Department Workspace | User tasks | `/departments/workspace/my-tasks` | DEPARTMENT | Database (filtered) |
| Department Dashboard | Dept monitoring | `/assignment-center/admin-summary` | HEAD_OFFICE | Database (computed) |

**Key Principles:**
- Every page queries database via API
- No static JSON files
- No demo data
- No session-dependent business data
- All pages show consistent, real-time data

---

