"""
Create Golden Set for Resolver Evaluation
SuRaksha Phase 7 - Final Validation

Purpose: Build 25 manually verified query-requirement pairs
"""

import json
from collections import defaultdict

# Load taxonomy
print("Loading requirements taxonomy...")
with open('requirements/requirements_taxonomy.json', 'r', encoding='utf-8') as f:
    taxonomy = json.load(f)

print(f"Total requirements: {len(taxonomy)}")

# Analyze by domain and subdomain
by_domain = defaultdict(list)
by_subdomain = defaultdict(list)

for req in taxonomy:
    by_domain[req['domain']].append(req)
    subdomain = req.get('subdomain', 'Unknown')
    by_subdomain[f"{req['domain']}/{subdomain}"].append(req)

print("\nDomain distribution:")
for domain, reqs in sorted(by_domain.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {domain}: {len(reqs)}")

print("\n" + "="*80)
print("GENERATING GOLDEN SET CANDIDATES")
print("="*80)

# Key subdomains to cover
key_topics = [
    ("AML", "STR Reporting", "suspicious transaction"),
    ("AML", "CTR Reporting", "cash transaction reporting"),
    ("KYC", "Customer Identification", "customer identification"),
    ("KYC", "Customer Due Diligence", "customer due diligence"),
    ("KYC", "PEP", "politically exposed person"),
    ("Record Retention", "Record Keeping", "record retention"),
    ("Cybersecurity", "Incident Reporting", "cyber incident"),
    ("Reporting", "Regulatory Reporting", "reporting requirement"),
    ("Governance", "Board Oversight", "board approval"),
    ("Risk Management", "Risk Framework", "risk management"),
]

golden_candidates = []

for domain, subdomain_hint, query_hint in key_topics:
    # Find requirements in this category
    candidates = [r for r in taxonomy 
                  if r['domain'] == domain 
                  and (subdomain_hint.lower() in r.get('subdomain', '').lower()
                       or query_hint in r['requirement_text'].lower())]
    
    if candidates:
        # Pick the first one with substantial text
        for candidate in candidates:
            if len(candidate['requirement_text']) > 50:
                golden_candidates.append({
                    'domain': domain,
                    'subdomain': candidate.get('subdomain', 'Unknown'),
                    'requirement_id': candidate['requirement_id'],
                    'query_hint': query_hint,
                    'text_snippet': candidate['requirement_text'][:200]
                })
                break

print(f"\nFound {len(golden_candidates)} golden candidates\n")

for i, cand in enumerate(golden_candidates, 1):
    print(f"{i}. {cand['domain']}/{cand['subdomain']}")
    print(f"   Query: {cand['query_hint']}")
    print(f"   Req ID: {cand['requirement_id']}")
    print(f"   Text: {cand['text_snippet']}...")
    print()

# Show more specific examples
print("\n" + "="*80)
print("SPECIFIC REQUIREMENT EXAMPLES")
print("="*80)

# Find CTR deadline
ctr_reqs = [r for r in taxonomy if 'CTR' in r['requirement_text'] or 'cash transaction report' in r['requirement_text'].lower()]
print(f"\nCTR requirements: {len(ctr_reqs)}")
for r in ctr_reqs[:3]:
    print(f"  {r['requirement_id']}: {r['requirement_text'][:150]}...")

# Find beneficial ownership
bo_reqs = [r for r in taxonomy if 'beneficial owner' in r['requirement_text'].lower()]
print(f"\nBeneficial ownership requirements: {len(bo_reqs)}")
for r in bo_reqs[:3]:
    print(f"  {r['requirement_id']}: {r['requirement_text'][:150]}...")

# Find KYC review
kyc_review = [r for r in taxonomy if 'review' in r['requirement_text'].lower() and r['domain'] == 'KYC']
print(f"\nKYC review requirements: {len(kyc_review)}")
for r in kyc_review[:3]:
    print(f"  {r['requirement_id']}: {r['requirement_text'][:150]}...")

# Find record retention period
retention = [r for r in taxonomy if 'year' in r['requirement_text'].lower() and r['domain'] == 'Record Retention']
print(f"\nRecord retention with years: {len(retention)}")
for r in retention[:3]:
    print(f"  {r['requirement_id']}: {r['requirement_text'][:150]}...")

print("\n" + "="*80)
print("Ready to create golden_queries.json")
print("Review the above output and manually verify the most relevant requirement IDs")
print("="*80)
