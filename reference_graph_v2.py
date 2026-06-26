import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: NetworkX not installed. Installing with: pip install networkx")

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = str(PROJECT_ROOT / "cross_references.json")
OUTPUT_GRAPH_JSON = str(PROJECT_ROOT / "reference_graph_v2.json")
OUTPUT_SUMMARY_TXT = str(PROJECT_ROOT / "graph_summary_v2.txt")
OUTPUT_DOT = str(PROJECT_ROOT / "reference_graph_v2.dot")
OUTPUT_PNG = str(PROJECT_ROOT / "reference_graph_v2.png")

# ============================================================
# NOISE PATTERNS
# ============================================================

NOISE_PATTERNS = [
    r'^notification\s+\d{1,2}$',
    r'^DNBS\(PD\)CC\.No$',
    r'^circular$',
    r'^CC$',
    r'^notification$',
]

# ============================================================
# IMPROVED NORMALIZATION
# ============================================================

def normalize_reference(ref: str) -> str:
    """
    Enhanced normalization for reference names
    Handles all spacing, punctuation, and case variations
    """
    
    # Convert to lowercase
    ref_lower = ref.lower().strip()
    
    # Remove extra spaces
    ref_normalized = re.sub(r'\s+', ' ', ref_lower)
    
    # Remove trailing/leading punctuation
    ref_normalized = ref_normalized.strip('.,;:')
    
    # Normalize "No." to "no " (preserve space)
    ref_normalized = ref_normalized.replace('no.', 'no ')
    
    # Normalize "Circular No X" to "cc no X"
    ref_normalized = re.sub(r'^circular\s+no\s+(\d+)', r'cc no \1', ref_normalized)
    
    # Normalize inconsistent spacing in "CC No215" to "cc no 215"
    ref_normalized = re.sub(r'cc\s*no\s*(\d+)', r'cc no \1', ref_normalized)
    
    # Normalize inconsistent spacing in "Notification No13" to "notification no 13"
    ref_normalized = re.sub(r'notification\s*no\s*(\d+)', r'notification no \1', ref_normalized)
    
    # Final cleanup
    ref_normalized = re.sub(r'\s+', ' ', ref_normalized)
    
    return ref_normalized.strip()


def is_noise(ref: str) -> bool:
    """Check if reference is noise"""
    
    ref_lower = ref.lower().strip()
    
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, ref_lower, re.IGNORECASE):
            return True
    
    if len(ref_lower) < 4:
        return True
    
    return False


def create_display_label(ref: str) -> str:
    """Create consistent display label"""
    
    # Normalize first
    normalized = normalize_reference(ref)
    
    # Then capitalize properly for display
    words = normalized.split()
    display_words = []
    
    for i, word in enumerate(words):
        if word.lower() in ['no', 'cc', 'rbi']:
            display_words.append(word.upper() if word.lower() != 'no' else 'No')
        elif word.isdigit() or '/' in word:
            display_words.append(word)
        else:
            display_words.append(word.capitalize())
    
    return ' '.join(display_words)


# ============================================================
# NETWORKX GRAPH BUILDER
# ============================================================

class RegulatoryGraphV2:
    """Enhanced regulatory knowledge graph using NetworkX"""
    
    def __init__(self):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required. Install with: pip install networkx")
        
        self.graph = nx.MultiDiGraph()  # Allow multiple edges, then deduplicate
        self.normalization_map = {}
        self.edge_metadata = defaultdict(list)  # Track all metadata for dedupe
    
    def add_node(self, node_id: str, node_type: str) -> str:
        """Add node with normalization"""
        
        if node_type == "REGULATORY_REFERENCE":
            normalized_id = normalize_reference(node_id)
            self.normalization_map[node_id] = normalized_id
            
            if is_noise(normalized_id):
                return None
            
            node_id = normalized_id
        
        if not self.graph.has_node(node_id):
            self.graph.add_node(
                node_id,
                type=node_type,
                display_label=create_display_label(node_id) if node_type == "REGULATORY_REFERENCE" else node_id
            )
        
        return node_id
    
    def add_edge(self, source: str, target: str, relationship_type: str,
                 domain: str, requirement_id: str, chunk_id: int):
        """Add edge with deduplication support"""
        
        # Normalize target if needed
        if target in self.normalization_map:
            target = self.normalization_map[target]
        
        if target is None or not self.graph.has_node(target):
            return
        
        if not self.graph.has_node(source):
            return
        
        # Create edge key for deduplication
        edge_key = (source, target, relationship_type)
        
        # Store metadata
        metadata = {
            "relationship_type": relationship_type,
            "domain": domain,
            "requirement_id": requirement_id,
            "chunk_id": chunk_id
        }
        
        self.edge_metadata[edge_key].append(metadata)
        
        # Add edge to graph (will handle deduplication later)
        self.graph.add_edge(
            source,
            target,
            relationship_type=relationship_type,
            domain=domain,
            requirement_id=requirement_id,
            chunk_id=chunk_id
        )
    
    def deduplicate_edges(self):
        """Remove duplicate edges, keeping metadata from all instances"""
        
        # Convert to simple DiGraph (removes multi-edges, keeps last)
        simple_graph = nx.DiGraph()
        
        # Copy nodes
        for node, data in self.graph.nodes(data=True):
            simple_graph.add_node(node, **data)
        
        # Process edges - merge duplicates
        edge_data_merged = {}
        
        for source, target, data in self.graph.edges(data=True):
            edge_key = (source, target, data['relationship_type'])
            
            if edge_key not in edge_data_merged:
                # Get all metadata for this edge
                all_metadata = self.edge_metadata.get(edge_key, [data])
                
                # Merge metadata
                merged = {
                    "relationship_type": data['relationship_type'],
                    "domains": list(set(m['domain'] for m in all_metadata)),
                    "requirement_ids": list(set(m['requirement_id'] for m in all_metadata)),
                    "chunk_ids": list(set(m['chunk_id'] for m in all_metadata)),
                    "occurrence_count": len(all_metadata)
                }
                
                edge_data_merged[edge_key] = merged
        
        # Add unique edges
        for (source, target, rel_type), data in edge_data_merged.items():
            simple_graph.add_edge(source, target, **data)
        
        self.graph = simple_graph
    
    def calculate_centrality(self) -> Dict:
        """Calculate network centrality metrics"""
        
        # Degree centrality
        in_degree = dict(self.graph.in_degree())
        out_degree = dict(self.graph.out_degree())
        
        # Betweenness centrality (computationally expensive for large graphs)
        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except:
            betweenness = {}
        
        # Find most influential
        most_referenced = sorted(
            [(node, in_degree.get(node, 0)) for node in self.graph.nodes() 
             if self.graph.nodes[node]['type'] == 'REGULATORY_REFERENCE'],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        most_connected = sorted(
            [(node, out_degree.get(node, 0)) for node in self.graph.nodes()
             if self.graph.nodes[node]['type'] == 'DOCUMENT'],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        most_influential = sorted(
            betweenness.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10] if betweenness else []
        
        return {
            "degree_centrality": {
                "in_degree": in_degree,
                "out_degree": out_degree
            },
            "betweenness_centrality": betweenness,
            "most_referenced_circulars": most_referenced,
            "most_connected_documents": most_connected,
            "most_influential_nodes": most_influential
        }
    
    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive graph statistics"""
        
        # Basic counts
        doc_nodes = [n for n, d in self.graph.nodes(data=True) if d['type'] == 'DOCUMENT']
        ref_nodes = [n for n, d in self.graph.nodes(data=True) if d['type'] == 'REGULATORY_REFERENCE']
        
        # Unique edge count
        unique_edges = self.graph.number_of_edges()
        
        # Domain distribution
        domain_counts = Counter()
        for _, _, data in self.graph.edges(data=True):
            domains = data.get('domains', [data.get('domain')])
            for domain in domains:
                if domain:
                    domain_counts[domain] += 1
        
        # Relationship distribution
        rel_counts = Counter()
        for _, _, data in self.graph.edges(data=True):
            rel_counts[data['relationship_type']] += 1
        
        # Graph quality metrics
        num_nodes = self.graph.number_of_nodes()
        num_edges = unique_edges
        
        # Connected components
        if num_nodes > 0:
            weakly_connected = nx.number_weakly_connected_components(self.graph)
        else:
            weakly_connected = 0
        
        # Density
        max_edges = num_nodes * (num_nodes - 1) if num_nodes > 1 else 1
        density = num_edges / max_edges if max_edges > 0 else 0
        
        # Average degree
        if num_nodes > 0:
            total_degree = sum(dict(self.graph.in_degree()).values()) + \
                          sum(dict(self.graph.out_degree()).values())
            avg_degree = total_degree / num_nodes
        else:
            avg_degree = 0
        
        # Centrality metrics
        centrality = self.calculate_centrality()
        
        return {
            "total_nodes": num_nodes,
            "total_edges": num_edges,
            "unique_edges": unique_edges,
            "document_nodes": len(doc_nodes),
            "reference_nodes": len(ref_nodes),
            "nodes_removed_as_noise": len(self.normalization_map) - len(ref_nodes),
            "relationship_counts": dict(rel_counts),
            "top_domains": dict(domain_counts.most_common(10)),
            "graph_density": round(density, 6),
            "average_degree": round(avg_degree, 2),
            "connected_components": weakly_connected,
            **centrality
        }
    
    def to_dict(self) -> Dict:
        """Export as dictionary"""
        
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "type": data['type'],
                "display_label": data.get('display_label', node)
            })
        
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "relationship_type": data['relationship_type'],
                "domains": data.get('domains', [data.get('domain')]),
                "requirement_ids": data.get('requirement_ids', [data.get('requirement_id')]),
                "chunk_ids": data.get('chunk_ids', [data.get('chunk_id')]),
                "occurrence_count": data.get('occurrence_count', 1)
            })
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_file": INPUT_FILE,
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "version": "2.0"
            },
            "nodes": nodes,
            "edges": edges,
            "statistics": self.calculate_statistics()
        }
    
    def to_dot(self) -> str:
        """Export as DOT format"""
        
        lines = []
        lines.append("digraph RegulatoryKnowledgeGraphV2 {")
        lines.append("  rankdir=LR;")
        lines.append("  node [fontname=\"Arial\"];")
        lines.append("  edge [fontname=\"Arial\", fontsize=10];")
        lines.append("")
        
        # Document nodes
        lines.append("  // Document Nodes")
        for node, data in self.graph.nodes(data=True):
            if data['type'] == "DOCUMENT":
                label = node.replace(".pdf", "")
                lines.append(f'  "{node}" [shape=box, style=filled, fillcolor=lightblue, label="{label}"];')
        
        lines.append("")
        lines.append("  // Regulatory Reference Nodes")
        for node, data in self.graph.nodes(data=True):
            if data['type'] == "REGULATORY_REFERENCE":
                label = data.get('display_label', node)
                lines.append(f'  "{node}" [shape=ellipse, style=filled, fillcolor=lightgreen, label="{label}"];')
        
        lines.append("")
        lines.append("  // Edges (Deduplicated)")
        
        # Group by relationship type
        edges_by_type = defaultdict(list)
        for source, target, data in self.graph.edges(data=True):
            edges_by_type[data['relationship_type']].append((source, target, data))
        
        for rel_type in ["refers_to", "consolidates", "modifies"]:
            if rel_type in edges_by_type:
                lines.append(f"  // {rel_type} relationships")
                
                color = {"refers_to": "gray", "consolidates": "blue", "modifies": "red"}.get(rel_type, "black")
                
                for source, target, data in edges_by_type[rel_type]:
                    label = rel_type.replace("_", " ")
                    count = data.get('occurrence_count', 1)
                    if count > 1:
                        label = f"{label} (×{count})"
                    lines.append(f'  "{source}" -> "{target}" [label="{label}", color="{color}"];')
                
                lines.append("")
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_summary(self) -> str:
        """Generate comprehensive text summary"""
        
        stats = self.calculate_statistics()
        
        lines = []
        lines.append("=" * 80)
        lines.append("REGULATORY KNOWLEDGE GRAPH SUMMARY V2")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Version: 2.0 (NetworkX-based with deduplication)")
        lines.append("")
        
        lines.append("GRAPH STRUCTURE")
        lines.append("-" * 80)
        lines.append(f"Total Nodes              : {stats['total_nodes']}")
        lines.append(f"Total Edges (Unique)     : {stats['unique_edges']}")
        lines.append(f"Document Nodes           : {stats['document_nodes']}")
        lines.append(f"Reference Nodes          : {stats['reference_nodes']}")
        lines.append(f"Nodes Removed as Noise   : {stats['nodes_removed_as_noise']}")
        lines.append("")
        
        lines.append("GRAPH QUALITY METRICS")
        lines.append("-" * 80)
        lines.append(f"Connected Components     : {stats['connected_components']}")
        lines.append(f"Graph Density            : {stats['graph_density']:.6f}")
        lines.append(f"Average Degree           : {stats['average_degree']:.2f}")
        lines.append("")
        
        lines.append("RELATIONSHIP DISTRIBUTION")
        lines.append("-" * 80)
        for rel_type, count in sorted(stats['relationship_counts'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['unique_edges']) * 100 if stats['unique_edges'] > 0 else 0
            lines.append(f"  {rel_type:20s} : {count:3d} ({pct:5.1f}%)")
        lines.append("")
        
        lines.append("CENTRALITY ANALYSIS")
        lines.append("-" * 80)
        lines.append("\nMost Referenced Circulars (Degree Centrality):")
        for i, (node, degree) in enumerate(stats['most_referenced_circulars'][:10], 1):
            display = self.graph.nodes[node].get('display_label', node)
            lines.append(f"  {i:2d}. {display:40s} : {degree:3d} incoming")
        
        lines.append("\nMost Connected Documents (Degree Centrality):")
        for i, (node, degree) in enumerate(stats['most_connected_documents'][:10], 1):
            lines.append(f"  {i:2d}. {node:40s} : {degree:3d} outgoing")
        
        if stats.get('most_influential_nodes'):
            lines.append("\nMost Influential Nodes (Betweenness Centrality):")
            for i, (node, score) in enumerate(stats['most_influential_nodes'][:10], 1):
                display = self.graph.nodes[node].get('display_label', node)
                lines.append(f"  {i:2d}. {display:40s} : {score:.4f}")
        
        lines.append("")
        lines.append("TOP DOMAINS")
        lines.append("-" * 80)
        for domain, count in sorted(stats['top_domains'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['unique_edges']) * 100 if stats['unique_edges'] > 0 else 0
            lines.append(f"  {domain:20s} : {count:3d} ({pct:5.1f}%)")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF SUMMARY")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# ============================================================
# MAIN FUNCTION
# ============================================================

def build_graph_v2(input_file: str) -> RegulatoryGraphV2:
    """Build improved regulatory graph"""
    
    print("=" * 80)
    print("REFERENCE GRAPH BUILDER V2 - PHASE 7 MODULE 3")
    print("=" * 80)
    
    if not HAS_NETWORKX:
        print("\n✗ ERROR: NetworkX is required")
        print("Install with: pip install networkx")
        return None
    
    print(f"\n[1] Loading cross-references...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    references = data.get('references', [])
    print(f"    Loaded: {len(references)} cross-references")
    
    print("\n[2] Building NetworkX graph...")
    graph = RegulatoryGraphV2()
    
    for ref in references:
        source_doc = ref.get('source_document')
        target_ref = ref.get('referenced_circular')
        relationship_types = ref.get('relationship_types', ['refers_to'])
        domain = ref.get('domain', 'Unknown')
        req_id = ref.get('source_requirement_id', '')
        chunk_id = ref.get('chunk_id', 0)
        
        graph.add_node(source_doc, "DOCUMENT")
        normalized_target = graph.add_node(target_ref, "REGULATORY_REFERENCE")
        
        for rel_type in relationship_types:
            graph.add_edge(source_doc, target_ref, rel_type, domain, req_id, chunk_id)
    
    print(f"    Initial nodes: {graph.graph.number_of_nodes()}")
    print(f"    Initial edges: {graph.graph.number_of_edges()}")
    
    print("\n[3] Deduplicating edges...")
    graph.deduplicate_edges()
    print(f"    Unique edges: {graph.graph.number_of_edges()}")
    
    return graph


def export_graph_v2(graph: RegulatoryGraphV2):
    """Export graph to various formats"""
    
    print("\n[4] Exporting graph...")
    
    with open(OUTPUT_GRAPH_JSON, 'w', encoding='utf-8') as f:
        json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"    ✓ JSON: {OUTPUT_GRAPH_JSON}")
    
    with open(OUTPUT_SUMMARY_TXT, 'w', encoding='utf-8') as f:
        f.write(graph.generate_summary())
    print(f"    ✓ Summary: {OUTPUT_SUMMARY_TXT}")
    
    with open(OUTPUT_DOT, 'w', encoding='utf-8') as f:
        f.write(graph.to_dot())
    print(f"    ✓ DOT: {OUTPUT_DOT}")
    
    try:
        import subprocess
        result = subprocess.run(
            ['dot', '-Tpng', OUTPUT_DOT, '-o', OUTPUT_PNG],
            capture_output=True, timeout=30
        )
        if result.returncode == 0:
            print(f"    ✓ PNG: {OUTPUT_PNG}")
        else:
            print(f"    ⚠ PNG export failed")
    except:
        print(f"    ⚠ Graphviz not available - PNG skipped")


def main():
    """Main execution"""
    
    try:
        graph = build_graph_v2(INPUT_FILE)
        if graph is None:
            return
        
        export_graph_v2(graph)
        
        print("\n[5] Graph statistics...")
        stats = graph.calculate_statistics()
        
        print("\n" + "=" * 80)
        print("FINAL STATISTICS")
        print("=" * 80)
        print(f"\nNodes: {stats['total_nodes']}")
        print(f"Unique Edges: {stats['unique_edges']}")
        print(f"Connected Components: {stats['connected_components']}")
        print(f"Density: {stats['graph_density']:.6f}")
        print(f"Average Degree: {stats['average_degree']:.2f}")
        
        print("\nTop 3 Referenced:")
        for node, degree in stats['most_referenced_circulars'][:3]:
            display = graph.graph.nodes[node].get('display_label', node)
            print(f"  {degree} → {display}")
        
        print("\n" + "=" * 80)
        print("✓ Reference Graph V2 Build Complete")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
