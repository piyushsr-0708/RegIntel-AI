import json
import os
import tempfile
import unittest
from reference_graph import (
    normalize_reference,
    is_noise,
    create_clean_label,
    RegulatoryGraph,
    build_graph
)

# ============================================================
# TEST DATA
# ============================================================

TEST_REFERENCES = {
    "metadata": {
        "generated_at": "2026-06-20T12:00:00",
        "total_references": 5
    },
    "references": [
        {
            "source_document": "TEST001.pdf",
            "referenced_circular": "CC No 46",
            "relationship_types": ["refers_to"],
            "domain": "KYC",
            "source_requirement_id": "REQ_001",
            "chunk_id": 1
        },
        {
            "source_document": "TEST001.pdf",
            "referenced_circular": "Circular No 46",  # Should normalize to same as above
            "relationship_types": ["consolidates"],
            "domain": "AML",
            "source_requirement_id": "REQ_002",
            "chunk_id": 2
        },
        {
            "source_document": "TEST002.pdf",
            "referenced_circular": "Notification No.13",
            "relationship_types": ["refers_to"],
            "domain": "Reporting",
            "source_requirement_id": "REQ_003",
            "chunk_id": 3
        },
        {
            "source_document": "TEST002.pdf",
            "referenced_circular": "Notification No 13",  # Should normalize to same as above
            "relationship_types": ["modifies"],
            "domain": "Governance",
            "source_requirement_id": "REQ_004",
            "chunk_id": 4
        },
        {
            "source_document": "TEST003.pdf",
            "referenced_circular": "notification 2",  # Should be filtered as noise
            "relationship_types": ["refers_to"],
            "domain": "General",
            "source_requirement_id": "REQ_005",
            "chunk_id": 5
        }
    ]
}

# ============================================================
# UNIT TESTS
# ============================================================

class TestNormalization(unittest.TestCase):
    """Test reference normalization functions"""
    
    def test_normalize_cc_vs_circular(self):
        """Test normalization of CC vs Circular"""
        ref1 = "CC No 46"
        ref2 = "Circular No 46"
        
        norm1 = normalize_reference(ref1)
        norm2 = normalize_reference(ref2)
        
        self.assertEqual(norm1, norm2)
    
    def test_normalize_notification_dot(self):
        """Test normalization of Notification No. vs No"""
        ref1 = "Notification No.13"
        ref2 = "Notification No 13"
        
        norm1 = normalize_reference(ref1)
        norm2 = normalize_reference(ref2)
        
        self.assertEqual(norm1, norm2)
    
    def test_normalize_case_insensitive(self):
        """Test case insensitive normalization"""
        ref1 = "CC No 231"
        ref2 = "cc no 231"
        ref3 = "CC NO 231"
        
        norm1 = normalize_reference(ref1)
        norm2 = normalize_reference(ref2)
        norm3 = normalize_reference(ref3)
        
        self.assertEqual(norm1, norm2)
        self.assertEqual(norm2, norm3)
    
    def test_normalize_extra_spaces(self):
        """Test normalization with extra spaces"""
        ref = "CC  No   46"
        norm = normalize_reference(ref)
        
        self.assertNotIn("  ", norm)
    
    def test_is_noise_notification_number(self):
        """Test noise detection for 'notification 2'"""
        ref = "notification 2"
        self.assertTrue(is_noise(ref))
    
    def test_is_noise_incomplete_reference(self):
        """Test noise detection for incomplete reference"""
        ref = "DNBS(PD)CC.No"
        self.assertTrue(is_noise(ref))
    
    def test_is_noise_valid_reference(self):
        """Test that valid references are not marked as noise"""
        ref = "CC No 46"
        self.assertFalse(is_noise(ref))
    
    def test_create_clean_label(self):
        """Test clean label creation"""
        ref = "cc no 46"
        label = create_clean_label(ref)
        
        # Should capitalize properly
        self.assertTrue(label[0].isupper())


class TestRegulatoryGraph(unittest.TestCase):
    """Test RegulatoryGraph class"""
    
    def setUp(self):
        """Set up test graph"""
        self.graph = RegulatoryGraph()
    
    def test_add_document_node(self):
        """Test adding document node"""
        node_id = self.graph.add_node("TEST.pdf", "DOCUMENT")
        
        self.assertIsNotNone(node_id)
        self.assertIn("TEST.pdf", self.graph.nodes)
        self.assertEqual(self.graph.nodes["TEST.pdf"]["type"], "DOCUMENT")
    
    def test_add_reference_node(self):
        """Test adding reference node"""
        node_id = self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        
        self.assertIsNotNone(node_id)
        # Should be normalized
        norm_id = normalize_reference("CC No 46")
        self.assertIn(norm_id, self.graph.nodes)
    
    def test_add_duplicate_node(self):
        """Test that duplicate nodes are not added"""
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        
        # Should only have one node
        self.assertEqual(len(self.graph.nodes), 1)
    
    def test_normalize_duplicate_references(self):
        """Test that similar references are normalized to same node"""
        node_id1 = self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        node_id2 = self.graph.add_node("Circular No 46", "REGULATORY_REFERENCE")
        
        # Should have same normalized ID
        self.assertEqual(node_id1, node_id2)
        
        # Should only have one node for this reference
        norm_id = normalize_reference("CC No 46")
        matching_nodes = [n for n in self.graph.nodes if normalize_reference(n) == norm_id]
        self.assertEqual(len(matching_nodes), 1)
    
    def test_filter_noise_nodes(self):
        """Test that noise nodes are filtered out"""
        node_id = self.graph.add_node("notification 2", "REGULATORY_REFERENCE")
        
        # Should return None for noise
        self.assertIsNone(node_id)
    
    def test_add_edge(self):
        """Test adding edge"""
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        
        self.graph.add_edge(
            "TEST.pdf",
            "CC No 46",
            "refers_to",
            "KYC",
            "REQ_001",
            1
        )
        
        self.assertEqual(len(self.graph.edges), 1)
        self.assertEqual(self.graph.edges[0]["relationship_type"], "refers_to")
    
    def test_calculate_statistics(self):
        """Test statistics calculation"""
        # Add some nodes and edges
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        self.graph.add_edge("TEST.pdf", "CC No 46", "refers_to", "KYC", "REQ_001", 1)
        
        stats = self.graph.calculate_statistics()
        
        self.assertIn("total_nodes", stats)
        self.assertIn("total_edges", stats)
        self.assertIn("document_nodes", stats)
        self.assertIn("reference_nodes", stats)
        self.assertGreater(stats["total_nodes"], 0)
        self.assertGreater(stats["total_edges"], 0)
    
    def test_to_dict(self):
        """Test dictionary export"""
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        self.graph.add_edge("TEST.pdf", "CC No 46", "refers_to", "KYC", "REQ_001", 1)
        
        graph_dict = self.graph.to_dict()
        
        self.assertIn("metadata", graph_dict)
        self.assertIn("nodes", graph_dict)
        self.assertIn("edges", graph_dict)
        self.assertIn("statistics", graph_dict)
        
        self.assertIsInstance(graph_dict["nodes"], list)
        self.assertIsInstance(graph_dict["edges"], list)
    
    def test_to_dot(self):
        """Test DOT format export"""
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        self.graph.add_edge("TEST.pdf", "CC No 46", "refers_to", "KYC", "REQ_001", 1)
        
        dot_content = self.graph.to_dot()
        
        self.assertIn("digraph", dot_content)
        self.assertIn("TEST.pdf", dot_content)
        self.assertIn("->", dot_content)
    
    def test_generate_summary(self):
        """Test summary generation"""
        self.graph.add_node("TEST.pdf", "DOCUMENT")
        self.graph.add_node("CC No 46", "REGULATORY_REFERENCE")
        self.graph.add_edge("TEST.pdf", "CC No 46", "refers_to", "KYC", "REQ_001", 1)
        
        summary = self.graph.generate_summary()
        
        self.assertIn("REGULATORY KNOWLEDGE GRAPH SUMMARY", summary)
        self.assertIn("Total Nodes", summary)
        self.assertIn("Total Edges", summary)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_build_graph_from_test_data(self):
        """Test building graph from test data"""
        
        # Create temp input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(TEST_REFERENCES, f)
            input_file = f.name
        
        try:
            # Build graph
            graph = build_graph(input_file)
            
            # Verify nodes
            self.assertGreater(len(graph.nodes), 0)
            
            # Verify edges
            self.assertGreater(len(graph.edges), 0)
            
            # Verify normalization worked
            # "CC No 46" and "Circular No 46" should be one node
            norm_id = normalize_reference("CC No 46")
            self.assertIn(norm_id, graph.nodes)
            
            # Verify noise was filtered
            # "notification 2" should not be in nodes
            noise_norm = normalize_reference("notification 2")
            self.assertNotIn(noise_norm, graph.nodes)
            
            # Verify statistics
            stats = graph.calculate_statistics()
            self.assertGreater(stats["total_nodes"], 0)
            self.assertGreater(stats["total_edges"], 0)
            
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)
    
    def test_full_export_cycle(self):
        """Test complete export cycle"""
        
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(TEST_REFERENCES, f)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_json = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_txt = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            output_dot = f.name
        
        try:
            # Build graph
            graph = build_graph(input_file)
            
            # Export JSON
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(graph.to_dict(), f)
            
            self.assertTrue(os.path.exists(output_json))
            self.assertGreater(os.path.getsize(output_json), 0)
            
            # Verify JSON structure
            with open(output_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertIn("nodes", data)
            self.assertIn("edges", data)
            self.assertIn("statistics", data)
            
            # Export summary
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(graph.generate_summary())
            
            self.assertTrue(os.path.exists(output_txt))
            self.assertGreater(os.path.getsize(output_txt), 0)
            
            # Export DOT
            with open(output_dot, 'w', encoding='utf-8') as f:
                f.write(graph.to_dot())
            
            self.assertTrue(os.path.exists(output_dot))
            self.assertGreater(os.path.getsize(output_dot), 0)
            
        finally:
            for f in [input_file, output_json, output_txt, output_dot]:
                if os.path.exists(f):
                    os.unlink(f)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""
    
    def test_empty_references(self):
        """Test with empty references list"""
        graph = RegulatoryGraph()
        
        # Should not crash
        stats = graph.calculate_statistics()
        self.assertEqual(stats["total_nodes"], 0)
        self.assertEqual(stats["total_edges"], 0)
    
    def test_all_noise_references(self):
        """Test when all references are noise"""
        graph = RegulatoryGraph()
        
        graph.add_node("TEST.pdf", "DOCUMENT")
        graph.add_node("notification 2", "REGULATORY_REFERENCE")
        graph.add_node("DNBS(PD)CC.No", "REGULATORY_REFERENCE")
        
        # Should only have the document node
        self.assertEqual(len(graph.nodes), 1)
    
    def test_special_characters_in_references(self):
        """Test handling of special characters"""
        graph = RegulatoryGraph()
        
        ref = "CC No. 46/2020-21"
        node_id = graph.add_node(ref, "REGULATORY_REFERENCE")
        
        self.assertIsNotNone(node_id)
    
    def test_very_long_reference_name(self):
        """Test with very long reference name"""
        graph = RegulatoryGraph()
        
        ref = "Very Long Circular Name " * 10
        node_id = graph.add_node(ref, "REGULATORY_REFERENCE")
        
        self.assertIsNotNone(node_id)


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("REFERENCE GRAPH - TEST SUITE")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestRegulatoryGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run     : {result.testsRun}")
    print(f"Successes     : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures      : {len(result.failures)}")
    print(f"Errors        : {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
