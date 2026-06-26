import json
import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

INPUT_TAXONOMY = str(PROJECT_ROOT / "data/requirements/requirements_taxonomy.json")
INPUT_CHUNKS = str(PROJECT_ROOT / "data" / "chunks")
OUTPUT_FILE = str(PROJECT_ROOT / "cross_references.json")

# ============================================================
# CROSS-REFERENCE PATTERNS
# ============================================================

# Pattern for circular references - ENHANCED to catch department-prefixed formats
CIRCULAR_PATTERN = r'(?:DNBS\.?\(PD\)\.?(?:CC\.?)?No\.?\s*\d+|DBOD\.?(?:AML\.?)?(?:BC\.?)?No\.?\s*\d+|DBR\.?(?:BP\.?)?(?:BC\.?)?No\.?\s*\d+|RPCD\.?CO\.?(?:RF\.?)?(?:BC\.?)?No\.?\s*\d+|(?:DNBS|RBI|DOR|DBR|FMRD|FSD|FIDD|CO|DOS)\s*\([^)]+\)\s*(?:CC|No\.|Circular)\s*(?:No\.?)?\s*[\w/\.-]+)'

# Pattern for dates (multiple formats)
DATE_PATTERNS = [
    r'dated\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',  # dated February 21, 2005
    r'dated\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',     # dated 21 February 2005
    r'dated\s+(\d{2}/\d{2}/\d{4})',               # dated 21/02/2005
    r'dated\s+(\d{2}\.\d{2}\.\d{4})',             # dated 21.02.2005
]

# Relationship keywords
RELATIONSHIP_KEYWORDS = {
    'supersedes': [
        'supersede', 'supersedes', 'superseded by', 'replaces', 'replaced by',
        'in supersession', 'in place of', 'withdraws', 'withdrawn',
        'no longer applicable', 'stands withdrawn', 'hereby withdrawn'
    ],
    'amends': [
        'amend', 'amends', 'amended by', 'modifies', 'modified by',
        'revises', 'revised by', 'updates?', 'updated by',
        'changes', 'changed by'
    ],
    'modifies': [
        'modifies', 'modified', 'modifying', 'modification to',
        'alters', 'altered', 'varying', 'variation to'
    ],
    'replaces': [
        'replaces', 'replaced', 'replacing', 'in replacement of',
        'substitutes', 'substituted', 'instead of'
    ],
    'clarifies': [
        'clarifies', 'clarified', 'clarifying', 'clarification',
        'explains', 'explained', 'interpretation of',
        'in clarification', 'for clarity'
    ],
    'extends': [
        'extends', 'extended', 'extension of', 'extends the deadline',
        'extends the period', 'extended till'
    ],
    'consolidates': [
        'consolidates', 'consolidated', 'consolidation of',
        'master circular', 'consolidated circular'
    ],
    'refers_to': [
        'refers to', 'reference to', 'as per', 'in terms of',
        'pursuant to', 'in accordance with', 'as mentioned in',
        'vide', 'details are in'
    ]
}

# Document number patterns - ENHANCED
DOC_NUMBER_PATTERNS = [
    r'DNBS\.?\(PD\)\.?CC\.?No\.?\s*\d+',  # DNBS(PD).CC.No209
    r'DBOD\.?(?:AML\.?)?(?:BC\.?)?No\.?\s*\d+',  # DBOD.AML.BC.No.95
    r'DBR\.?(?:BP\.?)?(?:BC\.?)?No\.?\s*\d+',  # DBR.BP.BC.No.42
    r'RPCD\.?CO\.?(?:RF\.?)?(?:BC\.?)?No\.?\s*\d+',  # RPCD.CO.RF.BC.No.12
    r'(?:RBI|DNBS|DOR|DBR)/\d{4}-\d{2,4}/\d+',  # RBI/2011-12/25
    r'(?:circular|notification|directive)\s+(?:no\.?|number)?\s*[A-Z]*\d+',  # Circular No. 123
    r'(?:CC|Circular)\s+No\.?\s*\d+',  # CC No. 48
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    return re.sub(r'\s+', ' ', text).strip()


def extract_circular_references(text: str) -> List[str]:
    """Extract circular/notification references from text"""
    
    text = normalize_text(text)
    references = []
    
    # Find circular patterns
    matches = re.finditer(CIRCULAR_PATTERN, text, re.IGNORECASE)
    for match in matches:
        ref = match.group(0).strip()
        references.append(ref)
    
    # Find document numbers
    for pattern in DOC_NUMBER_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            ref = match.group(0).strip()
            if ref not in references:
                references.append(ref)
    
    return references


def extract_dates(text: str) -> List[str]:
    """Extract dates from text"""
    
    dates = []
    
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1).strip()
            dates.append(date_str)
    
    return dates


def detect_relationship_type(text: str) -> List[str]:
    """Detect relationship type from text"""
    
    text_lower = text.lower()
    detected_relationships = []
    
    for rel_type, keywords in RELATIONSHIP_KEYWORDS.items():
        for keyword in keywords:
            # Use word boundary for more precise matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                if rel_type not in detected_relationships:
                    detected_relationships.append(rel_type)
                break  # Found one keyword for this relationship type
    
    return detected_relationships


def extract_context_window(text: str, reference: str, window_size: int = 200) -> str:
    """Extract context around a reference"""
    
    # Find position of reference
    text_lower = text.lower()
    ref_lower = reference.lower()
    
    pos = text_lower.find(ref_lower)
    
    if pos == -1:
        return text[:window_size]
    
    # Get context before and after
    start = max(0, pos - window_size // 2)
    end = min(len(text), pos + len(reference) + window_size // 2)
    
    context = text[start:end].strip()
    
    return context


def clean_reference(ref: str) -> str:
    """Clean and standardize reference"""
    
    # Remove extra spaces
    ref = re.sub(r'\s+', ' ', ref)
    
    # Remove trailing punctuation
    ref = ref.rstrip('.,;:')
    
    return ref.strip()


# ============================================================
# MAIN PROCESSING FUNCTIONS
# ============================================================

def parse_requirement_references(requirement: Dict) -> List[Dict]:
    """Parse references from a single requirement"""
    
    text = requirement.get('requirement_text', '')
    
    if not text or len(text) < 20:
        return []
    
    # Extract circular references
    circular_refs = extract_circular_references(text)
    
    if not circular_refs:
        return []
    
    # Detect relationship types
    relationships = detect_relationship_type(text)
    
    # Default to 'refers_to' if no specific relationship found
    if not relationships:
        relationships = ['refers_to']
    
    # Extract dates
    dates = extract_dates(text)
    
    # Build reference objects
    references = []
    
    for ref in circular_refs:
        
        ref_cleaned = clean_reference(ref)
        
        # Get context around reference
        context = extract_context_window(text, ref, window_size=150)
        
        ref_obj = {
            'source_requirement_id': requirement['requirement_id'],
            'source_document': requirement['source_document'],
            'referenced_circular': ref_cleaned,
            'relationship_types': relationships,
            'context': context,
            'dates_mentioned': dates,
            'domain': requirement.get('domain', 'Unknown'),
            'chunk_id': requirement.get('chunk_id', 0)
        }
        
        references.append(ref_obj)
    
    return references


def parse_chunk_references(chunk: Dict) -> List[Dict]:
    """Parse references from a chunk (for more context)"""
    
    text = chunk.get('text', '')
    source_file = chunk.get('source_file', 'Unknown')
    chunk_id = chunk.get('chunk_id', 0)
    
    if not text or len(text) < 50:
        return []
    
    # Extract circular references
    circular_refs = extract_circular_references(text)
    
    if not circular_refs:
        return []
    
    # Detect relationship types
    relationships = detect_relationship_type(text)
    
    if not relationships:
        relationships = ['refers_to']
    
    # Extract dates
    dates = extract_dates(text)
    
    # Build reference objects
    references = []
    
    for ref in circular_refs:
        
        ref_cleaned = clean_reference(ref)
        
        # Get context
        context = extract_context_window(text, ref, window_size=200)
        
        ref_obj = {
            'source_document': source_file,
            'source_chunk_id': chunk_id,
            'referenced_circular': ref_cleaned,
            'relationship_types': relationships,
            'context': context,
            'dates_mentioned': dates
        }
        
        references.append(ref_obj)
    
    return references


def build_reference_graph(all_references: List[Dict]) -> Dict:
    """Build a graph of document relationships"""
    
    # Group by source document
    by_source = defaultdict(list)
    
    for ref in all_references:
        source = ref.get('source_document', ref.get('source_requirement_id', 'Unknown'))
        by_source[source].append(ref)
    
    # Group by referenced circular
    by_target = defaultdict(list)
    
    for ref in all_references:
        target = ref['referenced_circular']
        by_target[target].append(ref)
    
    # Group by relationship type
    by_relationship = defaultdict(list)
    
    for ref in all_references:
        for rel_type in ref['relationship_types']:
            by_relationship[rel_type].append(ref)
    
    return {
        'by_source_document': dict(by_source),
        'by_referenced_circular': dict(by_target),
        'by_relationship_type': dict(by_relationship)
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    
    print("=" * 80)
    print("CROSS-REFERENCE PARSER - PHASE 7 MODULE 2")
    print("=" * 80)
    
    # Load taxonomy data
    print(f"\n[1] Loading taxonomy data...")
    
    with open(INPUT_TAXONOMY, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
    
    print(f"    Loaded: {len(taxonomy)} requirements")
    
    # Parse references from requirements
    print("\n[2] Parsing references from requirements...")
    
    all_references = []
    
    for idx, req in enumerate(taxonomy, 1):
        refs = parse_requirement_references(req)
        all_references.extend(refs)
        
        if idx % 500 == 0:
            print(f"    Processed: {idx}/{len(taxonomy)}")
    
    print(f"    Found: {len(all_references)} references from requirements")
    
    # Parse references from chunks (for additional context)
    print("\n[3] Parsing references from chunks...")
    
    import os
    
    chunk_references = []
    chunk_count = 0
    
    if os.path.exists(INPUT_CHUNKS):
        for filename in os.listdir(INPUT_CHUNKS):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(INPUT_CHUNKS, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            for chunk in chunks:
                refs = parse_chunk_references(chunk)
                chunk_references.extend(refs)
                chunk_count += 1
    
    print(f"    Processed: {chunk_count} chunks")
    print(f"    Found: {len(chunk_references)} additional references")
    
    # Combine and deduplicate
    print("\n[4] Building reference graph...")
    
    # Use requirement references as primary (they have more metadata)
    combined_references = all_references
    
    # Build graph
    reference_graph = build_reference_graph(combined_references)
    
    # Calculate statistics
    unique_sources = len(reference_graph['by_source_document'])
    unique_targets = len(reference_graph['by_referenced_circular'])
    
    relationship_stats = {
        rel_type: len(refs)
        for rel_type, refs in reference_graph['by_relationship_type'].items()
    }
    
    # Build output
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_references': len(combined_references),
            'unique_source_documents': unique_sources,
            'unique_referenced_circulars': unique_targets,
            'relationship_types_found': list(relationship_stats.keys())
        },
        'statistics': {
            'by_relationship_type': relationship_stats,
            'top_referenced_circulars': get_top_n_items(
                reference_graph['by_referenced_circular'], 
                n=20
            ),
            'top_source_documents': get_top_n_items(
                reference_graph['by_source_document'], 
                n=20
            )
        },
        'references': combined_references,
        'reference_graph': {
            'by_source_document': reference_graph['by_source_document'],
            'by_referenced_circular': reference_graph['by_referenced_circular'],
            'by_relationship_type': reference_graph['by_relationship_type']
        }
    }
    
    # Save output
    print(f"\n[5] Saving results...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"    Saved: {OUTPUT_FILE}")
    
    # Print statistics
    print("\n" + "=" * 80)
    print("CROSS-REFERENCE STATISTICS")
    print("=" * 80)
    
    print(f"\nTotal References Found      : {len(combined_references)}")
    print(f"Unique Source Documents     : {unique_sources}")
    print(f"Unique Referenced Circulars : {unique_targets}")
    
    print("\nRELATIONSHIP TYPE DISTRIBUTION")
    print("-" * 80)
    for rel_type, count in sorted(relationship_stats.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(combined_references)) * 100 if combined_references else 0
        print(f"  {rel_type:20s} : {count:4d} ({pct:5.1f}%)")
    
    print("\nTOP 10 MOST REFERENCED CIRCULARS")
    print("-" * 80)
    top_circulars = get_top_n_items(reference_graph['by_referenced_circular'], n=10)
    for circular, count in top_circulars:
        print(f"  {count:3d} references → {circular}")
    
    print("\nTOP 10 DOCUMENTS WITH MOST REFERENCES")
    print("-" * 80)
    top_sources = get_top_n_items(reference_graph['by_source_document'], n=10)
    for source, count in top_sources:
        print(f"  {count:3d} references → {source}")
    
    print("\n" + "=" * 80)
    print("CROSS-REFERENCE PARSING COMPLETE")
    print("=" * 80)
    print(f"\nOutput: {OUTPUT_FILE}")
    
    # Sample references
    print("\n" + "=" * 80)
    print("SAMPLE REFERENCES")
    print("=" * 80)
    
    sample_count = min(5, len(combined_references))
    
    for i, ref in enumerate(combined_references[:sample_count], 1):
        print(f"\n[SAMPLE {i}]")
        print("-" * 80)
        print(f"Source: {ref.get('source_document', ref.get('source_requirement_id', 'Unknown'))}")
        print(f"Referenced: {ref['referenced_circular']}")
        print(f"Relationship: {', '.join(ref['relationship_types'])}")
        print(f"Domain: {ref.get('domain', 'N/A')}")
        print(f"Context: {ref['context'][:150]}...")
    
    print("\n" + "=" * 80)
    print("✓ Cross-reference parser executed successfully")
    print("=" * 80)


def get_top_n_items(data_dict: Dict[str, List], n: int = 10) -> List[Tuple[str, int]]:
    """Get top N items by count"""
    
    counts = [(key, len(value)) for key, value in data_dict.items()]
    counts.sort(key=lambda x: x[1], reverse=True)
    
    return counts[:n]


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    
    try:
        main()
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: Input file not found")
        print(f"  {e}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
