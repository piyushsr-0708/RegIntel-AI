# RegIntel AI - Offline Agentic Regulatory Intelligence Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![React](https://img.shields.io/badge/react-19.2-blue.svg)
![Status](https://img.shields.io/badge/status-hackathon-orange.svg)

> An **offline-first**, deterministic AI-powered platform for RBI regulatory compliance intelligence, featuring semantic search, knowledge graphs, gap analysis, and visual analytics.

---

## 🎯 Overview

**RegIntel AI** is an enterprise-grade regulatory intelligence system designed for financial institutions to navigate India's complex RBI (Reserve Bank of India) compliance landscape. Unlike cloud-based SaaS solutions, RegIntel AI operates **100% offline**, ensuring data security and deterministic execution.

### Key Capabilities

- 🔍 **Semantic Search**: Natural language queries across 2,941 classified regulatory requirements
- 🧠 **Knowledge Graphs**: Visual relationship mapping between circulars, notifications, and master directions
- 📊 **Department Risk Heatmaps**: Compliance gap analysis by department
- ⚡ **Offline-First**: No internet required after initial setup
- 🎯 **Deadline Tracking**: Automated extraction and tracking of compliance deadlines
- 📈 **Executive Dashboards**: Real-time compliance metrics and risk indicators
- 🔗 **Cross-Reference Resolution**: Automatic parsing of circular dependencies

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     RegIntel AI Platform                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   PDF       │  │  Extraction  │  │   Requirement   │    │
│  │  Ingestion  ├─→│  & Chunking  ├─→│  Classification │    │
│  └─────────────┘  └──────────────┘  └─────────────────┘    │
│         │                                      │             │
│         │                                      ↓             │
│         │                           ┌─────────────────┐     │
│         │                           │   Taxonomy      │     │
│         │                           │   Builder       │     │
│         │                           └─────────────────┘     │
│         ↓                                      │             │
│  ┌─────────────┐                              │             │
│  │  ChromaDB   │←─────────────────────────────┘             │
│  │ Vector Store│                                             │
│  └─────────────┘                                             │
│         │                                                    │
│         ↓                                                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │  Semantic   │  │   Knowledge  │  │   Department    │    │
│  │   Search    │  │     Graph    │  │     Mapper      │    │
│  └─────────────┘  └──────────────┘  └─────────────────┘    │
│         │                  │                   │             │
│         └──────────────────┴───────────────────┘             │
│                            │                                 │
│                            ↓                                 │
│                  ┌──────────────────┐                        │
│                  │  Dashboard APIs  │                        │
│                  │   (JSON Maps)    │                        │
│                  └──────────────────┘                        │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │  React Frontend │
                    │  Vite Dashboard │
                    └─────────────────┘
```


### Technology Stack

**Backend (Python AI Pipeline)**:
- **Vector Database**: ChromaDB (persistent, offline-first)
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Graph Processing**: NetworkX
- **PDF Processing**: PyMuPDF (fitz)
- **Data Processing**: Pandas, NumPy

**Frontend (React Dashboard)**:
- **Framework**: React 19.2 + Vite 8.1
- **Visualization**: Recharts, Cytoscape.js
- **Routing**: React Router DOM
- **Styling**: Modern CSS with responsive design

**Data Assets**:
- **Source Documents**: 103 RBI PDFs (AML, KYC, Cybersecurity)
- **Requirements**: 2,941 classified regulatory requirements
- **Embeddings**: 1,410 vector embeddings
- **Knowledge Graph**: 14 nodes, 19 cross-reference edges

---

## 📁 Repository Structure

```
RegIntel-AI/
├── data/                           # CRITICAL: Preprocessing artifacts
│   ├── chroma_db/                  # ChromaDB vector database
│   ├── vector_db/                  # Alternative vector store
│   ├── chunks/                     # Preprocessed text chunks (14 files)
│   ├── extracted_text/             # Extracted PDF text (14 files)
│   ├── requirements/               # Classified requirements
│   │   ├── requirements.json       # Raw requirements
│   │   ├── requirements_clean.json # Filtered requirements
│   │   └── requirements_taxonomy.json  # Classified (2,941 reqs)
│   ├── requirement_db/             # Requirement-specific vector DB
│   └── dataset/                    # Source PDF documents (103 files)
│       └── rbi/
│           ├── aml/
│           ├── kyc/
│           └── cybersecurity/
│
├── maps/                           # CRITICAL: Dashboard JSON feeds
│   ├── dashboard_metrics.json
│   ├── department_heatmap.json
│   ├── executive_summary.json
│   ├── graph_ui.json
│   └── ...
│
├── frontend/                       # React Dashboard
│   └── dashboard/
│       ├── src/                    # React source code
│       ├── public/                 # Static assets
│       ├── package.json            # NPM dependencies
│       └── vite.config.js          # Vite configuration
│
├── archive/                        # Historical reference (versions, backups)
│
├── docs/                           # Comprehensive documentation (60+ files)
│   ├── DEMO_FLOW.md
│   ├── RUN_APPLICATION.md
│   ├── FINAL_HANDOVER_REPORT.md
│   └── ...
│
├── tests/                          # Unit tests
│   └── test_map_modules.py
│
├── *.py                            # Python pipeline scripts (42 files)
├── requirements.txt                # Python dependencies
├── PROJECT_STATE.md                # Detailed project documentation
├── TEAM_HANDOVER.md                # Team transition guide
└── README.md                       # This file
```

### Important Notes on Data Directories

⚠️ **DO NOT DELETE `data/` directory** - Contains:
- Pre-computed vector embeddings (expensive to regenerate)
- Preprocessed text chunks
- Classified requirement taxonomy
- ChromaDB vector database

These artifacts enable **offline deterministic execution** and are essential for production use.

---


## 🚀 Quick Start

### Prerequisites

- **Python**: 3.13+ (tested on 3.13)
- **Node.js**: 18+ (for frontend)
- **Storage**: ~2 GB (includes vector databases and embeddings)
- **RAM**: 4 GB minimum, 8 GB recommended

### Installation

#### 1. Clone Repository

```bash
git clone <repository-url>
cd RegIntel-AI
```

#### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Setup Frontend

```bash
cd frontend/dashboard

# Install dependencies
npm install

# Build for production
npm run build

# Or run development server
npm run dev
```

### Verify Installation

```bash
# Test Python imports
python -c "import chromadb; import sentence_transformers; print('Python dependencies OK')"

# Check data directories exist
ls data/chroma_db/
ls data/requirements/
ls maps/

# Check frontend build
ls frontend/dashboard/dist/
```

---

## 📖 Usage

### Running the Backend Pipeline

#### 1. Extract Text from PDFs (if needed)
```bash
python extract_text.py
```
**Output**: `data/extracted_text/` (14 .txt files)

#### 2. Chunk Documents
```bash
python chunk_documents.py
```
**Output**: `data/chunks/` (14 JSON files with 1,410 chunks)

#### 3. Extract Requirements
```bash
python extract_requirements_v2.py
```
**Output**: `data/requirements/requirements_clean.json` (2,941 requirements)

#### 4. Build Taxonomy
```bash
python taxonomy_builder.py
```
**Output**: `data/requirements/requirements_taxonomy.json` (classified requirements)

#### 5. Build Vector Database
```bash
python build_vector_db.py
```
**Output**: `data/chroma_db/` and `data/vector_db/` (vector embeddings)

#### 6. Parse Cross-References
```bash
python cross_reference_parser.py
```
**Output**: `cross_references.json` (19 cross-references)

#### 7. Build Knowledge Graph
```bash
python reference_graph_v2.py
```
**Output**: `reference_graph_v2.json` (graph with 14 nodes)

#### 8. Generate Dashboard Maps
```bash
python map_generator.py
python map_dashboard_feed.py
```
**Output**: `maps/*.json` (9 dashboard data files)


### Running the Frontend Dashboard

#### Development Mode
```bash
cd frontend/dashboard
npm run dev
```
Open browser to `http://localhost:5173`

#### Production Build
```bash
cd frontend/dashboard
npm run build
npm run preview
```

### Query Interface (CLI)

#### Semantic Search
```bash
python query_regintel.py
```
**Example queries**:
- "What are the KYC requirements for banks?"
- "CTR reporting deadline"
- "Cyber incident reporting requirements"

#### Requirement Search
```bash
python search_requirements.py
```
Search by domain, obligation type, or keyword

#### Gap Analysis
```bash
python gap_analysis_engine_v3.py
```
Compare your controls against RBI requirements

---

## 🎯 Features

### 1. Semantic Search Engine
- Natural language query processing
- Vector similarity search with ChromaDB
- Domain-aware filtering (KYC, AML, Cybersecurity, etc.)
- Confidence scoring (High/Medium/Low)
- **Accuracy**: 24% Top-1, 36% Top-3 (see `docs/GOLDEN_SET_FINDINGS.md`)

### 2. Knowledge Graph
- 14 source documents mapped
- 19 cross-reference relationships
- Visual graph rendering (Cytoscape.js)
- Relationship types: `refers_to`, `consolidates`, `modifies`

### 3. Department Risk Heatmaps
- 10 departments mapped (IT, Legal, Finance, etc.)
- Risk scoring based on:
  - Number of applicable requirements
  - Obligation criticality (Mandatory > Recommended)
  - Domain weighting (AML/KYC highest)

### 4. Deadline Tracking
- Automated deadline extraction from requirements
- Timeline visualization
- Department-wise deadline distribution

### 5. Executive Dashboard
- Total requirements: 2,941
- Domain breakdown (9 categories)
- Obligation type distribution
- Compliance gap metrics

### 6. Validation Suite
- Taxonomy audit (35% misclassification rate)
- Cross-reference coverage (57%)
- Resolver benchmarking (100% uptime, 0.5s avg response)
- Golden set evaluation (25 verified test queries)

---

## 📊 Current Metrics

| Metric | Value |
|--------|-------|
| **RBI PDFs Processed** | 103 documents |
| **Requirements Extracted** | 2,941 classified |
| **Vector Embeddings** | 1,410 chunks |
| **Domains Covered** | 9 (AML, KYC, Cybersecurity, etc.) |
| **Knowledge Graph Nodes** | 14 documents |
| **Cross-References** | 19 relationships |
| **Top-1 Accuracy** | 24% (golden set) |
| **Top-3 Accuracy** | 36% (golden set) |
| **Avg Query Time** | 0.5 seconds |

### Domain Distribution
- General: 903 (30.7%)
- AML: 613 (20.8%)
- KYC: 468 (15.9%)
- Reporting: 296 (10.1%)
- Record Retention: 287 (9.8%)
- Others: 374 (12.7%)

### Obligation Types
- Mandatory: 1,103 (37.5%)
- Recommended: 624 (21.2%)
- Conditional: 617 (21.0%)
- Informational: 528 (18.0%)
- Prohibited: 69 (2.3%)

---


## 🧪 Testing & Validation

### Run Unit Tests
```bash
# Test taxonomy builder
python test_taxonomy_builder.py

# Test cross-reference parser
python test_cross_reference_parser.py

# Test resolver
python test_resolver_benchmark.py

# Test map modules
python -m pytest tests/test_map_modules.py
```

### Run Validation Suite
```bash
# Run complete quality gate (all validations)
python phase7_quality_gate.py
```

**Validation Modules**:
1. **Taxonomy Audit**: Checks classification quality
2. **Cross-Reference Audit**: Validates reference extraction
3. **Resolver Benchmark**: Tests semantic search performance
4. **Golden Set Evaluation**: Measures accuracy on 25 verified queries

### View Validation Reports
```bash
# Check generated reports
cat taxonomy_audit_report.txt
cat cross_reference_audit_report.txt
cat resolver_benchmark_report.txt
cat golden_set_evaluation_report.txt
cat phase7_quality_gate_report.txt
```

---

## 📚 Documentation

### Key Documentation Files

- **`PROJECT_STATE.md`**: Comprehensive project documentation (15-30 pages)
- **`TEAM_HANDOVER.md`**: Team transition guide
- **`docs/RUN_APPLICATION.md`**: Detailed execution guide
- **`docs/DEMO_FLOW.md`**: Demo walkthrough
- **`docs/GOLDEN_SET_FINDINGS.md`**: Accuracy analysis
- **`docs/FINAL_HANDOVER_REPORT.md`**: Project completion report

### Architecture Documentation

See `docs/` directory for:
- Dependency maps
- Integration reports
- Pipeline verification
- Frontend-backend contracts
- Code quality reports

---

## 🎬 Demo Workflow

### Recommended Demo Flow

1. **Show Executive Dashboard** (Frontend)
   - Open `http://localhost:5173`
   - Navigate to Dashboard → Overview
   - Show 2,941 requirements, 9 domains

2. **Department Risk Heatmap**
   - Navigate to Dashboard → Departments
   - Show IT (highest risk: 847 requirements)
   - Explain risk scoring methodology

3. **Semantic Search** (CLI)
   ```bash
   python query_regintel.py
   # Query: "KYC requirements for banks"
   ```
   - Show Top-5 results
   - Explain confidence scoring

4. **Knowledge Graph** (Frontend)
   - Navigate to Dashboard → Graph
   - Show circular dependencies
   - Explain cross-reference relationships

5. **Gap Analysis** (CLI)
   ```bash
   python gap_analysis_engine_v3.py
   ```
   - Show compliance gaps
   - Explain priority scoring

### Demo Script

See `docs/DEMO_FLOW.md` for complete 10-minute demo script with talking points.

---

## 🔧 Known Limitations

### Accuracy Limitations
- **Top-1 Accuracy**: 24% (target: 70% for production)
- **Top-3 Accuracy**: 36% (target: 85% for production)
- **AML Domain**: 0% accuracy (critical issue)
- **Misclassification Rate**: 35% (acceptable for PoC, needs improvement)

### Technical Limitations
- **No Temporal Reasoning**: Cannot determine if Circular A supersedes Circular B
- **No Hierarchy Awareness**: Treats Master Circulars same as Notifications
- **Static Corpus**: No real-time RBI website scraping
- **Single Language**: English only
- **No Applicability Filtering**: Cannot filter by bank type, NBFC category

### See Also
- `docs/GOLDEN_SET_FINDINGS.md` - Detailed accuracy analysis
- `docs/KNOWN_ISSUES.md` - Complete issue list with severity

---

## 🚀 Future Roadmap

### Phase 8: Accuracy Improvements (Planned)
- Re-weight scoring algorithm (reduce semantic similarity weight)
- Add document hierarchy (Master Circular > Circular > Notification)
- Implement query expansion (STR → "Suspicious Transaction Report")
- Use LLM for Top-10 re-ranking (GPT-4 or local Llama)
- **Target**: 50-60% Top-1 accuracy

### Phase 9: Production Hardening (Planned)
- Expand golden set (25 → 100 queries)
- Add user feedback loop
- Implement supersession detection
- Build change detection pipeline
- Add audit trail

### Phase 10: Advanced Features (Planned)
- Multi-language support (Hindi, regional languages)
- Real-time RBI website monitoring
- Automated PDF download pipeline
- RESTful API for integrations
- Mobile app (React Native)

---


## 🤝 Contributing

This is a hackathon project currently not accepting external contributions. However, feedback and suggestions are welcome via issues.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

**RegIntel AI Team**
- AI Pipeline Development
- Knowledge Graph Engineering
- Frontend Dashboard Development
- Validation Framework Design

---

## 🙏 Acknowledgments

- **RBI**: Source regulatory documents
- **ChromaDB**: Vector database technology
- **Sentence Transformers**: Embedding models
- **React Community**: Frontend framework
- **Hackathon Organizers**: Platform and support

---

## 📞 Support

For questions or issues:
1. Check `docs/` directory for detailed documentation
2. Review `PROJECT_STATE.md` for comprehensive project context
3. See `TEAM_HANDOVER.md` for operational details
4. Open an issue in the repository

---

## ⚠️ Important Notes

### For Developers

1. **Do Not Delete `data/` Directory**: Contains preprocessing artifacts critical for offline operation
2. **Embeddings Are Expensive**: ChromaDB vector database takes 10-15 minutes to rebuild
3. **Run Order Matters**: See `docs/RUN_ORDER.md` for correct pipeline execution sequence
4. **Windows Paths**: Code uses Windows paths (`D:\SuRaksha\...`). Update for Linux/Mac if needed.

### For Deployment

1. **Storage Requirements**: ~2 GB total (data: 460 MB, node_modules: 1 GB, venv: 300 MB)
2. **First Run**: Initial setup takes 15-20 minutes (download embeddings + build vector DB)
3. **Offline Operation**: After setup, no internet required
4. **Python Version**: Tested on Python 3.13, may work on 3.10+

### For Demo/Presentation

1. **Start Frontend First**: `npm run dev` in `frontend/dashboard/`
2. **Pre-generate Maps**: Run `map_generator.py` and `map_dashboard_feed.py` before demo
3. **Prepare Queries**: Have 3-5 sample queries ready for semantic search demo
4. **Know Limitations**: Be transparent about 24% accuracy (research-grade, not production)

---

## 📈 Project Status

**Current Status**: Hackathon Complete ✅
- ✅ Full pipeline operational
- ✅ Frontend dashboard deployed
- ✅ Validation suite complete
- ✅ Documentation comprehensive
- ⚠️ Accuracy needs improvement (24% → 70% target)

**Suitable For**:
- Academic research
- Proof-of-concept demonstrations
- Regulatory intelligence prototypes
- Learning AI/ML pipeline architecture

**Not Suitable For** (Yet):
- Production compliance systems
- Mission-critical decision making
- Real-time regulatory monitoring

---

## 📊 Repository Statistics

```
Languages:
- Python:     70% (42 scripts, 10K+ LOC)
- JavaScript: 20% (React frontend)
- JSON:       8%  (Data files)
- Markdown:   2%  (Documentation)

Repository Size:
- Core Code:        ~10 MB
- Data Assets:      ~460 MB
- Dependencies:     ~1.3 GB (node_modules + venv)
- Documentation:    ~5 MB

Files:
- Python scripts:   42
- Test files:       10
- JSON data:        150+
- Markdown docs:    60+
- Source PDFs:      103
```

---

**Built with ❤️ for regulatory compliance automation**

*Last Updated: June 26, 2026*
