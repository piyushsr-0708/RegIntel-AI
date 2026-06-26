import json
import re
import hashlib
from typing import Dict, List, Tuple
from datetime import datetime

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = str(PROJECT_ROOT / "data/requirements/requirements_clean.json")
OUTPUT_FILE = str(PROJECT_ROOT / "data/requirements/requirements_taxonomy.json")

# ============================================================
# DOMAIN & SUBDOMAIN CLASSIFICATION RULES
# ============================================================

DOMAIN_RULES = {
    "KYC": {
        "keywords": [
            "kyc", "know your customer", "customer identification",
            "customer due diligence", "cdd", "identity verification",
            "customer acceptance", "proof of identity", "proof of address",
            "identity documents", "beneficial owner", "beneficial ownership",
            "client identification", "customer verification"
        ],
        "subdomains": {
            "Customer Identification": [
                "identity verification", "proof of identity", "identity documents",
                "identification documents", "customer identification",
                "identity proof", "officially valid document"
            ],
            "Customer Due Diligence": [
                "due diligence", "cdd", "customer due diligence",
                "risk assessment", "customer profiling", "risk categorization"
            ],
            "Beneficial Ownership": [
                "beneficial owner", "beneficial ownership", "ultimate beneficial",
                "controlling person", "natural person"
            ],
            "Ongoing Monitoring": [
                "ongoing monitoring", "periodic review", "update customer",
                "refresh kyc", "periodic updation"
            ]
        }
    },
    
    "AML": {
        "keywords": [
            "aml", "anti-money laundering", "money laundering", "terrorist financing",
            "suspicious transaction", "str", "ctr", "cash transaction",
            "fiu", "fiu-ind", "pep", "politically exposed", "sanctions",
            "screening", "transaction monitoring"
        ],
        "subdomains": {
            "Transaction Monitoring": [
                "transaction monitoring", "suspicious transaction",
                "unusual transaction", "monitor transaction",
                "transaction pattern", "transaction alert"
            ],
            "STR Reporting": [
                "str", "suspicious transaction report", "reporting to fiu",
                "fiu-ind", "furnish to fiu", "report suspicious"
            ],
            "CTR Reporting": [
                "ctr", "cash transaction report", "cash transaction",
                "currency transaction", "15th of the succeeding month"
            ],
            "PEP Screening": [
                "pep", "politically exposed person", "politically exposed",
                "pep screening", "enhanced due diligence"
            ],
            "Sanctions Screening": [
                "sanctions", "unsc", "ofac", "screening",
                "sanctioned entities", "designated individuals"
            ]
        }
    },
    
    "Cybersecurity": {
        "keywords": [
            "cyber", "cybersecurity", "information security", "cyber security",
            "data security", "network security", "endpoint security",
            "vulnerability", "penetration test", "siem", "soc",
            "incident response", "cyber attack", "data breach",
            "encryption", "firewall", "antivirus", "malware"
        ],
        "subdomains": {
            "Cyber Risk Management": [
                "cyber risk", "risk management", "cyber resilience",
                "risk assessment", "threat assessment"
            ],
            "Incident Response": [
                "incident response", "cyber incident", "security incident",
                "incident management", "breach response"
            ],
            "Security Monitoring": [
                "siem", "soc", "security monitoring", "continuous monitoring",
                "real time monitoring", "threat monitoring"
            ],
            "Access Control": [
                "access control", "authentication", "authorization",
                "privileged access", "user access"
            ],
            "Data Protection": [
                "data security", "encryption", "data protection",
                "data privacy", "sensitive data"
            ]
        }
    },
    
    "Risk Management": {
        "keywords": [
            "risk management", "operational risk", "credit risk",
            "market risk", "liquidity risk", "risk appetite",
            "risk framework", "risk governance", "risk mitigation",
            "internal control", "internal audit"
        ],
        "subdomains": {
            "Operational Risk": [
                "operational risk", "process risk", "operational loss",
                "operational failure"
            ],
            "Credit Risk": [
                "credit risk", "default risk", "counterparty risk",
                "credit exposure"
            ],
            "Market Risk": [
                "market risk", "price risk", "interest rate risk",
                "foreign exchange risk"
            ],
            "Risk Governance": [
                "risk governance", "risk framework", "risk policy",
                "risk committee", "board approval"
            ]
        }
    },
    
    "Record Retention": {
        "keywords": [
            "record", "retention", "maintain", "preserve", "retain",
            "record keeping", "documentation", "years", "year",
            "archive", "storage"
        ],
        "subdomains": {
            "Transaction Records": [
                "transaction record", "account record", "payment record",
                "maintain record of transaction"
            ],
            "KYC Records": [
                "kyc record", "customer record", "identity record",
                "customer information file"
            ],
            "Audit Trail": [
                "audit trail", "audit log", "system log",
                "transaction log"
            ],
            "Retention Period": [
                "five years", "ten years", "retention period",
                "preserve for", "maintain for"
            ]
        }
    },
    
    "Reporting": {
        "keywords": [
            "report", "reporting", "submit", "furnish", "file",
            "return", "statement", "disclosure"
        ],
        "subdomains": {
            "Regulatory Reporting": [
                "regulatory report", "submit to rbi", "furnish to",
                "report to reserve bank"
            ],
            "Periodic Reporting": [
                "monthly report", "quarterly report", "annual report",
                "periodic reporting", "half-yearly"
            ],
            "Incident Reporting": [
                "incident report", "report incident", "cyber incident",
                "security incident", "breach report"
            ],
            "Compliance Reporting": [
                "compliance report", "compliance return",
                "compliance certificate"
            ]
        }
    },
    
    "Governance": {
        "keywords": [
            "board", "governance", "director", "committee",
            "policy", "framework", "approval", "oversight",
            "senior management", "ceo", "compliance officer"
        ],
        "subdomains": {
            "Board Oversight": [
                "board", "board approval", "board of directors",
                "board oversight"
            ],
            "Policy Framework": [
                "policy", "framework", "policy framework",
                "formulate policy", "approve policy"
            ],
            "Committee Structure": [
                "committee", "risk committee", "audit committee",
                "it committee"
            ],
            "Roles & Responsibilities": [
                "compliance officer", "chief information security officer",
                "principal officer", "designated director"
            ]
        }
    },
    
    "Technology": {
        "keywords": [
            "system", "technology", "software", "application",
            "infrastructure", "network", "database", "digital",
            "electronic", "automation", "api", "cloud"
        ],
        "subdomains": {
            "System Security": [
                "system security", "application security",
                "secure system", "security controls"
            ],
            "Infrastructure": [
                "infrastructure", "network", "server", "data center",
                "cloud infrastructure"
            ],
            "Digital Services": [
                "digital", "digital payment", "electronic",
                "online service", "mobile application"
            ],
            "Technology Governance": [
                "technology governance", "it governance",
                "it policy", "it framework"
            ]
        }
    }
}

# ============================================================
# OBLIGATION TYPE CLASSIFICATION
# ============================================================

OBLIGATION_KEYWORDS = {
    "Mandatory": [
        "shall", "must", "required to", "mandatory", "obliged to",
        "have to", "need to", "ought to", "bound to"
    ],
    "Recommended": [
        "should", "recommended", "advised to", "may ensure",
        "encouraged to", "suggested", "desirable", "prudent"
    ],
    "Prohibited": [
        "shall not", "must not", "prohibited", "forbidden",
        "not allowed", "not permitted", "restricted"
    ],
    "Conditional": [
        "if", "where", "in case", "provided that", "subject to",
        "when", "unless", "except"
    ]
}

# ============================================================
# EFFECTIVE STATUS CLASSIFICATION
# ============================================================

def extract_effective_status(requirement: str, source_file: str, deadline: str) -> str:
    """
    Determine if requirement is Active, Superseded, or Proposed
    """
    
    req_lower = requirement.lower()
    
    # Check for superseded indicators
    superseded_patterns = [
        "has been superseded",
        "is replaced by",
        "no longer applicable",
        "withdrawn",
        "repealed",
        "rescinded"
    ]
    
    for pattern in superseded_patterns:
        if pattern in req_lower:
            return "Superseded"
    
    # Check for proposed/draft indicators
    proposed_patterns = [
        "proposed",
        "draft",
        "under consideration",
        "consultation",
        "for discussion"
    ]
    
    for pattern in proposed_patterns:
        if pattern in req_lower:
            return "Proposed"
    
    # Check deadline to see if it's past
    if deadline:
        # Extract years from deadline
        year_match = re.search(r'\b(20\d{2})\b', deadline)
        if year_match:
            deadline_year = int(year_match.group(1))
            current_year = datetime.now().year
            
            # If deadline is more than 2 years old, might be superseded
            # But we'll mark as Active by default
            pass
    
    # Default is Active
    return "Active"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(text: str) -> str:
    """Normalize text for matching"""
    return text.lower().strip()


def calculate_match_score(text: str, keywords: List[str]) -> int:
    """Calculate match score based on keyword presence"""
    text_lower = normalize_text(text)
    score = 0
    
    for keyword in keywords:
        if keyword in text_lower:
            # Weight longer keywords higher
            score += len(keyword.split())
    
    return score


def classify_domain(requirement: str) -> Tuple[str, str]:
    """
    Classify requirement into domain and subdomain
    Returns: (domain, subdomain)
    """
    
    req_lower = normalize_text(requirement)
    
    best_domain = "General"
    best_subdomain = "Miscellaneous"
    best_score = 0
    
    # Score each domain
    for domain, rules in DOMAIN_RULES.items():
        domain_score = calculate_match_score(req_lower, rules["keywords"])
        
        if domain_score > best_score:
            best_score = domain_score
            best_domain = domain
            
            # Find best subdomain
            subdomain_scores = {}
            for subdomain, keywords in rules["subdomains"].items():
                subdomain_score = calculate_match_score(req_lower, keywords)
                subdomain_scores[subdomain] = subdomain_score
            
            if subdomain_scores:
                best_subdomain = max(subdomain_scores, key=subdomain_scores.get)
                
                # If no subdomain matches well, use "Other"
                if subdomain_scores[best_subdomain] == 0:
                    best_subdomain = "Other"
    
    return best_domain, best_subdomain


def classify_obligation_type(requirement: str, existing_type: str) -> str:
    """
    Classify obligation type with priority system
    Returns: Mandatory | Recommended | Prohibited | Conditional | Informational
    """
    
    req_lower = normalize_text(requirement)
    
    # Priority 1: Check for Conditional first (sentences starting with conditional keywords)
    # This handles "If X, then Y shall Z" cases
    req_start = req_lower[:50]  # Check first 50 chars for conditional start
    for keyword in OBLIGATION_KEYWORDS["Conditional"]:
        if req_start.startswith(keyword) or f" {keyword} " in req_start:
            return "Conditional"
    
    # Priority 2: Prohibited (most restrictive)
    for keyword in OBLIGATION_KEYWORDS["Prohibited"]:
        if keyword in req_lower:
            return "Prohibited"
    
    # Priority 3: Mandatory
    for keyword in OBLIGATION_KEYWORDS["Mandatory"]:
        if keyword in req_lower:
            return "Mandatory"
    
    # Priority 4: Recommended
    for keyword in OBLIGATION_KEYWORDS["Recommended"]:
        if keyword in req_lower:
            return "Recommended"
    
    # Priority 5: Conditional (fallback for conditional keywords anywhere)
    for keyword in OBLIGATION_KEYWORDS["Conditional"]:
        if keyword in req_lower:
            return "Conditional"
    
    # Default: Use existing or Informational
    return existing_type if existing_type else "Informational"


def generate_requirement_id(source_file: str, chunk_id: int, requirement: str) -> str:
    """
    Generate unique requirement ID
    Format: REQ_<SOURCE_PREFIX>_<CHUNK>_<HASH>
    """
    
    # Extract source prefix (first 8 chars of filename without extension)
    source_prefix = source_file.replace(".pdf", "")[:8].upper()
    
    # Generate short hash of requirement text
    text_hash = hashlib.md5(requirement.encode('utf-8')).hexdigest()[:6].upper()
    
    req_id = f"REQ_{source_prefix}_{chunk_id:04d}_{text_hash}"
    
    return req_id


# ============================================================
# MAIN PROCESSING
# ============================================================

def build_taxonomy(input_file: str, output_file: str):
    """
    Main function to build taxonomy from requirements
    """
    
    print("=" * 80)
    print("TAXONOMY BUILDER - PHASE 7 MODULE 1")
    print("=" * 80)
    
    # Load input
    print(f"\nLoading: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        requirements = json.load(f)
    
    print(f"Loaded: {len(requirements)} requirements")
    
    # Process each requirement
    print("\nProcessing requirements...")
    
    taxonomy_data = []
    
    domain_stats = {}
    obligation_stats = {}
    status_stats = {}
    
    for idx, req in enumerate(requirements, 1):
        
        # Extract fields
        source_file = req.get("source_file", "unknown.pdf")
        chunk_id = req.get("chunk_id", 0)
        requirement_text = req.get("requirement", "")
        existing_obligation = req.get("obligation_type", "")
        deadline = req.get("deadline", "")
        entity = req.get("entity", "")
        
        # Generate requirement ID
        requirement_id = generate_requirement_id(source_file, chunk_id, requirement_text)
        
        # Classify domain and subdomain
        domain, subdomain = classify_domain(requirement_text)
        
        # Classify obligation type
        obligation_type = classify_obligation_type(requirement_text, existing_obligation)
        
        # Determine effective status
        effective_status = extract_effective_status(requirement_text, source_file, deadline)
        
        # Build taxonomy entry
        taxonomy_entry = {
            "requirement_id": requirement_id,
            "domain": domain,
            "subdomain": subdomain,
            "obligation_type": obligation_type,
            "source_document": source_file,
            "effective_status": effective_status,
            "requirement_text": requirement_text,
            "entity": entity,
            "deadline": deadline,
            "chunk_id": chunk_id
        }
        
        taxonomy_data.append(taxonomy_entry)
        
        # Update stats
        domain_stats[domain] = domain_stats.get(domain, 0) + 1
        obligation_stats[obligation_type] = obligation_stats.get(obligation_type, 0) + 1
        status_stats[effective_status] = status_stats.get(effective_status, 0) + 1
        
        # Progress indicator
        if idx % 500 == 0:
            print(f"  Processed: {idx}/{len(requirements)}")
    
    # Save output
    print(f"\nSaving: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("\n" + "=" * 80)
    print("TAXONOMY STATISTICS")
    print("=" * 80)
    
    print(f"\nTotal Requirements: {len(taxonomy_data)}")
    
    print("\nDOMAIN DISTRIBUTION")
    print("-" * 80)
    for domain, count in sorted(domain_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(taxonomy_data)) * 100
        print(f"  {domain:20s} : {count:4d} ({percentage:5.1f}%)")
    
    print("\nOBLIGATION TYPE DISTRIBUTION")
    print("-" * 80)
    for obligation, count in sorted(obligation_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(taxonomy_data)) * 100
        print(f"  {obligation:20s} : {count:4d} ({percentage:5.1f}%)")
    
    print("\nEFFECTIVE STATUS DISTRIBUTION")
    print("-" * 80)
    for status, count in sorted(status_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(taxonomy_data)) * 100
        print(f"  {status:20s} : {count:4d} ({percentage:5.1f}%)")
    
    print("\n" + "=" * 80)
    print("TAXONOMY BUILD COMPLETE")
    print("=" * 80)
    print(f"\nOutput: {output_file}")
    print(f"Records: {len(taxonomy_data)}")
    
    return taxonomy_data


# ============================================================
# SAMPLE OUTPUT GENERATOR
# ============================================================

def generate_sample_output(taxonomy_data: List[Dict], sample_size: int = 10):
    """
    Print sample output for verification
    """
    
    print("\n" + "=" * 80)
    print("SAMPLE OUTPUT")
    print("=" * 80)
    
    # Show diverse samples
    samples = {
        "Mandatory KYC": None,
        "Mandatory AML": None,
        "Recommended Cybersecurity": None,
        "Mandatory Record Retention": None,
        "Mandatory Reporting": None
    }
    
    for entry in taxonomy_data:
        key = f"{entry['obligation_type']} {entry['domain']}"
        
        if key in samples and samples[key] is None:
            samples[key] = entry
    
    for idx, (label, entry) in enumerate(samples.items(), 1):
        if entry:
            print(f"\n[SAMPLE {idx}] {label}")
            print("-" * 80)
            print(f"Requirement ID    : {entry['requirement_id']}")
            print(f"Domain            : {entry['domain']}")
            print(f"Subdomain         : {entry['subdomain']}")
            print(f"Obligation Type   : {entry['obligation_type']}")
            print(f"Source Document   : {entry['source_document']}")
            print(f"Effective Status  : {entry['effective_status']}")
            print(f"Requirement Text  : {entry['requirement_text'][:200]}...")
    
    print("\n" + "=" * 80)


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    
    try:
        # Build taxonomy
        taxonomy_data = build_taxonomy(INPUT_FILE, OUTPUT_FILE)
        
        # Generate sample output
        generate_sample_output(taxonomy_data, sample_size=10)
        
        print("\n✓ Taxonomy builder executed successfully")
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: Input file not found")
        print(f"  Expected: {INPUT_FILE}")
        print(f"  {e}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
