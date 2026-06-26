#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Effective Requirement Resolver
SuRaksha Phase 7 - Module 4

Purpose: Determine the most current and relevant RBI requirement for user queries
Instead of just retrieving chunks, this answers: "What is the effective requirement?"
"""

import json
import chromadb
import sys
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

CHROMA_PATH = str(PROJECT_ROOT / "data" / "vector_db")
COLLECTION_NAME = "regintel_rbi"

TAXONOMY_FILE = str(PROJECT_ROOT / "data/requirements/requirements_taxonomy.json")
CROSS_REFERENCES_FILE = str(PROJECT_ROOT / "cross_references.json")
REFERENCE_GRAPH_FILE = str(PROJECT_ROOT / "reference_graph_v2.json")

# ============================================================
# SCORING WEIGHTS
# ============================================================

WEIGHTS = {
    "semantic_similarity": 0.40,    # Primary: How well does it match the query?
    "obligation_type": 0.20,        # Mandatory > Recommended > Informational
    "domain_match": 0.15,           # Does domain align with query intent?
    "graph_centrality": 0.10,       # Is document well-referenced?
    "effective_status": 0.10,       # Is it active vs proposed?
    "source_authority": 0.05,       # Source document authority
}

OBLIGATION_SCORES = {
    "Mandatory": 1.0,
    "Prohibited": 0.9,
    "Conditional": 0.8,
    "Recommended": 0.6,
    "Informational": 0.4,
}

DOMAIN_KEYWORDS = {
    "KYC": ["kyc", "know your customer", "customer identification", "cip", "identity", "verification"],
    "AML": ["aml", "anti money laundering", "suspicious", "transaction monitoring", "ctr", "str", "pep"],
    "Cybersecurity": ["cyber", "security", "breach", "incident", "data protection", "IT", "technology"],
    "Risk Management": ["risk", "management", "framework", "assessment", "mitigation"],
    "Record Retention": ["record", "retention", "storage", "archive", "documentation", "maintain"],
    "Reporting": ["report", "reporting", "submission", "filing", "disclosure"],
    "Governance": ["governance", "board", "policy", "compliance", "oversight"],
    "Technology": ["technology", "digital", "system", "software", "automation"],
}

# ============================================================
# RESOLVER CLASS
# ============================================================

class EffectiveRequirementResolver:
    """
    Resolves user queries to the most effective RBI requirement
    """
    
    def __init__(self):
        """Initialize resolver with all data sources"""
        
        print("Initializing Effective Requirement Resolver...")
        
        # Load taxonomy
        print(f"  Loading taxonomy from {TAXONOMY_FILE}")
        with open(TAXONOMY_FILE, 'r', encoding='utf-8') as f:
            self.taxonomy = json.load(f)
        print(f"    [OK] Loaded {len(self.taxonomy)} requirements")
        
        # Load cross-references
        print(f"  Loading cross-references from {CROSS_REFERENCES_FILE}")
        with open(CROSS_REFERENCES_FILE, 'r', encoding='utf-8') as f:
            self.cross_refs = json.load(f)
        print(f"    [OK] Loaded {len(self.cross_refs.get('references', []))} cross-references")
        
        # Load reference graph
        print(f"  Loading reference graph from {REFERENCE_GRAPH_FILE}")
        with open(REFERENCE_GRAPH_FILE, 'r', encoding='utf-8') as f:
            self.graph = json.load(f)
        print(f"    [OK] Loaded graph with {self.graph['metadata']['total_nodes']} nodes")
        
        # Initialize ChromaDB
        print(f"  Connecting to ChromaDB at {CHROMA_PATH}")
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
        print(f"    [OK] Connected to collection '{COLLECTION_NAME}'")
        
        # Build lookup indexes
        self._build_indexes()
        
        print("[OK] Resolver initialized successfully\n")
    
    def _build_indexes(self):
        """Build fast lookup indexes"""
        
        print("  Building indexes...")
        
        # Requirement ID → full requirement
        self.req_by_id = {r['requirement_id']: r for r in self.taxonomy}
        
        # Source document → requirements
        self.reqs_by_doc = defaultdict(list)
        for req in self.taxonomy:
            self.reqs_by_doc[req['source_document']].append(req)
        
        # Domain → requirements
        self.reqs_by_domain = defaultdict(list)
        for req in self.taxonomy:
            self.reqs_by_domain[req['domain']].append(req)
        
        # Build document centrality scores from graph
        self.doc_centrality = {}
        if 'statistics' in self.graph:
            out_degree = self.graph['statistics']['degree_centrality']['out_degree']
            max_degree = max(out_degree.values()) if out_degree else 1
            
            for doc, degree in out_degree.items():
                self.doc_centrality[doc] = degree / max_degree if max_degree > 0 else 0
        
        print(f"    [OK] Indexed {len(self.req_by_id)} requirements")
        print(f"    [OK] Indexed {len(self.reqs_by_doc)} source documents")
        print(f"    [OK] Indexed {len(self.doc_centrality)} document centrality scores")
    
    def detect_domain(self, query: str) -> str:
        """Detect primary domain from query"""
        
        query_lower = query.lower()
        domain_scores = {}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return "General"
    
    def retrieve_candidates(self, query: str, top_k: int = 20) -> List[Dict]:
        """Retrieve candidate requirements using semantic search"""
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        candidates = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                chunk_id = results['ids'][0][i]
                distance = results['distances'][0][i]
                metadata = results['metadatas'][0][i]
                text = results['documents'][0][i]
                
                # Convert distance to similarity (lower distance = higher similarity)
                # Assuming cosine distance: similarity = 1 - distance
                similarity = 1.0 - distance
                
                candidates.append({
                    "chunk_id": chunk_id,
                    "similarity": similarity,
                    "source_document": metadata.get('source_file', ''),
                    "text": text,
                    "metadata": metadata
                })
        
        return candidates
    
    def score_requirement(self, req: Dict, query: str, similarity: float, 
                         detected_domain: str) -> Tuple[float, Dict]:
        """Calculate comprehensive score for a requirement"""
        
        scores = {}
        
        # 1. Semantic similarity (from vector search)
        scores['semantic_similarity'] = similarity
        
        # 2. Obligation type score
        obligation_type = req.get('obligation_type', 'Informational')
        scores['obligation_type'] = OBLIGATION_SCORES.get(obligation_type, 0.4)
        
        # 3. Domain match score
        req_domain = req.get('domain', 'General')
        if req_domain == detected_domain:
            scores['domain_match'] = 1.0
        elif req_domain in ["General", "Governance"]:
            scores['domain_match'] = 0.5  # General rules apply broadly
        else:
            scores['domain_match'] = 0.2
        
        # 4. Graph centrality (how well-referenced is source doc)
        source_doc = req.get('source_document', '')
        scores['graph_centrality'] = self.doc_centrality.get(source_doc, 0.0)
        
        # 5. Effective status
        effective_status = req.get('effective_status', 'Active')
        scores['effective_status'] = 1.0 if effective_status == 'Active' else 0.3
        
        # 6. Source authority (placeholder - all equal for now)
        scores['source_authority'] = 1.0
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * WEIGHTS[key]
            for key in WEIGHTS.keys()
        )
        
        return total_score, scores
    
    def calculate_confidence(self, top_requirements: List[Dict], 
                            detected_domain: str) -> str:
        """Calculate confidence level for the resolution - RECALIBRATED"""
        
        if not top_requirements:
            return "Low"
        
        top_req = top_requirements[0]
        top_score = top_req['total_score']
        
        # RECALIBRATED THRESHOLDS for regulatory corpus
        # High confidence criteria (relaxed from 0.75 to 0.70)
        if (top_score >= 0.70 and
            top_req['requirement']['domain'] == detected_domain and
            top_req['requirement']['obligation_type'] in ['Mandatory', 'Prohibited']):
            return "High"
        
        # Medium confidence criteria (relaxed from 0.60 to 0.50)
        if (top_score >= 0.50 and
            top_req['similarity'] > 0.0):  # Positive semantic match
            return "Medium"
        
        return "Low"
    
    def find_related_circulars(self, source_doc: str) -> List[str]:
        """Find related circular references for a document"""
        
        related = []
        
        # Check cross-references
        ref_graph = self.cross_refs.get('reference_graph', {})
        doc_refs = ref_graph.get('by_source_document', {}).get(source_doc, [])
        
        for ref in doc_refs:
            circular = ref.get('referenced_circular', '')
            if circular and circular not in related:
                related.append(circular)
        
        return related
    
    def resolve(self, query: str, top_k: int = 5) -> Dict:
        """
        Main resolution method: Find the most effective requirement for a query
        
        Args:
            query: User's compliance query
            top_k: Number of top requirements to return
        
        Returns:
            Dictionary with effective requirement and supporting evidence
        """
        
        print(f"\n{'='*80}")
        print(f"RESOLVING QUERY: {query}")
        print(f"{'='*80}\n")
        
        # Step 1: Detect domain
        detected_domain = self.detect_domain(query)
        print(f"[1] Detected Domain: {detected_domain}")
        
        # Step 2: Retrieve candidates
        print(f"\n[2] Retrieving candidates from vector database...")
        candidates = self.retrieve_candidates(query, top_k=20)
        print(f"    Retrieved {len(candidates)} candidates")
        
        # Step 3: Match candidates to taxonomy requirements
        print(f"\n[3] Matching candidates to taxonomy...")
        scored_requirements = []
        
        for candidate in candidates:
            # ChromaDB returns metadata with source_file and chunk_id
            metadata = candidate.get('metadata', {})
            source_doc = metadata.get('source_file', candidate.get('source_document', ''))
            chunk_id_str = metadata.get('chunk_id', candidate.get('chunk_id', '0'))
            
            # Convert chunk_id to int
            try:
                chunk_num = int(chunk_id_str)
            except:
                continue
            
            # Find requirements from this document/chunk
            doc_reqs = self.reqs_by_doc.get(source_doc, [])
            
            for req in doc_reqs:
                if req.get('chunk_id') == chunk_num:
                    # Score this requirement
                    total_score, score_breakdown = self.score_requirement(
                        req, query, candidate['similarity'], detected_domain
                    )
                    
                    scored_requirements.append({
                        'requirement': req,
                        'similarity': candidate['similarity'],
                        'total_score': total_score,
                        'score_breakdown': score_breakdown,
                        'chunk_text': candidate['text']
                    })
        
        print(f"    Matched {len(scored_requirements)} requirements")
        
        # Step 4: Sort by total score
        scored_requirements.sort(key=lambda x: x['total_score'], reverse=True)
        top_requirements = scored_requirements[:top_k]
        
        # Step 5: Calculate confidence
        confidence = self.calculate_confidence(top_requirements, detected_domain)
        
        # Step 6: Build result
        if not top_requirements:
            return {
                'query': query,
                'detected_domain': detected_domain,
                'confidence': 'Low',
                'effective_requirement': None,
                'supporting_requirements': [],
                'message': 'No matching requirements found'
            }
        
        effective_req = top_requirements[0]
        
        # Find related circulars
        related_circulars = self.find_related_circulars(
            effective_req['requirement']['source_document']
        )
        
        result = {
            'query': query,
            'detected_domain': detected_domain,
            'confidence': confidence,
            'effective_requirement': {
                'requirement_id': effective_req['requirement']['requirement_id'],
                'requirement_text': effective_req['requirement']['requirement_text'],
                'obligation_type': effective_req['requirement']['obligation_type'],
                'domain': effective_req['requirement']['domain'],
                'subdomain': effective_req['requirement']['subdomain'],
                'source_document': effective_req['requirement']['source_document'],
                'effective_status': effective_req['requirement']['effective_status'],
                'entity': effective_req['requirement'].get('entity', ''),
                'deadline': effective_req['requirement'].get('deadline', ''),
                'total_score': round(effective_req['total_score'], 4),
                'similarity': round(effective_req['similarity'], 4),
                'score_breakdown': {k: round(v, 4) for k, v in effective_req['score_breakdown'].items()}
            },
            'supporting_requirements': [
                {
                    'requirement_id': req['requirement']['requirement_id'],
                    'requirement_text': req['requirement']['requirement_text'][:200] + '...',
                    'obligation_type': req['requirement']['obligation_type'],
                    'domain': req['requirement']['domain'],
                    'source_document': req['requirement']['source_document'],
                    'total_score': round(req['total_score'], 4),
                    'similarity': round(req['similarity'], 4)
                }
                for req in top_requirements[1:top_k]
            ],
            'related_circulars': related_circulars[:5],
            'graph_metadata': {
                'document_centrality': self.doc_centrality.get(
                    effective_req['requirement']['source_document'], 0.0
                ),
                'total_candidates': len(candidates),
                'matched_requirements': len(scored_requirements)
            }
        }
        
        return result
    
    def format_result(self, result: Dict) -> str:
        """Format result as readable text"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("EFFECTIVE REQUIREMENT RESOLUTION")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"Query: {result['query']}")
        lines.append(f"Detected Domain: {result['detected_domain']}")
        lines.append(f"Confidence: {result['confidence']}")
        lines.append("")
        
        if not result['effective_requirement']:
            lines.append("No matching requirements found.")
            return "\n".join(lines)
        
        eff = result['effective_requirement']
        
        lines.append("-" * 80)
        lines.append("CURRENT EFFECTIVE REQUIREMENT")
        lines.append("-" * 80)
        lines.append("")
        lines.append(f"Requirement ID: {eff['requirement_id']}")
        lines.append(f"Obligation Type: {eff['obligation_type']}")
        lines.append(f"Domain: {eff['domain']} / {eff['subdomain']}")
        lines.append(f"Status: {eff['effective_status']}")
        lines.append(f"Source Document: {eff['source_document']}")
        lines.append(f"Entity: {eff['entity']}")
        if eff['deadline']:
            lines.append(f"Deadline: {eff['deadline']}")
        lines.append("")
        lines.append(f"Requirement Text:")
        lines.append(f"  {eff['requirement_text']}")
        lines.append("")
        lines.append(f"Confidence Metrics:")
        lines.append(f"  Total Score: {eff['total_score']:.4f}")
        lines.append(f"  Semantic Similarity: {eff['similarity']:.4f}")
        lines.append("")
        lines.append(f"Score Breakdown:")
        for key, value in eff['score_breakdown'].items():
            weight = WEIGHTS.get(key, 0)
            lines.append(f"  {key:25s} : {value:.4f} (weight: {weight:.2f})")
        lines.append("")
        
        if result['supporting_requirements']:
            lines.append("-" * 80)
            lines.append("SUPPORTING REQUIREMENTS (Top 4)")
            lines.append("-" * 80)
            lines.append("")
            
            for i, req in enumerate(result['supporting_requirements'], 2):
                lines.append(f"{i}. {req['requirement_id']}")
                lines.append(f"   Domain: {req['domain']}")
                lines.append(f"   Obligation: {req['obligation_type']}")
                lines.append(f"   Score: {req['total_score']:.4f} | Similarity: {req['similarity']:.4f}")
                lines.append(f"   Text: {req['requirement_text']}")
                lines.append("")
        
        if result['related_circulars']:
            lines.append("-" * 80)
            lines.append("RELATED CIRCULAR REFERENCES")
            lines.append("-" * 80)
            lines.append("")
            for circular in result['related_circulars']:
                lines.append(f"  • {circular}")
            lines.append("")
        
        lines.append("-" * 80)
        lines.append("GRAPH METADATA")
        lines.append("-" * 80)
        lines.append("")
        meta = result['graph_metadata']
        lines.append(f"Document Centrality: {meta['document_centrality']:.4f}")
        lines.append(f"Total Candidates Retrieved: {meta['total_candidates']}")
        lines.append(f"Requirements Matched: {meta['matched_requirements']}")
        lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF RESOLUTION")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """Main execution"""
    
    print("=" * 80)
    print("EFFECTIVE REQUIREMENT RESOLVER - PHASE 7 MODULE 4")
    print("=" * 80)
    print()
    
    # Initialize resolver
    resolver = EffectiveRequirementResolver()
    
    # Sample queries
    queries = [
        "What are the record retention requirements for KYC documents?",
        "What is required for beneficial ownership identification?",
        "What are the CTR reporting requirements?",
    ]
    
    for query in queries:
        result = resolver.resolve(query)
        print(resolver.format_result(result))
        print("\n")


if __name__ == "__main__":
    main()
