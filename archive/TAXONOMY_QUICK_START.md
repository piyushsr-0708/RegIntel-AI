# Taxonomy Builder - Quick Start Guide

## 🚀 Execution

```cmd
cd D:\SuRaksha
python taxonomy_builder.py
```

**Runtime:** ~5-8 seconds for 2,941 requirements

---

## 📊 Results Summary

### Processed Dataset
- **Input:** `requirements_clean.json` (2,941 requirements)
- **Output:** `requirements_taxonomy.json` (1.68 MB)
- **Success Rate:** 100%

### Domain Distribution
| Domain | Count | % |
|--------|-------|---|
| General | 903 | 30.7% |
| AML | 613 | 20.8% |
| KYC | 468 | 15.9% |
| Reporting | 296 | 10.1% |
| Record Retention | 287 | 9.8% |
| Governance | 136 | 4.6% |
| Technology | 117 | 4.0% |
| Cybersecurity | 90 | 3.1% |
| Risk Management | 31 | 1.1% |

### Obligation Type Distribution
| Type | Count | % |
|------|-------|---|
| Mandatory | 1,103 | 37.5% |
| Recommended | 624 | 21.2% |
| Conditional | 617 | 21.0% |
| Informational | 528 | 18.0% |
| Prohibited | 69 | 2.3% |

### Effective Status
| Status | Count | % |
|--------|-------|---|
| Active | 2,902 | 98.7% |
| Proposed | 39 | 1.3% |
| Superseded | 0 | 0.0% |

---

## 📝 Output Schema

```json
{
  "requirement_id": "REQ_25KY0107_0003_6721FA",
  "domain": "Governance",
  "subdomain": "Policy Framework",
  "obligation_type": "Recommended",
  "source_document": "25KY010711F.pdf",
  "effective_status": "Active",
  "requirement_text": "Full text...",
  "entity": "nbfcs",
  "deadline": "three months",
  "chunk_id": 3
}
```

---

## 🔍 Query Examples

### Filter by Domain (Python)
```python
import json

with open('requirements/requirements_taxonomy.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all KYC requirements
kyc_reqs = [r for r in data if r['domain'] == 'KYC']
print(f"KYC Requirements: {len(kyc_reqs)}")  # Output: 468

# Get all mandatory AML requirements
mandatory_aml = [r for r in data 
                 if r['domain'] == 'AML' 
                 and r['obligation_type'] == 'Mandatory']
print(f"Mandatory AML: {len(mandatory_aml)}")

# Get cybersecurity requirements with deadlines
cyber_deadlines = [r for r in data 
                   if r['domain'] == 'Cybersecurity' 
                   and r['deadline']]
```

### Group by Source Document
```python
from collections import defaultdict

by_source = defaultdict(list)
for req in data:
    by_source[req['source_document']].append(req)

# Show requirements per document
for doc, reqs in sorted(by_source.items()):
    print(f"{doc}: {len(reqs)} requirements")
```

### Find High-Priority Requirements
```python
# Prohibited actions (must not do)
prohibited = [r for r in data if r['obligation_type'] == 'Prohibited']
print(f"Prohibited: {len(prohibited)}")  # Output: 69

# Mandatory with short deadlines
urgent = [r for r in data 
          if r['obligation_type'] == 'Mandatory' 
          and any(keyword in r['deadline'].lower() 
                  for keyword in ['day', 'days', 'hour', 'hours'])]
```

---

## ✅ Testing

```cmd
python test_taxonomy_builder.py
```

**Expected Result:**
```
Tests Run     : 18
Successes     : 18
Failures      : 0
Errors        : 0
```

---

## 📂 File Locations

```
D:\SuRaksha\
├── taxonomy_builder.py                      # Main module
├── test_taxonomy_builder.py                 # Test suite (18 tests)
├── sample_taxonomy_output.json              # Sample output
├── TAXONOMY_BUILDER_README.md               # Full documentation
├── TAXONOMY_QUICK_START.md                  # This file
└── requirements\
    ├── requirements_clean.json              # Input (2,941 reqs)
    └── requirements_taxonomy.json           # Output (generated)
```

---

## 🔧 Customization

### Change Input/Output Paths
Edit `taxonomy_builder.py` lines 9-10:
```python
INPUT_FILE = r"D:\SuRaksha\requirements\requirements_clean.json"
OUTPUT_FILE = r"D:\SuRaksha\requirements\requirements_taxonomy.json"
```

### Add New Domain
Edit `DOMAIN_RULES` in `taxonomy_builder.py`:
```python
"Your_Domain": {
    "keywords": ["keyword1", "keyword2"],
    "subdomains": {
        "Your_Subdomain": ["keyword3", "keyword4"]
    }
}
```

---

## 🎯 Use Cases

### Compliance Dashboard
```python
# Calculate compliance metrics
total = len(data)
mandatory = len([r for r in data if r['obligation_type'] == 'Mandatory'])
compliant_rate = (mandatory / total) * 100
print(f"Mandatory Compliance Requirements: {mandatory}/{total} ({compliant_rate:.1f}%)")
```

### Regulatory Impact Assessment
```python
# Analyze new circular
new_circular = "KYC09062025.pdf"
new_reqs = [r for r in data if r['source_document'] == new_circular]

mandatory = [r for r in new_reqs if r['obligation_type'] == 'Mandatory']
with_deadlines = [r for r in new_reqs if r['deadline']]

print(f"New Circular: {new_circular}")
print(f"  Total Requirements: {len(new_reqs)}")
print(f"  Mandatory: {len(mandatory)}")
print(f"  With Deadlines: {len(with_deadlines)}")
```

### Stakeholder Assignment
```python
# Route requirements to teams
routing_map = {
    'KYC': 'Compliance Team',
    'AML': 'Compliance Team',
    'Cybersecurity': 'IT Security Team',
    'Technology': 'IT Team',
    'Governance': 'Board & Management',
    'Risk Management': 'Risk Team',
    'Reporting': 'Compliance Team',
    'Record Retention': 'Operations Team'
}

for req in data:
    req['assigned_to'] = routing_map.get(req['domain'], 'Unassigned')
```

---

## 📊 Statistics Breakdown

### Top 5 Source Documents
```python
from collections import Counter

doc_counts = Counter(r['source_document'] for r in data)
for doc, count in doc_counts.most_common(5):
    print(f"{doc}: {count}")
```

### Deadline Analysis
```python
with_deadlines = [r for r in data if r['deadline']]
print(f"Requirements with Deadlines: {len(with_deadlines)}")

# Common deadline patterns
deadline_patterns = Counter(r['deadline'] for r in with_deadlines)
for pattern, count in deadline_patterns.most_common(10):
    print(f"  {pattern}: {count}")
```

---

## 🚨 Troubleshooting

### Issue: File not found error
```cmd
# Verify input file exists
dir D:\SuRaksha\requirements\requirements_clean.json
```

### Issue: Low accuracy in classification
- Review classification rules in `DOMAIN_RULES`
- Add domain-specific keywords
- Check requirement text quality

### Issue: Slow performance
- Normal: ~5-8 seconds for 2,941 requirements
- If slower: Check disk I/O or antivirus interference

---

## 📈 Next Steps

### Phase 7 Module 2: Impact Assessor
```python
# Use taxonomy output as input
# Add complexity scoring
# Add cost estimation
# Add stakeholder routing
```

### Phase 7 Module 3: Alert Generator
```python
# Use impact analysis output
# Generate priority-based alerts
# Add deadline tracking
# Add escalation workflows
```

### Phase 8: Audit Trail System
```python
# Use requirement_id as primary key
# Link evidence documents
# Track compliance status
# Generate audit packages
```

---

## 📞 Support

For full documentation, see: `TAXONOMY_BUILDER_README.md`

For code details, review:
- `taxonomy_builder.py` - Main implementation
- `test_taxonomy_builder.py` - Test cases
- `sample_taxonomy_output.json` - Expected output format
