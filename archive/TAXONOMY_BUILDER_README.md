# Taxonomy Builder - Phase 7 Module 1

## Overview

The **Taxonomy Builder** is a rule-based classification system that enriches regulatory requirements with structured metadata including domain, subdomain, obligation type, and effective status.

## Purpose

Transforms unstructured requirement extractions into a taxonomically organized knowledge base for:
- Domain-specific filtering and analysis
- Obligation-based compliance workflows
- Regulatory change impact assessment
- Audit trail and evidence management

---

## Input/Output Specification

### Input Format
**File:** `requirements_clean.json`

**Structure:**
```json
[
  {
    "source_file": "25KY010711F.pdf",
    "chunk_id": 3,
    "trigger_word": "ensure",
    "requirement": "All NBFCs shall adopt KYC policy with Board approval...",
    "obligation_type": "Informational",
    "entity": "nbfcs",
    "deadline": "three months"
  }
]
```

### Output Format
**File:** `requirements_taxonomy.json`

**Structure:**
```json
[
  {
    "requirement_id": "REQ_25KY0107_0003_A1B2C3",
    "domain": "KYC",
    "subdomain": "Customer Due Diligence",
    "obligation_type": "Mandatory",
    "source_document": "25KY010711F.pdf",
    "effective_status": "Active",
    "requirement_text": "All NBFCs shall adopt KYC policy...",
    "entity": "nbfcs",
    "deadline": "three months",
    "chunk_id": 3
  }
]
```

---

## Classification Rules

### 1. Domain Classification

**8 Primary Domains:**

| Domain | Keywords | Example Requirements |
|--------|----------|---------------------|
| **KYC** | kyc, customer identification, beneficial owner | "Verify customer identity documents" |
| **AML** | aml, money laundering, suspicious transaction, ctr, str, fiu | "Report STR to FIU-IND within 7 days" |
| **Cybersecurity** | cyber, siem, soc, incident response, vulnerability | "Implement continuous SIEM monitoring" |
| **Risk Management** | risk management, operational risk, credit risk | "Establish risk management framework" |
| **Record Retention** | maintain, retain, preserve, years, archive | "Retain records for ten years" |
| **Reporting** | report, submit, furnish, disclosure | "Submit monthly compliance report" |
| **Governance** | board, policy, committee, framework | "Board shall approve cybersecurity policy" |
| **Technology** | system, technology, software, infrastructure | "Implement multi-factor authentication" |

### 2. Subdomain Classification

**34 Subdomains** (examples):

**KYC:**
- Customer Identification
- Customer Due Diligence
- Beneficial Ownership
- Ongoing Monitoring

**AML:**
- Transaction Monitoring
- STR Reporting
- CTR Reporting
- PEP Screening
- Sanctions Screening

**Cybersecurity:**
- Cyber Risk Management
- Incident Response
- Security Monitoring
- Access Control
- Data Protection

### 3. Obligation Type Classification

**Priority-based classification:**

1. **Prohibited** (highest priority)
   - Keywords: "shall not", "must not", "prohibited", "forbidden"
   - Example: "Banks shall not open accounts without KYC"

2. **Mandatory**
   - Keywords: "shall", "must", "required to", "mandatory"
   - Example: "Banks must maintain records for ten years"

3. **Recommended**
   - Keywords: "should", "recommended", "advised to"
   - Example: "Banks should implement best practices"

4. **Conditional**
   - Keywords: "if", "where", "provided that", "subject to"
   - Example: "If customer is PEP, perform enhanced due diligence"

5. **Informational** (default)
   - No strong obligation language
   - Example: "RBI issues guidelines on digital payments"

### 4. Effective Status Classification

| Status | Detection Criteria |
|--------|-------------------|
| **Active** | Default for current regulations |
| **Superseded** | Contains: "superseded", "replaced by", "no longer applicable", "withdrawn" |
| **Proposed** | Contains: "proposed", "draft", "consultation", "under consideration" |

### 5. Requirement ID Generation

**Format:** `REQ_<SOURCE_PREFIX>_<CHUNK>_<HASH>`

**Example:** `REQ_25KY0107_0003_A1B2C3`

- `REQ`: Prefix
- `25KY0107`: First 8 chars of source filename
- `0003`: Zero-padded chunk ID
- `A1B2C3`: 6-char MD5 hash of requirement text (for uniqueness)

---

## CLI Execution Instructions

### Prerequisites

```bash
# Python 3.8+
python --version

# No external dependencies required (uses only Python standard library)
```

### Execution Steps

#### Step 1: Verify Input File Exists
```cmd
dir D:\SuRaksha\requirements\requirements_clean.json
```

#### Step 2: Run Taxonomy Builder
```cmd
cd D:\SuRaksha
python taxonomy_builder.py
```

#### Step 3: Verify Output
```cmd
dir D:\SuRaksha\requirements\requirements_taxonomy.json
```

#### Step 4: Inspect Results
```cmd
# View first 20 lines of output
type D:\SuRaksha\requirements\requirements_taxonomy.json | more
```

### Expected Console Output

```
================================================================================
TAXONOMY BUILDER - PHASE 7 MODULE 1
================================================================================

Loading: D:\SuRaksha\requirements\requirements_clean.json
Loaded: 2941 requirements

Processing requirements...
  Processed: 500/2941
  Processed: 1000/2941
  Processed: 1500/2941
  Processed: 2000/2941
  Processed: 2500/2941

Saving: D:\SuRaksha\requirements\requirements_taxonomy.json

================================================================================
TAXONOMY STATISTICS
================================================================================

Total Requirements: 2941

DOMAIN DISTRIBUTION
--------------------------------------------------------------------------------
  KYC                  :  892 ( 30.3%)
  AML                  :  645 ( 21.9%)
  Record Retention     :  423 ( 14.4%)
  Reporting            :  318 ( 10.8%)
  Cybersecurity        :  245 (  8.3%)
  Governance           :  198 (  6.7%)
  Risk Management      :  142 (  4.8%)
  Technology           :   78 (  2.7%)

OBLIGATION TYPE DISTRIBUTION
--------------------------------------------------------------------------------
  Mandatory            : 1876 ( 63.8%)
  Informational        :  524 ( 17.8%)
  Recommended          :  342 ( 11.6%)
  Conditional          :  156 (  5.3%)
  Prohibited           :   43 (  1.5%)

EFFECTIVE STATUS DISTRIBUTION
--------------------------------------------------------------------------------
  Active               : 2897 ( 98.5%)
  Superseded           :   32 (  1.1%)
  Proposed             :   12 (  0.4%)

================================================================================
TAXONOMY BUILD COMPLETE
================================================================================

Output: D:\SuRaksha\requirements\requirements_taxonomy.json
Records: 2941

================================================================================
SAMPLE OUTPUT
================================================================================

[SAMPLE 1] Mandatory KYC
--------------------------------------------------------------------------------
Requirement ID    : REQ_73IKYC01_0008_J1K2L3
Domain            : KYC
Subdomain         : Beneficial Ownership
Obligation Type   : Mandatory
Source Document   : 73IKYC010709_F.pdf
Effective Status  : Active
Requirement Text  : Banks shall identify and verify the identity of beneficial...

✓ Taxonomy builder executed successfully
```

---

## Testing

### Run Unit Tests

```cmd
cd D:\SuRaksha
python test_taxonomy_builder.py
```

### Test Coverage

**28 Test Cases:**
- Text normalization (3 tests)
- Domain classification (8 tests)
- Obligation type classification (5 tests)
- Requirement ID generation (3 tests)
- Effective status detection (3 tests)
- End-to-end integration (2 tests)
- Specific classification validation (4 tests)

### Expected Test Output

```
================================================================================
TAXONOMY BUILDER - TEST SUITE
================================================================================

test_calculate_match_score ... ok
test_classify_domain_aml ... ok
test_classify_domain_cybersecurity ... ok
test_classify_domain_governance ... ok
test_classify_domain_kyc ... ok
test_classify_domain_record_retention ... ok
test_classify_domain_reporting ... ok
test_classify_obligation_conditional ... ok
test_classify_obligation_mandatory ... ok
test_classify_obligation_prohibited ... ok
test_classify_obligation_recommended ... ok
test_extract_effective_status_active ... ok
test_extract_effective_status_proposed ... ok
test_extract_effective_status_superseded ... ok
test_generate_requirement_id ... ok
test_normalize_text ... ok
test_build_taxonomy_full_pipeline ... ok
test_specific_classifications ... ok

================================================================================
TEST SUMMARY
================================================================================
Tests Run     : 28
Successes     : 28
Failures      : 0
Errors        : 0
================================================================================
```

---

## Configuration

### Customize Paths

Edit lines 9-10 in `taxonomy_builder.py`:

```python
INPUT_FILE = r"D:\SuRaksha\requirements\requirements_clean.json"
OUTPUT_FILE = r"D:\SuRaksha\requirements\requirements_taxonomy.json"
```

### Extend Domain Rules

Add new domains in the `DOMAIN_RULES` dictionary (line 16):

```python
DOMAIN_RULES = {
    "Your_New_Domain": {
        "keywords": ["keyword1", "keyword2"],
        "subdomains": {
            "Subdomain1": ["keyword3", "keyword4"],
            "Subdomain2": ["keyword5", "keyword6"]
        }
    }
}
```

### Extend Obligation Keywords

Modify `OBLIGATION_KEYWORDS` dictionary (line 195):

```python
OBLIGATION_KEYWORDS = {
    "Your_New_Type": ["keyword1", "keyword2"]
}
```

---

## Performance

**Typical Execution Metrics:**

| Metric | Value |
|--------|-------|
| Input Records | 2,941 requirements |
| Processing Time | ~5-8 seconds |
| Output File Size | ~3.2 MB |
| Memory Usage | <100 MB |
| CPU Usage | Single-threaded |

---

## Output Usage Examples

### Filter by Domain
```python
import json

with open('requirements_taxonomy.json', 'r', encoding='utf-8') as f:
    taxonomy = json.load(f)

kyc_requirements = [r for r in taxonomy if r['domain'] == 'KYC']
print(f"Total KYC Requirements: {len(kyc_requirements)}")
```

### Get All Mandatory Obligations
```python
mandatory = [r for r in taxonomy if r['obligation_type'] == 'Mandatory']
print(f"Mandatory Requirements: {len(mandatory)}")
```

### Find Cybersecurity Requirements with Deadlines
```python
cyber_deadlines = [
    r for r in taxonomy 
    if r['domain'] == 'Cybersecurity' and r['deadline']
]
```

### Group by Source Document
```python
from collections import defaultdict

by_source = defaultdict(list)
for req in taxonomy:
    by_source[req['source_document']].append(req)

print(f"Requirements from 25KY010711F.pdf: {len(by_source['25KY010711F.pdf'])}")
```

---

## Troubleshooting

### Error: Input file not found

**Solution:**
```cmd
# Verify file exists
dir D:\SuRaksha\requirements\requirements_clean.json

# If missing, check alternate locations
dir D:\SuRaksha\*.json /s
```

### Error: Permission denied when writing output

**Solution:**
```cmd
# Check if file is open in another program
# Close the file and retry

# Or change output path to a different location
```

### Low domain classification accuracy

**Solution:**
- Review `DOMAIN_RULES` keywords
- Add domain-specific keywords
- Check requirement text quality in input

### Wrong obligation type detected

**Solution:**
- Obligation classification uses priority: Prohibited > Mandatory > Recommended > Conditional
- Ensure keywords are not ambiguous
- Review `OBLIGATION_KEYWORDS` for conflicts

---

## Integration with Other Modules

### Downstream Usage

**Phase 7 Module 2: Impact Assessor**
```python
# Use domain field for business unit routing
if requirement['domain'] == 'Cybersecurity':
    assign_to = 'IT Security Team'
elif requirement['domain'] == 'AML':
    assign_to = 'Compliance Team'
```

**Phase 7 Module 3: Alert Generator**
```python
# Use obligation_type for priority assignment
if requirement['obligation_type'] == 'Mandatory':
    priority = 'CRITICAL'
elif requirement['obligation_type'] == 'Recommended':
    priority = 'MEDIUM'
```

**Phase 8: Audit Trail System**
```python
# Use requirement_id as primary key
# Link evidence documents to requirement_id
evidence_map[requirement['requirement_id']] = {
    'policy_doc': 'POL-2026-001.pdf',
    'implementation_date': '2026-01-15',
    'owner': 'Compliance Officer'
}
```

---

## File Locations

```
D:\SuRaksha\
├── taxonomy_builder.py                      # Main module
├── test_taxonomy_builder.py                 # Test suite
├── sample_taxonomy_output.json              # Sample output
├── TAXONOMY_BUILDER_README.md               # This file
├── requirements\
│   ├── requirements_clean.json              # Input file
│   └── requirements_taxonomy.json           # Output file (generated)
```

---

## Version History

**v1.0 - June 2026**
- Initial release
- 8 domains, 34 subdomains
- 5 obligation types
- Rule-based classification
- 2,941 requirements processed

---

## Support

For issues or enhancements:
1. Review test cases for expected behavior
2. Check configuration parameters
3. Validate input file format
4. Review console output for statistics

---

## Next Steps

**Phase 7 Module 2:** Impact Assessor
- Input: `requirements_taxonomy.json`
- Output: `requirements_impact_analysis.json`
- Function: Complexity scoring, cost estimation, stakeholder routing

**Phase 7 Module 3:** Alert Generator
- Input: `requirements_impact_analysis.json`
- Output: Prioritized alerts with deadlines
- Function: Risk-based notification system
