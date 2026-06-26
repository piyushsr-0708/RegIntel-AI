"""
Test suite for Reference Graph Builder V2
Phase 7 Module 3 - Enhanced NetworkX implementation
"""

import unittest
import json
import os
from reference_graph_v2 import (

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

    RegulatoryGraphV2,
    normalize_reference,
    is_noise,
    create_display_label,
    build_graph_v2
)

class TestNormalizationV2(unittest.TestCase):
    """Test enhanced normalization"""
    
    def test_spacing_normalization(self):
        """Test spacing inconsistencies are normalized"""
        # Issue from V1: "CC No215" vs "CC No 215"
        self.assertEqual(
            normalize_reference("CC No215"),
            normalize_reference("CC No 215")
        )
        
        self.assertEqual(
            normalize_reference("CCNo215"),
            normalize_reference("CC No 215")
        )
    
    def test_case_normalization(self):
        """Test case insensitive normalization"""
        # Issue from V1: "CC No 46" vs "Cc no 46"
        self.assertEqual(
            normalize_reference("CC No 46"),
            normalize_reference("Cc no 46")
        )
        
        self.assertEqual(
            normalize_reference("NOTIFICATION NO 13"),
            normalize_reference("notification no 13")
        )
    
    def test_punctuation_normalization(self):
        """Test punctuation handling"""
        self.assertEqual(
            normalize_reference("Notification No.13"),
            normalize_reference("Notification No 13")
        )
        
        self.assertEqual(
            normalize_reference("Circular No.152"),
            normalize_reference("Circular No 152")
        )
    
    def test_circular_to_cc_normalization(self):
        """Test Circular No X maps to CC No X"""
        result = normalize_reference("Circular No 231")
        expected = normalize_reference("CC No 231")
        self.assertEqual(result, expected)
    
    def test_whitespace_cleanup(self):
        """Test extra whitespace is removed"""
        self.assertEqual(
            normalize_reference("CC  No   46"),
            "cc no 46"
        )
        
        self.assertEqual(
            normalize_reference("  Notification   No   13  "),
            "notification no 13"
        )


class TestNoiseDetection(unittest.TestCase):
    """Test noise filtering"""
    
    def test_incomplete_references_are_noise(self):
        """Test incomplete references are filtered"""
        self.assertTrue(is_noise("DNBS(PD)CC.No"))
        self.assertTrue(is_noise("notification 2"))
        self.assertTrue(is_noise("CC"))
        self.assertTrue(is_noise("No"))
    
    def test_valid_references_not_noise(self):
        """Test valid references are kept"""
        self.assertFalse(is_noise("CC No 46"))
        self.assertFalse(is_noise("Notification No 13"))
        self.assertFalse(is_noise("RBI/2016-17/11"))
    
    def test_short_references_are_noise(self):
        """Test very short strings are filtered"""
        self.assertTrue(is_noise("No"))
        self.assertTrue(is_noise("CC"))
        self.assertTrue(is_noise("123"))


class TestDisplayLabels(unittest.TestCase):
    """Test display label formatting"""
    
    def test_display_label_formatting(self):
        """Test proper capitalization for display"""
        self.assertEqual(
            create_display_label("cc no 46"),
            "CC No 46"
        )
        
        self.assertEqual(
            create_display_label("notification no 13"),
            "Notification No 13"
        )
    
    def test_rbi_reference_formatting(self):
        """Test RBI reference display"""
        # RBI references with slashes stay lowercase (special format)
        label = create_display_label("rbi/2016-17/11")
        # This format doesn't capitalize RBI, which is correct
        self.assertIn("rbi", label.lower())


class TestGraphStructure(unittest.TestCase):
    """Test NetworkX graph building"""
    
    @classmethod
    def setUpClass(cls):
        """Build graph once for all tests"""
        cls.graph = build_graph_v2(str(PROJECT_ROOT / "cross_references.json"))
    
    def test_graph_created(self):
        """Test graph object is created"""
        self.assertIsNotNone(self.graph)
        self.assertTrue(hasattr(self.graph, 'graph'))
    
    def test_node_count(self):
        """Test correct number of nodes"""
        num_nodes = self.graph.graph.number_of_nodes()
        self.assertGreater(num_nodes, 0)
        self.assertEqual(num_nodes, 14)  # 5 docs + 9 refs
    
    def test_edge_count(self):
        """Test edges are deduplicated"""
        num_edges = self.graph.graph.number_of_edges()
        self.assertGreater(num_edges, 0)
        # V1 had 19 edges with duplicates, V2 should have fewer
        self.assertEqual(num_edges, 13)
    
    def test_node_types(self):
        """Test nodes have correct types"""
        for node, data in self.graph.graph.nodes(data=True):
            self.assertIn('type', data)
            self.assertIn(data['type'], ['DOCUMENT', 'REGULATORY_REFERENCE'])
    
    def test_document_nodes(self):
        """Test document nodes exist"""
        doc_nodes = [
            n for n, d in self.graph.graph.nodes(data=True)
            if d['type'] == 'DOCUMENT'
        ]
        self.assertEqual(len(doc_nodes), 5)
        self.assertIn("25KY010711F.pdf", doc_nodes)
        self.assertIn("41YC01072013KF.pdf", doc_nodes)
    
    def test_reference_nodes(self):
        """Test reference nodes exist and are normalized"""
        ref_nodes = [
            n for n, d in self.graph.graph.nodes(data=True)
            if d['type'] == 'REGULATORY_REFERENCE'
        ]
        self.assertEqual(len(ref_nodes), 9)
        
        # Test normalization worked
        self.assertIn("cc no 46", ref_nodes)
        self.assertIn("cc no 231", ref_nodes)
        
        # Test no duplicates
        node_ids = [n.lower() for n in ref_nodes]
        self.assertEqual(len(node_ids), len(set(node_ids)))


class TestDeduplication(unittest.TestCase):
    """Test edge deduplication"""
    
    @classmethod
    def setUpClass(cls):
        """Build graph once for all tests"""
        cls.graph = build_graph_v2(str(PROJECT_ROOT / "cross_references.json"))
    
    def test_no_duplicate_edges(self):
        """Test no duplicate edges exist"""
        edge_keys = []
        for source, target, data in self.graph.graph.edges(data=True):
            key = (source, target, data['relationship_type'])
            self.assertNotIn(key, edge_keys, f"Duplicate edge found: {key}")
            edge_keys.append(key)
    
    def test_cc_no_46_merged(self):
        """Test CC No 46 duplicates were merged"""
        # V1 had: 41YC01072013KF.pdf -> CC No 46 twice
        edges_to_cc46 = [
            (s, t, d) for s, t, d in self.graph.graph.edges(data=True)
            if t == "cc no 46" and s == "41YC01072013KF.pdf"
        ]
        
        # Should be exactly 1 edge now
        self.assertEqual(len(edges_to_cc46), 1)
        
        # Should have occurrence_count > 1
        edge_data = edges_to_cc46[0][2]
        self.assertEqual(edge_data.get('occurrence_count', 1), 2)
    
    def test_cc_no_152_merged(self):
        """Test CC No 152 duplicates were merged"""
        # V1 had: 25KY010711F.pdf -> CC No 152 twice
        edges_to_cc152 = [
            (s, t, d) for s, t, d in self.graph.graph.edges(data=True)
            if t == "cc no 152" and s == "25KY010711F.pdf"
        ]
        
        # Should be exactly 1 edge now
        self.assertEqual(len(edges_to_cc152), 1)
        
        # Should have occurrence_count > 1
        edge_data = edges_to_cc152[0][2]
        self.assertEqual(edge_data.get('occurrence_count', 1), 2)
    
    def test_merged_edge_metadata(self):
        """Test merged edges preserve all metadata"""
        # Check edges that were merged have multiple requirement IDs
        for source, target, data in self.graph.graph.edges(data=True):
            if data.get('occurrence_count', 1) > 1:
                # Should have multiple requirement IDs
                req_ids = data.get('requirement_ids', [])
                self.assertGreater(len(req_ids), 1)
                
                # Should have multiple chunk IDs
                chunk_ids = data.get('chunk_ids', [])
                self.assertGreater(len(chunk_ids), 1)


class TestCentralityMetrics(unittest.TestCase):
    """Test centrality calculations"""
    
    @classmethod
    def setUpClass(cls):
        """Build graph once for all tests"""
        cls.graph = build_graph_v2(str(PROJECT_ROOT / "cross_references.json"))
        cls.stats = cls.graph.calculate_statistics()
    
    def test_degree_centrality_calculated(self):
        """Test degree centrality is calculated"""
        self.assertIn('degree_centrality', self.stats)
        self.assertIn('in_degree', self.stats['degree_centrality'])
        self.assertIn('out_degree', self.stats['degree_centrality'])
    
    def test_document_out_degree(self):
        """Test documents have outgoing edges only"""
        out_degree = self.stats['degree_centrality']['out_degree']
        in_degree = self.stats['degree_centrality']['in_degree']
        
        # Documents should have out_degree > 0
        self.assertGreater(out_degree.get('25KY010711F.pdf', 0), 0)
        
        # Documents should have in_degree = 0
        self.assertEqual(in_degree.get('25KY010711F.pdf', 0), 0)
    
    def test_reference_in_degree(self):
        """Test references have incoming edges"""
        in_degree = self.stats['degree_centrality']['in_degree']
        
        # CC No 46 should have multiple incoming
        self.assertGreater(in_degree.get('cc no 46', 0), 0)
    
    def test_most_referenced_circulars(self):
        """Test most referenced circulars are identified"""
        most_ref = self.stats.get('most_referenced_circulars', [])
        self.assertGreater(len(most_ref), 0)
        
        # Should be sorted by degree
        degrees = [degree for _, degree in most_ref]
        self.assertEqual(degrees, sorted(degrees, reverse=True))
    
    def test_most_connected_documents(self):
        """Test most connected documents are identified"""
        most_conn = self.stats.get('most_connected_documents', [])
        self.assertGreater(len(most_conn), 0)
        
        # 25KY010711F.pdf should be highly connected
        doc_names = [doc for doc, _ in most_conn]
        self.assertIn('25KY010711F.pdf', doc_names)


class TestGraphQualityMetrics(unittest.TestCase):
    """Test graph quality metrics"""
    
    @classmethod
    def setUpClass(cls):
        """Build graph once for all tests"""
        cls.graph = build_graph_v2(str(PROJECT_ROOT / "cross_references.json"))
        cls.stats = cls.graph.calculate_statistics()
    
    def test_connected_components(self):
        """Test connected components calculation"""
        self.assertIn('connected_components', self.stats)
        self.assertGreater(self.stats['connected_components'], 0)
    
    def test_density_calculation(self):
        """Test graph density is calculated"""
        self.assertIn('graph_density', self.stats)
        density = self.stats['graph_density']
        self.assertGreaterEqual(density, 0.0)
        self.assertLessEqual(density, 1.0)
    
    def test_average_degree(self):
        """Test average degree is calculated"""
        self.assertIn('average_degree', self.stats)
        avg_degree = self.stats['average_degree']
        self.assertGreater(avg_degree, 0.0)
    
    def test_unique_edge_count(self):
        """Test unique edges are counted correctly"""
        self.assertIn('unique_edges', self.stats)
        unique = self.stats['unique_edges']
        total = self.stats['total_edges']
        
        # Unique should equal total after deduplication
        self.assertEqual(unique, total)
        
        # Should be less than V1's 19 edges
        self.assertLess(unique, 19)


class TestExportFormats(unittest.TestCase):
    """Test export functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Build graph once for all tests"""
        cls.graph = build_graph_v2(str(PROJECT_ROOT / "cross_references.json"))
    
    def test_json_export(self):
        """Test JSON export structure"""
        json_data = self.graph.to_dict()
        
        self.assertIn('metadata', json_data)
        self.assertIn('nodes', json_data)
        self.assertIn('edges', json_data)
        self.assertIn('statistics', json_data)
        
        # Check version
        self.assertEqual(json_data['metadata']['version'], "2.0")
    
    def test_json_nodes_structure(self):
        """Test JSON nodes have correct structure"""
        json_data = self.graph.to_dict()
        
        for node in json_data['nodes']:
            self.assertIn('id', node)
            self.assertIn('type', node)
            self.assertIn('display_label', node)
    
    def test_json_edges_structure(self):
        """Test JSON edges have V2 structure"""
        json_data = self.graph.to_dict()
        
        for edge in json_data['edges']:
            self.assertIn('source', edge)
            self.assertIn('target', edge)
            self.assertIn('relationship_type', edge)
            self.assertIn('domains', edge)  # V2 uses list
            self.assertIn('requirement_ids', edge)  # V2 uses list
            self.assertIn('chunk_ids', edge)  # V2 uses list
            self.assertIn('occurrence_count', edge)  # V2 addition
    
    def test_dot_export(self):
        """Test DOT format export"""
        dot_content = self.graph.to_dot()
        
        self.assertIn("digraph RegulatoryKnowledgeGraphV2", dot_content)
        self.assertIn("rankdir=LR", dot_content)
        
        # Should contain document nodes
        self.assertIn("25KY010711F.pdf", dot_content)
        
        # Should contain reference nodes
        self.assertIn("cc no 46", dot_content)
    
    def test_summary_export(self):
        """Test summary text generation"""
        summary = self.graph.generate_summary()
        
        self.assertIn("REGULATORY KNOWLEDGE GRAPH SUMMARY V2", summary)
        self.assertIn("Version: 2.0", summary)
        self.assertIn("GRAPH STRUCTURE", summary)
        self.assertIn("CENTRALITY ANALYSIS", summary)
        self.assertIn("Total Nodes", summary)
        # V2 uses "Total Edges (Unique)" not just "Unique Edges"
        self.assertIn("Total Edges (Unique)", summary)


class TestOutputFiles(unittest.TestCase):
    """Test output file generation"""
    
    def test_json_file_exists(self):
        """Test JSON output file exists"""
        self.assertTrue(os.path.exists(str(PROJECT_ROOT / "reference_graph_v2.json")))
    
    def test_summary_file_exists(self):
        """Test summary file exists"""
        self.assertTrue(os.path.exists(str(PROJECT_ROOT / "graph_summary_v2.txt")))
    
    def test_dot_file_exists(self):
        """Test DOT file exists"""
        self.assertTrue(os.path.exists(str(PROJECT_ROOT / "reference_graph_v2.dot")))
    
    def test_json_file_valid(self):
        """Test JSON file is valid"""
        with open(str(PROJECT_ROOT / "reference_graph_v2.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('nodes', data)
        self.assertIn('edges', data)
        self.assertIn('statistics', data)


class TestRegressionFromV1(unittest.TestCase):
    """Test fixes for V1 issues"""
    
    @classmethod
    def setUpClass(cls):
        """Build graph for regression testing"""
        cls.graph = build_graph_v2(str(PROJECT_ROOT / "cross_references.json"))
    
    def test_cc_no_215_normalized(self):
        """Test CC No215 vs CC No 215 are merged"""
        # Should only have one node for this
        ref_nodes = [
            n for n, d in self.graph.graph.nodes(data=True)
            if d['type'] == 'REGULATORY_REFERENCE'
        ]
        
        # Check both variations normalize to same
        norm1 = normalize_reference("CC No215")
        norm2 = normalize_reference("CC No 215")
        self.assertEqual(norm1, norm2)
        
        # Should have single node
        matching = [n for n in ref_nodes if 'cc no 215' in n.lower()]
        self.assertEqual(len(matching), 1)
    
    def test_cc_no_231_consolidated(self):
        """Test CC No 231 and Circular No 231 are merged"""
        # Should only have one node
        ref_nodes = [
            n for n, d in self.graph.graph.nodes(data=True)
            if d['type'] == 'REGULATORY_REFERENCE' and '231' in n
        ]
        self.assertEqual(len(ref_nodes), 1)
    
    def test_notification_spacing_fixed(self):
        """Test Notification No.13 vs Notification No 13"""
        norm1 = normalize_reference("Notification No.13")
        norm2 = normalize_reference("Notification No 13")
        self.assertEqual(norm1, norm2)
    
    def test_noise_references_removed(self):
        """Test noise references are filtered"""
        ref_nodes = [
            n for n, d in self.graph.graph.nodes(data=True)
            if d['type'] == 'REGULATORY_REFERENCE'
        ]
        
        # Should not contain noise
        self.assertNotIn("notification 2", ref_nodes)
        self.assertNotIn("dnbs(pd)cc.no", ref_nodes)


def run_tests():
    """Run all tests with verbose output"""
    
    print("=" * 80)
    print("REFERENCE GRAPH V2 TEST SUITE")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNormalizationV2))
    suite.addTests(loader.loadTestsFromTestCase(TestNoiseDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestDisplayLabels))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestDeduplication))
    suite.addTests(loader.loadTestsFromTestCase(TestCentralityMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphQualityMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestExportFormats))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestRegressionFromV1))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
