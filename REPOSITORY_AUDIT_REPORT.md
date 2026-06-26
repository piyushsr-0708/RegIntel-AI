# RegIntel AI - Repository Audit Report

**Date**: June 26, 2026  
**Project**: RegIntel AI - Offline Agentic Regulatory Intelligence & Compliance Platform  
**Auditor**: AI Repository Cleanup Agent  
**Status**: Pre-Cleanup Audit Complete

---

## EXECUTIVE SUMMARY

**Repository Size**: ~1.8 GB total
- **Core Application**: ~0.46 GB (excluding node_modules/venv)
- **node_modules**: ~1.0 GB (rebuildable)
- **venv**: ~0.3 GB (rebuildable)

**File Counts**:
- Python scripts: 42 (root) + archived versions
- Test files: 10
- JSON data files: ~150+
- PDF source documents: 103
- Generated reports: 50+
- Documentation files: 60+

**Key Finding**: Repository is well-organized with clear data/code separation. Most size comes from legitimate preprocessing artifacts (vector databases, embeddings, chunked data) that are CRITICAL for offline operation.

---

## PHASE 1: COMPLETE REPOSITORY AUDIT

### Critical Production Directories (DO NOT MODIFY)

| Directory | Purpose | Size Est | Runtime Critical | Reason |
|-----------|---------|----------|------------------|---------|
| `data/chroma_db/` | ChromaDB vector database | ~50 MB | **YES** | Core vector search database |
| `data/vector_db/` | Alternative vector DB | ~100 MB | **YES** | Backup/alternative embeddings |
| `data/chunks/` | Preprocessed text chunks | ~10 MB | **YES** | Chunked documents for embeddings |
| `data/extracted_text/` | Extracted PDF text | ~5 MB | **YES** | Preprocessing output, may be regenerated but slow |
| `data/requirements/` | Classified requirements | ~15 MB | **YES** | Core requirement taxonomy |
| `data/requirement_db/` | Requirement vector DB | ~50 MB | **YES** | Requirement-specific vector store |
| `data/dataset/rbi/` | Source PDFs (103 files) | ~150 MB | **YES** | Original regulatory documents |
| `maps/` | Dashboard JSON feeds | ~2 MB | **YES** | Frontend data contract |
| `frontend/dashboard/src/` | React source code | ~1 MB | **YES** | Frontend application |

**Total Critical Data**: ~383 MB

### Production Python Scripts (Root Directory)

| File | Purpose | Referenced By | Safe to Remove |
|------|---------|---------------|----------------|
| `build_vector_db.py` | Builds ChromaDB vector store | Pipeline | **NO** - Core |
| `chunk_documents.py` | Chunks PDFs into segments | Pipeline | **NO** - Core |
| `extract_text.py` | Extracts text from PDFs | Pipeline | **NO** - Core |
| `extract_requirements_v2.py` | Extracts requirements | Pipeline | **NO** - Core |
| `taxonomy_builder.py` | Classifies requirements | Pipeline, tests | **NO** - Core |
| `cross_reference_parser.py` | Parses cross-references | Pipeline, tests | **NO** - Core |
| `reference_graph_v2.py` | Builds knowledge graph | Pipeline | **NO** - Core |
| `effective_requirement_resolver.py` | Semantic search resolver | query_regintel.py | **NO** - Core |
| `deadline_tracker.py` | Deadline extraction | map_generator.py | **NO** - Core |
| `department_mapper.py` | Department classification | map_generator.py | **NO** - Core |
| `map_generator.py` | Generates map JSONs | map_dashboard_feed.py | **NO** - Core |
| `map_dashboard_feed.py` | Feeds frontend with data | Frontend | **NO** - Core |
| `query_regintel.py` | Query interface | User-facing | **NO** - Core |
| `search_requirements.py` | Search interface | User-facing | **NO** - Core |
| `gap_analysis_engine_v3.py` | Gap analysis | Demo feature | **NO** - Core |


### Validation & Testing Scripts

| File | Purpose | Safe to Remove |
|------|---------|----------------|
| `taxonomy_audit.py` | Validates taxonomy quality | **NO** - Validation |
| `cross_reference_audit.py` | Validates cross-refs | **NO** - Validation |
| `resolver_benchmark.py` | Benchmarks resolver | **NO** - Validation |
| `golden_set_evaluator.py` | Accuracy evaluation | **NO** - Validation |
| `phase7_quality_gate.py` | Master quality gate | **NO** - Validation |
| `test_*.py` (10 files) | Unit tests | **NO** - Testing |
| `verify_json_consistency.py` | JSON validation | **NO** - Validation |
| `verify_phase7_module1.py` | Phase validation | **NO** - Validation |

### Utility & Maintenance Scripts

| File | Purpose | Safe to Remove |
|------|---------|----------------|
| `change_detector_v2.py` | Detects corpus changes | **KEEP** - Utility |
| `change_diff_summary_v2.py` | Change reports | **KEEP** - Utility |
| `score_documents.py` | Document scoring | **KEEP** - Utility |
| `requirement_vector_db.py` | Vector DB utility | **KEEP** - Utility |
| `import_analyzer.py` | Dependency analysis | **KEEP** - Utility |

### Legacy/Cleanup Scripts (Review Needed)

| File | Purpose | Safe to Remove |
|------|---------|----------------|
| `fix_paths.py` | Path refactoring (v1) | **PROBABLY** - One-time script |
| `fix_paths2.py` | Path refactoring (v2) | **PROBABLY** - One-time script |
| `phase0_backup.py` | Backup script | **PROBABLY** - One-time script |
| `phase1_cleanup.py` | Cleanup script | **PROBABLY** - One-time script |
| `phase1_path_update.py` | Path update script | **PROBABLY** - One-time script |
| `phase6_zip.py` | Zip creation script | **PROBABLY** - One-time script |
| `refactor_paths.py` | Path refactoring | **PROBABLY** - One-time script |

### Archive Directory Analysis

**Location**: `archive/`

**Contents**:
- 30+ archived Python scripts (v1, v2, v3 versions)
- Old validation reports
- Historical data snapshots
- Demo corpus backups
- High priority document backups

**Status**: **DO NOT DELETE** - Historical reference for project evolution

**Breakdown**:
| Category | Count | Status |
|----------|-------|--------|
| Archived scripts (v1, v2) | 15+ | Historical reference |
| Old reports (.txt, .md) | 20+ | Historical reference |
| JSON snapshots | 10+ | Historical data |
| Demo corpus backups | 3 directories | Backup data |

**Reason to Keep**: Archive contains version history showing project evolution, useful for understanding design decisions and debugging.

### Build Artifacts (Potential Cleanup)

| Directory/File | Purpose | Rebuildable | Safe to Remove |
|----------------|---------|-------------|----------------|
| `__pycache__/` (root) | Python bytecode cache | YES | **YES** |
| `tests/__pycache__/` | Test bytecode cache | YES | **YES** |
| `archive/delete_candidates/__pycache__/` | Old cache | YES | **YES** |
| `frontend/dashboard/node_modules/` | NPM dependencies | YES | **YES** |
| `frontend/dashboard/dist/` | Build output | YES | **YES** |
| `venv/` | Python virtual env | YES | **YES** |

**Total Rebuildable**: ~1.3 GB


### Large Zip Files (Review Needed)

| File | Size | Purpose | Safe to Remove |
|------|------|---------|----------------|
| `SuRaksha_Backup_Docs.zip` | Unknown | Documentation backup | **REVIEW** - Redundant if docs/ exists |
| `SuRaksha_Backup_PreCleanup.zip` | Unknown | Pre-cleanup snapshot | **KEEP** - Safety backup |
| `SuRaksha_FullRepository.zip` | Large | Complete repo backup | **REVIEW** - Redundant for Git |
| `SuRaksha_TeamHandover.zip` | Unknown | Handover package | **KEEP** - Team reference |

**Recommendation**: Check contents. If docs/ and archive/ are complete, the doc backup zips may be redundant.

### Generated Reports & Documentation

**Location**: `docs/` (60+ markdown files)

**Categories**:
- Audit reports (15+)
- Feature documentation (10+)
- Validation reports (15+)
- Integration reports (10+)
- Handover documentation (5+)

**Status**: **KEEP ALL** - Comprehensive project documentation

**Specific Files**:
| Type | Count | Keep? |
|------|-------|-------|
| Audit reports | 15 | YES - Project history |
| Feature docs | 10 | YES - Capability reference |
| Validation reports | 15 | YES - Quality evidence |
| Integration reports | 10 | YES - Architecture docs |
| Demo/handover docs | 10 | YES - User guides |

### Generated JSON Outputs (Runtime Data)

**Location**: `maps/` + root directory

| File | Purpose | Runtime Critical |
|------|---------|------------------|
| `maps/dashboard_metrics.json` | Dashboard data | **YES** |
| `maps/department_heatmap.json` | Heatmap data | **YES** |
| `maps/department_summary.json` | Summary data | **YES** |
| `maps/executive_summary.json` | Executive view | **YES** |
| `maps/graph_ui.json` | Graph visualization | **YES** |
| `maps/map_details.json` | Detail view | **YES** |
| `maps/maps_output.json` | Master output | **YES** |
| `maps/priority_summary.json` | Priority data | **YES** |
| `maps/top_risk_departments.json` | Risk data | **YES** |
| `cross_references.json` | Cross-ref data | **YES** |
| `reference_graph_v2.json` | Graph data | **YES** |
| `golden_queries.json` | Test queries | **YES** |
| `missed_references.json` | Validation data | **YES** |

**Status**: **KEEP ALL** - Frontend contract + validation data

### Empty Directories

| Directory | Purpose | Safe to Remove |
|-----------|---------|----------------|
| `dummy_dir/` | Test directory | **YES** |
| `frontend/.vscode/` | Editor settings (empty) | **YES** |
| `archive/delete_candidates/dummy_dir/` | Old test dir | **YES** |

### Editor Configuration

| File/Dir | Purpose | Safe to Remove |
|----------|---------|----------------|
| `.vscode/settings.json` | VSCode settings | **KEEP** - Dev convenience |
| `frontend/dashboard/.gitignore` | Frontend gitignore | **KEEP** - Git config |
| `frontend/dashboard/.oxlintrc.json` | Linter config | **KEEP** - Code quality |
| `venv/.gitignore` | Venv gitignore | **YES** - Redundant if venv excluded |


---

## PHASE 2: DUPLICATE & TEMPORARY FILE SCAN

### Duplicate PDFs
**Search Result**: No duplicate PDFs found in `data/dataset/rbi/`
- All 103 PDFs have unique filenames
- No `.bak`, `.copy`, or `_old` suffixes detected

### Duplicate Screenshots
**Search Result**: No screenshot files found (`.png`, `.jpg`, `.jpeg`, `.gif`)
- Project appears to be code/data only
- No image assets in repository

### Old Exported Reports
**Search Result**: Multiple timestamped reports in `docs/` and archive
- All reports appear intentional (audit trail)
- No obvious "temporary" exports

**Recommendation**: KEEP - These document project evolution

### Temporary Files Search

**Pattern**: `*.bak`, `*.old`, `*.tmp`, `*.orig`

**Results**:
- **No `.bak` files found**
- **No `.old` files found**
- **No `.tmp` files found**
- **No `.orig` files found**

✓ Repository is clean of common temporary file patterns

### Build Artifacts (Rebuildable)

**Found**:
1. **`__pycache__/`** directories (3 locations)
   - Root `__pycache__/` (5 .pyc files)
   - `tests/__pycache__/` (1 .pyc file)
   - `archive/delete_candidates/__pycache__/` (unknown count)

2. **`frontend/dashboard/node_modules/`** (~1.0 GB)
   - 100% rebuildable from `package.json` + `package-lock.json`

3. **`frontend/dashboard/dist/`**
   - Build output from Vite
   - 100% rebuildable with `npm run build`

4. **`venv/`** (~0.3 GB)
   - Python virtual environment
   - 100% rebuildable from `requirements.txt`

### Zip File Analysis

**Found**: 4 zip files in root directory

| Zip File | Estimated Purpose | Recommendation |
|----------|-------------------|----------------|
| `SuRaksha_Backup_Docs.zip` | Documentation backup | Review contents vs `docs/` |
| `SuRaksha_Backup_PreCleanup.zip` | Safety snapshot before cleanup | **KEEP** - Safety net |
| `SuRaksha_FullRepository.zip` | Complete repository backup | Review if redundant with Git |
| `SuRaksha_TeamHandover.zip` | Team transition package | **KEEP** - Handover artifact |

**Action**: Check if doc zips duplicate existing `docs/` folder

### Unused Build Artifacts

**Python Cache Files**: 
- `*.pyc` files in `__pycache__` directories
- **Safe to remove**: YES
- **Will regenerate**: Automatically on next run

**Frontend Build Output**:
- `frontend/dashboard/dist/`
- **Safe to remove**: YES
- **Will regenerate**: With `npm run build`

### Archive Directory Deep Scan

**Contents Analysis**:

**Archived Python Scripts** (~/archive/):
- `compliance_answer_engine.py` (v1)
- `compliance_answer_engine_v2.py`
- `compliance_answer_engine_v3.py`  
- `compliance_answer_engine_v4.py`
- `gap_analysis_engine.py` (v1, v2)
- `change_detector_v1.py`
- `reference_graph.py` (v1)
- Plus 10+ other archived versions

**Status**: Historical reference showing v1 → v2 → v3 evolution

**Archived Data Directories**:
- `archive/change_analysis/` - Old change detection snapshots
- `archive/demo_corpus/` - Backup of demo PDF corpus
- `archive/high_priority/` - Backup of high-priority docs

**Status**: Data backups, intentionally preserved

**Archived Reports**:
- Old validation reports
- Old graph summaries
- Phase completion markers

**Status**: Project milestone documentation

**Recommendation**: **KEEP ENTIRE ARCHIVE** - Provides traceability and historical context


---

## PHASE 3: CLEANUP PLAN

### Category 1: DEFINITELY KEEP (No Changes)

**Critical Production Code** (42 Python scripts):
- All pipeline scripts (`extract_text.py`, `chunk_documents.py`, etc.)
- All resolver/query scripts
- All map generation scripts
- All validation scripts
- All test scripts

**Critical Data Directories**:
- `data/chroma_db/`
- `data/vector_db/`
- `data/chunks/`
- `data/extracted_text/`
- `data/requirements/`
- `data/requirement_db/`
- `data/dataset/`
- `maps/`

**Documentation**:
- All files in `docs/` directory (60+ files)
- `PROJECT_STATE.md`
- `TEAM_HANDOVER.md`
- `frontend/dashboard/README.md`

**Configuration**:
- `requirements.txt`
- `frontend/dashboard/package.json`
- `frontend/dashboard/package-lock.json`
- `frontend/dashboard/vite.config.js`
- `.vscode/settings.json`

**Frontend Source**:
- All files in `frontend/dashboard/src/`
- All files in `frontend/dashboard/public/`
- `frontend/dashboard/index.html`

**Generated Data**:
- All JSON files in root (cross_references, golden_queries, etc.)
- All JSON files in `maps/`
- All report `.txt` files

**Safety Backups**:
- `SuRaksha_Backup_PreCleanup.zip`
- `SuRaksha_TeamHandover.zip`

**Total to Keep**: ~460 MB (excluding node_modules/venv)

### Category 2: PROBABLY KEEP (Historical/Reference)

**Archive Directory**:
- **Entire `archive/` folder** with all contents
- **Reason**: Historical reference, version evolution, debugging aid
- **Size**: ~50 MB
- **Decision**: **KEEP**

**One-Time Scripts** (May have historical value):
- `fix_paths.py`, `fix_paths2.py`, `refactor_paths.py`
- `phase0_backup.py`, `phase1_cleanup.py`, `phase1_path_update.py`, `phase6_zip.py`
- **Reason**: Show refactoring history, may be referenced in commit messages
- **Decision**: **KEEP** (small files, historical value)

**Zip Files** (Review contents first):
- `SuRaksha_Backup_Docs.zip`
- `SuRaksha_FullRepository.zip`
- **Decision**: **MANUAL REVIEW** before removal

### Category 3: REVIEW MANUALLY

**Zip Files** (Need content inspection):
```
- SuRaksha_Backup_Docs.zip (check if duplicates docs/)
- SuRaksha_FullRepository.zip (check if redundant with Git)
```

**Action Required**: 
1. Extract and compare contents with existing directories
2. If 100% duplicate, can remove
3. If contains unique content, keep

### Category 4: DEFINITELY SAFE TO REMOVE

**Python Bytecode Cache**:
```
__pycache__/ (root)
tests/__pycache__/
archive/delete_candidates/__pycache__/
```
**Reason**: Auto-generated, will regenerate on next run  
**Size**: <5 MB  
**Impact**: Zero (Python regenerates automatically)

**Empty Directories**:
```
dummy_dir/
frontend/.vscode/ (if empty)
```
**Reason**: No purpose  
**Size**: 0 bytes  
**Impact**: Zero

**Build Artifacts (Optional - Rebuildable)**:
```
frontend/dashboard/node_modules/ (~1.0 GB)
frontend/dashboard/dist/
venv/ (~0.3 GB)
```
**Reason**: 100% rebuildable from lock files  
**Recommendation**: Remove for GitHub, document rebuild steps in README  
**Impact**: Users must run `npm install` and `pip install -r requirements.txt`

### Cleanup Summary Table

| Category | Items | Size | Action |
|----------|-------|------|--------|
| **Definitely Keep** | Production code, data, docs | ~460 MB | NO CHANGE |
| **Probably Keep** | Archive, one-time scripts | ~50 MB | NO CHANGE |
| **Review Manually** | 2 zip files | ~200 MB? | INSPECT FIRST |
| **Safe to Remove** | Bytecode cache, empty dirs | ~5 MB | REMOVE |
| **Rebuildable** | node_modules, venv, dist | ~1.3 GB | REMOVE (GitHub) |

### Recommended Actions

**Immediate Cleanup (Safe)**:
1. Remove `__pycache__/` directories (3 locations)
2. Remove `dummy_dir/`
3. Remove empty `frontend/.vscode/` (if truly empty)

**Before GitHub Push**:
1. Remove `frontend/dashboard/node_modules/`
2. Remove `frontend/dashboard/dist/`
3. Remove `venv/`
4. Create comprehensive .gitignore

**Manual Review Required**:
1. Inspect `SuRaksha_Backup_Docs.zip`
2. Inspect `SuRaksha_FullRepository.zip`
3. Make informed decision on each

**Total Potential Cleanup**: 
- Safe immediate: ~5 MB
- Before GitHub: ~1.3 GB
- **Repository after cleanup**: ~460 MB core + ~50 MB archive = **~510 MB**


---

## PHASE 4: CLEANUP EXECUTION

### Cleanup Operations Performed

#### Operation 1: Remove Python Bytecode Cache
**Target**: `__pycache__/` directories  
**Reason**: Auto-generated, safe to remove  
**Impact**: Zero (regenerates on next Python run)

**Locations**:
- `__pycache__/` (root)
- `tests/__pycache__/`
- `archive/delete_candidates/__pycache__/`

#### Operation 2: Remove Empty Directories
**Target**: Truly empty directories  
**Reason**: No purpose

**Locations**:
- `dummy_dir/` (confirmed empty)

#### Operation 3: Do NOT Remove (Preserve All)
**The following are PRESERVED** (following conservative principle):
- ✓ `archive/` - Historical reference
- ✓ All Python scripts (including one-time scripts)
- ✓ All data directories
- ✓ All JSON files
- ✓ All documentation
- ✓ `frontend/.vscode/` - Checked, may contain settings
- ✓ Zip files - Need manual review
- ✓ `venv/` and `node_modules/` - Will handle via .gitignore for GitHub

### Files Removed Summary

| Category | Files/Dirs Removed | Size Freed |
|----------|-------------------|------------|
| Python bytecode | `__pycache__/` (3 locations) | ~5 MB |
| Empty directories | `dummy_dir/` | 0 bytes |
| **Total** | **4 items** | **~5 MB** |

### Files Preserved (Not Removed)

**All Production Assets**: 
- 42 Python scripts (root)
- 10 test scripts
- All data directories (intact)
- All maps/ JSON files
- All docs/ markdown files
- Entire archive/ folder
- All zip files (for manual review)
- venv/ (will .gitignore for GitHub)
- node_modules/ (will .gitignore for GitHub)

**Reason**: Following HIGHEST PRIORITY RULE - "Never break execution"

