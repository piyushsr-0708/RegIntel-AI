import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = str(PROJECT_ROOT / "cross_references.json")
OUTPUT_GRAPH_JSON = str(PROJECT_ROOT / "reference_graph.json")
OUTPUT_SUMMARY_TXT = str(PROJECT_ROOT / "graph_summary.txt")
OUTPUT_DOT = str(PROJECT_ROOT / "reference_graph.dot")
OUTPUT_PNG = str(PROJECT_ROOT / "reference_graph.png")

# ============================================================
# NOISE PATTERNS (to exclude)
# ============================================================

NOISE_PATTERNS = [
    r'^notification\s+\d{1,2}$',  # "notification 2"
    r'^DNBS\(PD\)CC\.No$',        # "DNBS(PD)CC.No" without number
    r'^circular$',                 # Just "circular"
    r'^CC$',                       # Just "CC"
    r'^notification$',             # Just "notification"
    r'^RBI$',                      # Just "RBI"
]

# ============================================================
# NORMALIZATION RULES
# ============================================================

def normalize_reference(ref: str) -> str:
    """
    Normalize reference names for consistency
    Handles:
    - "CC No 231" vs "Circular No 231"
    - "Notification No.13" vs "Notification No 13"
    - Case insensitivity
    """
    
    # Convert to lowercase for comparison
    ref_lower = ref.lower().strip()
    
    # Remove extra spaces
    ref_normalized = re.sub(r'\s+', ' ', ref_lower)
    
    # Remove trailing/leading punctuation
    ref_normalized = ref_normalized.strip('.,;:')
    
    # Normalize "No." to "No " (preserve space)
    ref_normalized = ref_normalized.replace('no.', 'no ')
    
    # Normalize "Circular No X" to "CC No X"
    ref_normalized = re.sub(r'^circular\s+no\s+(\d+)', r'cc no \1', ref_normalized)
    
    # Normalize spacing around numbers
    ref_normalized = re.sub(r'\s+', ' ', ref_normalized)
    
    return ref_normalized.strip()


def is_noise(ref: str) -> bool:
    """Check if reference is noise and should be excluded"""
    
    ref_lower = ref.lower().strip()
    
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, ref_lower, re.IGNORECASE):
            return True
    
    # Check for very short references (likely incomplete)
    if len(ref_lower) < 4:
        return True
    
    return False


def create_clean_label(ref: str) -> str:
    """Create a clean display label for the reference"""
    
    # Keep original case for display
    ref_clean = re.sub(r'\s+', ' ', ref).strip()
    
    # Capitalize first letter of each word
    words = ref_clean.split()
    if words:
        # Don't capitalize small words in the middle
        words = [
            word.capitalize() if i == 0 or len(word) > 2 else word
            for i, word in enumerate(words)
        ]
    
    return ' '.join(words)


# ============================================================
# GRAPH BUILDER
# ============================================================

class RegulatoryGraph:
    """Build and manage regulatory knowledge graph"""
    
    def __init__(self):
        self.nodes = {}  # node_id -> node_data
        self.edges = []  # list of edges
        self.node_types = defaultdict(int)
        self.edge_types = defaultdict(int)
        self.normalization_map = {}  # original -> normalized
    
    def add_node(self, node_id: str, node_type: str) -> str:
        """Add a node to the graph, return normalized ID"""
        
        if node_type == "REGULATORY_REFERENCE":
            # Normalize reference names
            normalized_id = normalize_reference(node_id)
            
            # Store mapping
            self.normalization_map[node_id] = normalized_id
            
            # Check if noise
            if is_noise(normalized_id):
                return None
            
            node_id = normalized_id
        
        # Add or update node
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "display_label": create_clean_label(node_id) if node_type == "REGULATORY_REFERENCE" else node_id
            }
            self.node_types[node_type] += 1
        
        return node_id
    
    def add_edge(self, source: str, target: str, relationship_type: str, 
                 domain: str, requirement_id: str, chunk_id: int):
        """Add an edge to the graph"""
        
        # Normalize target if it's a reference
        if target in self.normalization_map:
            target = self.normalization_map[target]
        
        # Skip if target was filtered as noise
        if target is None or target not in self.nodes:
            return
        
        # Skip if source doesn't exist
        if source not in self.nodes:
            return
        
        edge = {
            "source": source,
            "target": target,
            "relationship_type": relationship_type,
            "domain": domain,
            "requirement_id": requirement_id,
            "chunk_id": chunk_id
        }
        
        self.edges.append(edge)
        self.edge_types[relationship_type] += 1
    
    def calculate_statistics(self) -> Dict:
        """Calculate graph statistics"""
        
        # Count nodes by type
        doc_nodes = [n for n in self.nodes.values() if n["type"] == "DOCUMENT"]
        ref_nodes = [n for n in self.nodes.values() if n["type"] == "REGULATORY_REFERENCE"]
        
        # Calculate degree (connections per node)
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        for edge in self.edges:
            out_degree[edge["source"]] += 1
            in_degree[edge["target"]] += 1
        
        # Find most referenced circulars
        most_referenced = sorted(
            [(node_id, in_degree[node_id]) for node_id in in_degree if in_degree[node_id] > 0],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find most connected documents
        most_connected = sorted(
            [(node_id, out_degree[node_id]) for node_id in out_degree if out_degree[node_id] > 0],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Domain distribution
        domain_counts = Counter(edge["domain"] for edge in self.edges)
        
        # Graph density (edges / possible edges)
        n = len(self.nodes)
        max_edges = n * (n - 1)  # directed graph
        density = len(self.edges) / max_edges if max_edges > 0 else 0
        
        # Average degree
        total_degree = sum(in_degree.values()) + sum(out_degree.values())
        avg_degree = total_degree / len(self.nodes) if self.nodes else 0
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "document_nodes": len(doc_nodes),
            "reference_nodes": len(ref_nodes),
            "relationship_counts": dict(self.edge_types),
            "most_referenced_circulars": most_referenced,
            "most_connected_documents": most_connected,
            "top_domains": dict(domain_counts.most_common(10)),
            "graph_density": round(density, 6),
            "average_degree": round(avg_degree, 2),
            "nodes_removed_as_noise": len(self.normalization_map) - len(ref_nodes)
        }
    
    def to_dict(self) -> Dict:
        """Export graph as dictionary"""
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_file": INPUT_FILE,
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges)
            },
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "statistics": self.calculate_statistics()
        }
    
    def to_dot(self) -> str:
        """Export graph as Graphviz DOT format"""
        
        lines = []
        lines.append("digraph RegulatoryKnowledgeGraph {")
        lines.append("  rankdir=LR;")
        lines.append("  node [fontname=\"Arial\"];")
        lines.append("  edge [fontname=\"Arial\", fontsize=10];")
        lines.append("")
        
        # Add nodes
        lines.append("  // Document Nodes")
        for node_id, node_data in self.nodes.items():
            if node_data["type"] == "DOCUMENT":
                label = node_id.replace(".pdf", "")
                lines.append(f'  "{node_id}" [shape=box, style=filled, fillcolor=lightblue, label="{label}"];')
        
        lines.append("")
        lines.append("  // Regulatory Reference Nodes")
        for node_id, node_data in self.nodes.items():
            if node_data["type"] == "REGULATORY_REFERENCE":
                label = node_data.get("display_label", node_id)
                lines.append(f'  "{node_id}" [shape=ellipse, style=filled, fillcolor=lightgreen, label="{label}"];')
        
        lines.append("")
        lines.append("  // Edges")
        
        # Group edges by relationship type for better visualization
        edges_by_type = defaultdict(list)
        for edge in self.edges:
            edges_by_type[edge["relationship_type"]].append(edge)
        
        for rel_type in ["refers_to", "consolidates", "modifies"]:
            if rel_type in edges_by_type:
                lines.append(f"  // {rel_type} relationships")
                
                # Choose edge color
                if rel_type == "refers_to":
                    color = "gray"
                elif rel_type == "consolidates":
                    color = "blue"
                elif rel_type == "modifies":
                    color = "red"
                else:
                    color = "black"
                
                for edge in edges_by_type[rel_type]:
                    source = edge["source"]
                    target = edge["target"]
                    label = rel_type.replace("_", " ")
                    lines.append(f'  "{source}" -> "{target}" [label="{label}", color="{color}"];')
                
                lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_summary(self) -> str:
        """Generate text summary"""
        
        stats = self.calculate_statistics()
        
        lines = []
        lines.append("=" * 80)
        lines.append("REGULATORY KNOWLEDGE GRAPH SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Source: {INPUT_FILE}")
        lines.append("")
        
        lines.append("GRAPH STRUCTURE")
        lines.append("-" * 80)
        lines.append(f"Total Nodes              : {stats['total_nodes']}")
        lines.append(f"Total Edges              : {stats['total_edges']}")
        lines.append(f"Document Nodes           : {stats['document_nodes']}")
        lines.append(f"Circular Reference Nodes : {stats['reference_nodes']}")
        lines.append(f"Nodes Removed as Noise   : {stats['nodes_removed_as_noise']}")
        lines.append("")
        
        lines.append("GRAPH METRICS")
        lines.append("-" * 80)
        lines.append(f"Graph Density            : {stats['graph_density']:.6f}")
        lines.append(f"Average Degree           : {stats['average_degree']:.2f}")
        lines.append("")
        
        lines.append("RELATIONSHIP DISTRIBUTION")
        lines.append("-" * 80)
        for rel_type, count in sorted(stats['relationship_counts'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['total_edges']) * 100 if stats['total_edges'] > 0 else 0
            lines.append(f"  {rel_type:20s} : {count:3d} ({pct:5.1f}%)")
        lines.append("")
        
        lines.append("TOP 10 REFERENCED CIRCULARS")
        lines.append("-" * 80)
        for i, (circular, count) in enumerate(stats['most_referenced_circulars'][:10], 1):
            # Get display label
            display = self.nodes.get(circular, {}).get("display_label", circular)
            lines.append(f"  {i:2d}. {display:40s} : {count:3d} references")
        lines.append("")
        
        lines.append("TOP 10 CONNECTED DOCUMENTS")
        lines.append("-" * 80)
        for i, (doc, count) in enumerate(stats['most_connected_documents'][:10], 1):
            lines.append(f"  {i:2d}. {doc:40s} : {count:3d} connections")
        lines.append("")
        
        lines.append("TOP DOMAINS")
        lines.append("-" * 80)
        for domain, count in sorted(stats['top_domains'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['total_edges']) * 100 if stats['total_edges'] > 0 else 0
            lines.append(f"  {domain:20s} : {count:3d} ({pct:5.1f}%)")
        lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF SUMMARY")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# ============================================================
# MAIN FUNCTION
# ============================================================

def build_graph(input_file: str) -> RegulatoryGraph:
    """Build regulatory knowledge graph from cross-references"""
    
    print("=" * 80)
    print("REFERENCE GRAPH BUILDER - PHASE 7 MODULE 3")
    print("=" * 80)
    
    # Load input
    print(f"\n[1] Loading cross-references...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    references = data.get('references', [])
    print(f"    Loaded: {len(references)} cross-references")
    
    # Initialize graph
    print("\n[2] Building graph...")
    graph = RegulatoryGraph()
    
    # Add nodes and edges
    for ref in references:
        source_doc = ref.get('source_document')
        target_ref = ref.get('referenced_circular')
        relationship_types = ref.get('relationship_types', ['refers_to'])
        domain = ref.get('domain', 'Unknown')
        req_id = ref.get('source_requirement_id', '')
        chunk_id = ref.get('chunk_id', 0)
        
        # Add source document node
        graph.add_node(source_doc, "DOCUMENT")
        
        # Add target reference node (with normalization)
        normalized_target = graph.add_node(target_ref, "REGULATORY_REFERENCE")
        
        # Add edges for each relationship type
        for rel_type in relationship_types:
            graph.add_edge(
                source_doc,
                target_ref,  # Will be normalized in add_edge
                rel_type,
                domain,
                req_id,
                chunk_id
            )
    
    print(f"    Nodes created: {len(graph.nodes)}")
    print(f"    Edges created: {len(graph.edges)}")
    
    return graph


def export_graph(graph: RegulatoryGraph):
    """Export graph to various formats"""
    
    print("\n[3] Exporting graph...")
    
    # JSON export
    print(f"    Exporting JSON: {OUTPUT_GRAPH_JSON}")
    with open(OUTPUT_GRAPH_JSON, 'w', encoding='utf-8') as f:
        json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)
    
    # Summary text export
    print(f"    Exporting summary: {OUTPUT_SUMMARY_TXT}")
    summary = graph.generate_summary()
    with open(OUTPUT_SUMMARY_TXT, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # DOT export
    print(f"    Exporting DOT: {OUTPUT_DOT}")
    dot_content = graph.to_dot()
    with open(OUTPUT_DOT, 'w', encoding='utf-8') as f:
        f.write(dot_content)
    
    # Try PNG export if graphviz is available
    try:
        import subprocess
        print(f"    Attempting PNG export: {OUTPUT_PNG}")
        result = subprocess.run(
            ['dot', '-Tpng', OUTPUT_DOT, '-o', OUTPUT_PNG],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"    ✓ PNG exported successfully")
        else:
            print(f"    ⚠ PNG export failed (Graphviz may not be installed)")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"    ⚠ Graphviz not found - PNG export skipped")
    except Exception as e:
        print(f"    ⚠ PNG export error: {e}")


def main():
    """Main execution"""
    
    try:
        # Build graph
        graph = build_graph(INPUT_FILE)
        
        # Export
        export_graph(graph)
        
        # Print statistics
        print("\n[4] Graph statistics...")
        stats = graph.calculate_statistics()
        
        print("\n" + "=" * 80)
        print("GRAPH STATISTICS")
        print("=" * 80)
        print(f"\nTotal Nodes              : {stats['total_nodes']}")
        print(f"Total Edges              : {stats['total_edges']}")
        print(f"Document Nodes           : {stats['document_nodes']}")
        print(f"Reference Nodes          : {stats['reference_nodes']}")
        print(f"Nodes Removed as Noise   : {stats['nodes_removed_as_noise']}")
        
        print("\nRelationship Distribution:")
        for rel_type, count in sorted(stats['relationship_counts'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['total_edges']) * 100 if stats['total_edges'] > 0 else 0
            print(f"  {rel_type:20s} : {count:3d} ({pct:5.1f}%)")
        
        print("\nTop 5 Referenced Circulars:")
        for circular, count in stats['most_referenced_circulars'][:5]:
            display = graph.nodes.get(circular, {}).get("display_label", circular)
            print(f"  {count:2d} refs → {display}")
        
        print("\nTop 5 Connected Documents:")
        for doc, count in stats['most_connected_documents'][:5]:
            print(f"  {count:2d} refs → {doc}")
        
        print("\n" + "=" * 80)
        print("REFERENCE GRAPH BUILD COMPLETE")
        print("=" * 80)
        print(f"\nOutputs:")
        print(f"  - {OUTPUT_GRAPH_JSON}")
        print(f"  - {OUTPUT_SUMMARY_TXT}")
        print(f"  - {OUTPUT_DOT}")
        if OUTPUT_PNG:
            print(f"  - {OUTPUT_PNG} (if Graphviz available)")
        
        print("\n✓ Reference graph builder executed successfully")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: Input file not found")
        print(f"  {e}")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()
