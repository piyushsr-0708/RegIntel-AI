# Cross-Reference Parser - Phase 7 Module 2

## Overview

The **Cross-Reference Parser** automatically detects and extracts relationships between RBI regulatory documents by identifying circular references and their relationship types (supersedes, amends, modifies, replaces, clarifies, etc.).

## Purpose

Provides automated discovery of regulatory document lineage and dependencies for:
- Identifying superseded regulations
- Tracking amendment chains
- Building regulatory knowledge graphs
- Understanding document evolution
- Ensuring compliance with latest versions

---

## Input/Output Specification

### Input Files
**1. Taxonomy Data:** `requirements_taxonomy.json` (from Phase 7 Module 1)
**2. Chunk Data:** `chunks/*.json` (for additional context)

### Output Format
**File:** `cross_references.json`

**Structure:**
```json
{
  "metadata": {
    "generated_at": "2026-06-20T08:15:00",
    "total_references": 19,
    "unique_source_documents": 5,
    "unique_referenced_circulars": 12,
    "relationship_types_found": ["refers_to", "consolidates", "modifies"]
  },
  "statistics": {
    "by_relationship_type": {...},
    "top_referenced_circulars": [...],
    "top_source_documents": [...]
  },
  "references": [
    {
      "source_requirement_id": "REQ_25KY0107_0009_ABC123",
      "source_document": "25KY010711F.pdf",
      "referenced_circular": "CC No 46",
      "relationship_types": ["refers_to"],
      "context": "RNBCs were also advised on the same lines vide CC No 46...",
      "dates_mentioned": ["December 30, 2004"],
      "domain": "Reporting",
      "chunk_id": 9
    }
  ],
  "reference_graph": {
    "by_source_document": {...},
    "by_referenced_circular": {...},
    "by_relationship_type": {...}
  }
}
```

---

## Detection Patterns

### 1. Circular Reference Patterns

Detects standard RBI circular formats:

| Pattern | Example |
|---------|---------|
| DNBS Format | `DNBS (PD) CC No. 48/10.42/2004-05` |
| RBI Format | `RBI/2011-12/25` |
| Department Format | `DOR (NBFC) CC No. 115/03.10.001/2019-20` |
| Simple Format | `CC No. 46`, `Circular No. 184` |

### 2. Relationship Types (8 Categories)

#### **Supersedes**
- **Keywords:** supersedes, superseded by, replaces, replaced by, in supersession, withdrawn
- **Usage:** Identifies when a new regulation replaces an old one
- **Example:** "This circular supersedes DNBS (PD) CC No. 48/10.42/2004-05"

#### **Amends**
- **Keywords:** amends, amended by, revises, revised by, updates, updated by
- **Usage:** Identifies partial modifications to existing regulations
- **Example:** "This circular amends RBI/2011-12/25"

#### **Modifies**
- **Keywords:** modifies, modified, modifying, alteration, varying
- **Usage:** Identifies specific changes to provisions
- **Example:** "The notification modifies the provisions of circular CC No. 115"

#### **Replaces**
- **Keywords:** replaces, replaced, replacing, in replacement of, substitutes
- **Usage:** Identifies direct replacements
- **Example:** "This replaces the earlier instruction issued vide CC 58"

#### **Clarifies**
- **Keywords:** clarifies, clarification, explains, interpretation of
- **Usage:** Identifies explanatory circulars
- **Example:** "This circular clarifies the requirements mentioned in RBI/2020-21/45"

#### **Extends**
- **Keywords:** extends, extended, extension of, extends the deadline
- **Usage:** Identifies deadline or scope extensions
- **Example:** "This circular extends the compliance deadline"

#### **Consolidates**
- **Keywords:** consolidates, consolidated, master circular, consolidated circular
- **Usage:** Identifies master circulars that combine multiple circulars
- **Example:** "Master circular consolidated circular dated July 1, 2009"

#### **Refers To** (Default)
- **Keywords:** refers to, as per, in terms of, pursuant to, vide, details are in
- **Usage:** General references to other circulars
- **Example:** "As per DNBS (PD) CC 48/10.42/2004-05"

### 3. Date Extraction Patterns

Multiple date formats supported:
- `dated February 21, 2005`
- `dated 21 February 2005`
- `dated 21/02/2005`
- `dated 21.02.2005`

---

## CLI Execution

### Prerequisites

```cmd
# Python 3.8+
python --version

# Input files must exist:
# - requirements\requirements_taxonomy.json (from Module 1)
# - chunks\*.json (existing)
```

### Execution Steps

#### Step 1: Verify Inputs
```cmd
dir D:\SuRaksha\requirements\requirements_taxonomy.json
dir D:\SuRaksha\chunks\*.json
```

#### Step 2: Run Parser
```cmd
cd D:\SuRaksha
python cross_reference_parser.py
```

#### Step 3: Verify Output
```cmd
dir D:\SuRaksha\cross_references.json
```

### Expected Console Output

```
================================================================================
CROSS-REFERENCE PARSER - PHASE 7 MODULE 2
================================================================================

[1] Loading taxonomy data...
    Loaded: 2941 requirements

[2] Parsing references from requirements...
    Processed: 500/2941
    Processed: 1000/2941
    ...
    Found: 19 references from requirements

[3] Parsing references from chunks...
    Processed: 1494 chunks
    Found: 138 additional references

[4] Building reference graph...

[5] Saving results...
    Saved: D:\SuRaksha\cross_references.json

================================================================================
CROSS-REFERENCE STATISTICS
================================================================================

Total References Found      : 19
Unique Source Documents     : 5
Unique Referenced Circulars : 12

RELATIONSHIP TYPE DISTRIBUTION
--------------------------------------------------------------------------------
  refers_to            :   14 ( 73.7%)
  consolidates         :    6 ( 31.6%)
  modifies             :    1 (  5.3%)

TOP 10 MOST REFERENCED CIRCULARS
--------------------------------------------------------------------------------
    3 references → CC No 46
    2 references → Circular No 184
    ...

================================================================================
✓ Cross-reference parser executed successfully
================================================================================
```

---

## Results Analysis

### Your Dataset Results

**Total References:** 19  
**Source Documents:** 5  
**Referenced Circulars:** 12  

**Top Referenced Circulars:**
1. CC No 46 (3 references)
2. Circular No 184 (2 references)
3. Circular No.152 (2 references)

**Documents with Most References:**
1. 25KY010711F.pdf (8 references)
2. 41YC01072013KF.pdf (7 references)
3. 70MK010714FL.pdf (2 references)

**Relationship Distribution:**
- refers_to: 73.7% (general references)
- consolidates: 31.6% (master circulars)
- modifies: 5.3% (modifications)

---

## Testing

### Run Unit Tests

```cmd
cd D:\SuRaksha
python test_cross_reference_parser.py
```

### Test Coverage

**26 Test Cases:**
- Circular reference extraction (4 tests)
- Date extraction (2 tests)
- Relationship type detection (6 tests)
- Context extraction (2 tests)
- Reference parsing (3 tests)
- Graph building (1 test)
- Integration tests (3 tests)
- Edge cases (5 tests)

### Expected Test Output

```
================================================================================
CROSS-REFERENCE PARSER - TEST SUITE
================================================================================

test_extract_circular_references_dnbs ... ok
test_extract_circular_references_rbi ... ok
test_detect_relationship_supersedes ... ok
test_detect_relationship_amends ... ok
...

================================================================================
TEST SUMMARY
================================================================================
Tests Run     : 26
Successes     : 26
Failures      : 0
Errors        : 0
================================================================================
```

---

## Configuration

### Customize Paths

Edit lines 9-11 in `cross_reference_parser.py`:

```python
INPUT_TAXONOMY = r"D:\SuRaksha\requirements\requirements_taxonomy.json"
INPUT_CHUNKS = r"D:\SuRaksha\chunks"
OUTPUT_FILE = r"D:\SuRaksha\cross_references.json"
```

### Add New Circular Patterns

Edit `CIRCULAR_PATTERN` (line 16):

```python
CIRCULAR_PATTERN = r'(?:DNBS|RBI|YOUR_DEPT)\s*\([^)]+\)\s*(?:CC|No\.)\s*[\w/\.-]+'
```

### Add New Relationship Types

Edit `RELATIONSHIP_KEYWORDS` (line 30):

```python
RELATIONSHIP_KEYWORDS = {
    'your_relationship': [
        'keyword1', 'keyword2', 'keyword3'
    ]
}
```

---

## Python Usage Examples

### Load Cross-References

```python
import json

with open('cross_references.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

references = data['references']
graph = data['reference_graph']
```

### Find Superseded Circulars

```python
superseded = [
    ref for ref in references
    if 'supersedes' in ref['relationship_types']
]

print(f"Superseded Circulars: {len(superseded)}")
for ref in superseded:
    print(f"{ref['source_document']} supersedes {ref['referenced_circular']}")
```

### Track Amendment Chain

```python
from collections import defaultdict

# Build amendment graph
amendments = defaultdict(list)

for ref in references:
    if 'amends' in ref['relationship_types']:
        source = ref['source_document']
        target = ref['referenced_circular']
        amendments[target].append(source)

# Find circulars with multiple amendments
for circular, sources in amendments.items():
    if len(sources) > 1:
        print(f"{circular} amended by: {', '.join(sources)}")
```

### Get References by Domain

```python
kyc_refs = [
    ref for ref in references
    if ref.get('domain') == 'KYC'
]

print(f"KYC Cross-References: {len(kyc_refs)}")
```

### Find Master Circulars

```python
master_circulars = [
    ref for ref in references
    if 'consolidates' in ref['relationship_types']
]

print(f"Master Circulars: {len(master_circulars)}")
for ref in master_circulars:
    print(f"- {ref['source_document']}")
```

### Build Document Timeline

```python
from collections import defaultdict

# Group by date
by_date = defaultdict(list)

for ref in references:
    for date in ref.get('dates_mentioned', []):
        by_date[date].append(ref)

# Show references by year
for date in sorted(by_date.keys()):
    refs = by_date[date]
    print(f"{date}: {len(refs)} references")
```

---

## Integration with Other Modules

### Upstream (Input from)

**Phase 7 Module 1:** taxonomy_builder.py
- Provides: requirements_taxonomy.json
- Used for: Extracting requirement-level references

**Phase 1-2:** chunk_documents.py
- Provides: chunks/*.json
- Used for: Additional context for references

### Downstream (Output to)

**Phase 7 Module 3:** Alert Generator
- Use case: Alert when referencing superseded circulars
- Data: reference_graph.by_relationship_type['supersedes']

**Phase 8:** Audit Trail System
- Use case: Track regulatory lineage
- Data: Complete reference graph

**Phase 7 Module 4:** Impact Assessor
- Use case: Assess impact of amendments
- Data: Relationships by document

---

## Use Cases

### 1. Compliance Verification

Ensure policies reference latest (non-superseded) circulars:

```python
# Find potentially obsolete references
obsolete = []

for ref in references:
    if 'supersedes' in ref['relationship_types']:
        obsolete.append({
            'old_circular': ref['referenced_circular'],
            'new_circular': ref['source_document'],
            'context': ref['context']
        })

print(f"Found {len(obsolete)} superseded circulars to update")
```

### 2. Regulatory Knowledge Graph

Build visual graph of document relationships:

```python
import networkx as nx

G = nx.DiGraph()

for ref in references:
    source = ref['source_document']
    target = ref['referenced_circular']
    rel_type = ref['relationship_types'][0]  # Primary relationship
    
    G.add_edge(source, target, relationship=rel_type)

# Find most influential circulars (high in-degree)
central = sorted(G.in_degree, key=lambda x: x[1], reverse=True)[:10]
```

### 3. Amendment Tracking

Track all amendments to a specific circular:

```python
def get_amendments(circular_id):
    """Get all amendments to a circular"""
    amendments = []
    
    for ref in references:
        if ref['referenced_circular'] == circular_id:
            if 'amends' in ref['relationship_types']:
                amendments.append({
                    'amended_by': ref['source_document'],
                    'date': ref.get('dates_mentioned', ['Unknown'])[0],
                    'context': ref['context']
                })
    
    return sorted(amendments, key=lambda x: x['date'])
```

### 4. Consolidated View

Find all circulars consolidated in a master circular:

```python
def get_consolidated_circulars(master_circular_doc):
    """Get all circulars consolidated in a master circular"""
    consolidated = []
    
    for ref in references:
        if ref['source_document'] == master_circular_doc:
            if 'consolidates' in ref['relationship_types']:
                consolidated.append(ref['referenced_circular'])
    
    return consolidated
```

---

## Performance

**Typical Execution Metrics:**

| Metric | Value |
|--------|-------|
| Input Records | 2,941 requirements + 1,494 chunks |
| Processing Time | ~8-12 seconds |
| References Found | 19 (varies by dataset) |
| Output File Size | ~50-200 KB |
| Memory Usage | <150 MB |

---

## Troubleshooting

### Low Reference Count

**Issue:** Found fewer references than expected

**Solutions:**
1. Check if source documents contain circular references
2. Review CIRCULAR_PATTERN regex for your dataset
3. Add more department prefixes (DNBS, RBI, DOR, etc.)
4. Check chunk data is available

### False Positives

**Issue:** Detecting irrelevant text as references

**Solutions:**
1. Tighten CIRCULAR_PATTERN regex
2. Add more context validation
3. Filter by minimum reference length
4. Review keyword patterns

### Missing Relationship Types

**Issue:** Relationships classified as "refers_to" instead of specific type

**Solutions:**
1. Add more keywords to RELATIONSHIP_KEYWORDS
2. Check keyword case sensitivity
3. Review context window size
4. Add domain-specific patterns

### Date Extraction Issues

**Issue:** Dates not extracted correctly

**Solutions:**
1. Add more date patterns to DATE_PATTERNS
2. Check date format in your documents
3. Verify regex patterns match your format

---

## Output File Structure

### Complete Schema

```json
{
  "metadata": {
    "generated_at": "ISO timestamp",
    "total_references": integer,
    "unique_source_documents": integer,
    "unique_referenced_circulars": integer,
    "relationship_types_found": [array of strings]
  },
  "statistics": {
    "by_relationship_type": {
      "relationship_name": count
    },
    "top_referenced_circulars": [
      [circular_id, count]
    ],
    "top_source_documents": [
      [document_name, count]
    ]
  },
  "references": [
    {
      "source_requirement_id": "string",
      "source_document": "string",
      "referenced_circular": "string",
      "relationship_types": [array],
      "context": "string",
      "dates_mentioned": [array],
      "domain": "string",
      "chunk_id": integer
    }
  ],
  "reference_graph": {
    "by_source_document": {
      "document_name": [array of references]
    },
    "by_referenced_circular": {
      "circular_id": [array of references]
    },
    "by_relationship_type": {
      "relationship_name": [array of references]
    }
  }
}
```

---

## Limitations

### Current Implementation

1. **Pattern-Based:** Uses regex patterns, may miss non-standard formats
2. **English Only:** Optimized for English language circulars
3. **Context Dependent:** Accuracy depends on context window quality
4. **Single-Level:** Does not build multi-level dependency chains (A→B→C)

### Known Issues

1. **Abbreviations:** May not detect all abbreviated circular names
2. **Informal References:** Misses conversational references ("previous circular")
3. **Implicit References:** Cannot detect implied relationships without keywords
4. **OCR Errors:** Sensitivity to PDF extraction quality

### Future Enhancements

1. Multi-level dependency tracking
2. Machine learning for relationship classification
3. Support for non-standard reference formats
4. Confidence scores for detected relationships
5. Automatic version numbering for amendments

---

## Version History

**v1.0 - June 20, 2026**
- Initial release
- 8 relationship types
- Pattern-based reference extraction
- Graph building capabilities
- 19 references detected from 2,941 requirements

---

## Next Steps

**Phase 7 Module 3:** Alert Generator
- Input: cross_references.json
- Function: Generate alerts when using superseded circulars
- Feature: Track compliance with latest versions

**Phase 8:** Regulatory Knowledge Graph
- Input: cross_references.json
- Function: Build visual graph of document relationships
- Feature: Interactive exploration of regulatory lineage

---

## Support

For issues or questions:
1. Review sample references in output
2. Check console statistics
3. Validate input file formats
4. Run test suite for verification

---

**Module Status:** ✓ Production Ready  
**Integration:** Phase 7 Module 2 complete, ready for downstream modules
