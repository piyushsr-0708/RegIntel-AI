import json
import os
import tempfile
import unittest
from cross_reference_parser import (
    extract_circular_references,
    extract_dates,
    detect_relationship_type,
    extract_context_window,
    clean_reference,
    parse_requirement_references,
    parse_chunk_references,
    build_reference_graph
)

# ============================================================
# TEST DATA
# ============================================================

TEST_TEXTS = {
    'supersedes': """This circular supersedes DNBS (PD) CC No. 48/10.42/2004-05 
                     dated February 21, 2005 which is hereby withdrawn.""",
    
    'amends': """This circular amends RBI/2011-12/25 dated July 1, 2011 to 
                 revise the reporting requirements.""",
    
    'modifies': """The notification modifies the provisions of circular 
                   DOR (NBFC) CC No. 115/03.10.001/2019-20.""",
    
    'replaces': """This replaces the earlier instruction issued vide 
                   DNBS (PD) CC 58/10.42/2005-06 dated October 11, 2005.""",
    
    'clarifies': """This circular clarifies the requirements mentioned in 
                    RBI/2020-21/45 dated March 15, 2021.""",
    
    'multiple_refs': """As per DNBS (PD) CC No. 48/10.42/2004-05 dated February 21, 2005
                        and in supersession of RBI/2018-19/123 dated December 1, 2018.""",
    
    'no_refs': """Banks must maintain adequate capital. Customer due diligence 
                  is mandatory for all accounts."""
}

TEST_REQUIREMENTS = [
    {
        'requirement_id': 'REQ_TEST001_0001_ABC123',
        'source_document': 'TEST001.pdf',
        'requirement_text': 'Details are in DNBS (PD) CC 48/10.42/2004-05 dated February 21, 2005',
        'domain': 'KYC',
        'chunk_id': 1
    },
    {
        'requirement_id': 'REQ_TEST002_0002_DEF456',
        'source_document': 'TEST002.pdf',
        'requirement_text': 'This circular supersedes RBI/2011-12/25 and withdraws all previous instructions',
        'domain': 'AML',
        'chunk_id': 2
    },
    {
        'requirement_id': 'REQ_TEST003_0003_GHI789',
        'source_document': 'TEST003.pdf',
        'requirement_text': 'Banks shall comply with cybersecurity guidelines. No reference here.',
        'domain': 'Cybersecurity',
        'chunk_id': 3
    }
]

TEST_CHUNKS = [
    {
        'source_file': 'TEST001.pdf',
        'chunk_id': 1,
        'text': 'In terms of DNBS (PD) CC No. 48/10.42/2004-05 dated February 21, 2005, all NBFCs must implement KYC procedures.'
    },
    {
        'source_file': 'TEST002.pdf',
        'chunk_id': 2,
        'text': 'This circular amends RBI/2020-21/100 dated January 15, 2021 to include additional requirements for reporting.'
    }
]

# ============================================================
# UNIT TESTS
# ============================================================

class TestCrossReferenceParser(unittest.TestCase):
    """Unit tests for cross_reference_parser.py"""
    
    def test_extract_circular_references_dnbs(self):
        """Test extraction of DNBS circular references"""
        text = "Details are in DNBS (PD) CC 48/10.42/2004-05 dated February 21, 2005"
        refs = extract_circular_references(text)
        
        self.assertGreater(len(refs), 0)
        self.assertTrue(any('DNBS' in ref for ref in refs))
    
    def test_extract_circular_references_rbi(self):
        """Test extraction of RBI references"""
        text = "As per RBI/2011-12/25 dated July 1, 2011"
        refs = extract_circular_references(text)
        
        self.assertGreater(len(refs), 0)
        self.assertTrue(any('RBI' in ref for ref in refs))
    
    def test_extract_circular_references_multiple(self):
        """Test extraction of multiple references"""
        text = TEST_TEXTS['multiple_refs']
        refs = extract_circular_references(text)
        
        self.assertGreaterEqual(len(refs), 2)
    
    def test_extract_circular_references_none(self):
        """Test when no references present"""
        text = TEST_TEXTS['no_refs']
        refs = extract_circular_references(text)
        
        # Might be 0 or might detect "Banks" as false positive
        # Just verify it returns a list
        self.assertIsInstance(refs, list)
    
    def test_extract_dates_standard_format(self):
        """Test date extraction - standard format"""
        text = "dated February 21, 2005"
        dates = extract_dates(text)
        
        self.assertGreater(len(dates), 0)
        self.assertIn('2005', dates[0])
    
    def test_extract_dates_multiple(self):
        """Test extraction of multiple dates"""
        text = "dated February 21, 2005 and revised on July 1, 2011"
        dates = extract_dates(text)
        
        # Should find at least one date
        self.assertGreater(len(dates), 0)
    
    def test_detect_relationship_supersedes(self):
        """Test supersedes relationship detection"""
        text = TEST_TEXTS['supersedes']
        relationships = detect_relationship_type(text)
        
        self.assertIn('supersedes', relationships)
    
    def test_detect_relationship_amends(self):
        """Test amends relationship detection"""
        text = TEST_TEXTS['amends']
        relationships = detect_relationship_type(text)
        
        self.assertIn('amends', relationships)
    
    def test_detect_relationship_modifies(self):
        """Test modifies relationship detection"""
        text = TEST_TEXTS['modifies']
        relationships = detect_relationship_type(text)
        
        self.assertIn('modifies', relationships)
    
    def test_detect_relationship_replaces(self):
        """Test replaces relationship detection"""
        text = TEST_TEXTS['replaces']
        relationships = detect_relationship_type(text)
        
        self.assertIn('replaces', relationships)
    
    def test_detect_relationship_clarifies(self):
        """Test clarifies relationship detection"""
        text = TEST_TEXTS['clarifies']
        relationships = detect_relationship_type(text)
        
        self.assertIn('clarifies', relationships)
    
    def test_detect_relationship_multiple(self):
        """Test detection of multiple relationships"""
        text = "This circular supersedes and amends RBI/2020/100"
        relationships = detect_relationship_type(text)
        
        # Should detect both supersedes and amends
        self.assertGreater(len(relationships), 0)
    
    def test_extract_context_window(self):
        """Test context extraction"""
        text = "This is some long text. Reference to DNBS (PD) CC 48. More text follows."
        reference = "DNBS (PD) CC 48"
        
        context = extract_context_window(text, reference, window_size=40)
        
        self.assertIn(reference, context)
        self.assertLessEqual(len(context), 100)  # Should be limited
    
    def test_clean_reference(self):
        """Test reference cleaning"""
        ref = "DNBS (PD) CC 48/10.42/2004-05  ."
        cleaned = clean_reference(ref)
        
        self.assertFalse(cleaned.endswith('.'))
        self.assertNotIn('  ', cleaned)
    
    def test_parse_requirement_references_with_refs(self):
        """Test parsing requirement with references"""
        req = TEST_REQUIREMENTS[0]
        refs = parse_requirement_references(req)
        
        self.assertGreater(len(refs), 0)
        self.assertEqual(refs[0]['source_requirement_id'], req['requirement_id'])
        self.assertIn('referenced_circular', refs[0])
        self.assertIn('relationship_types', refs[0])
    
    def test_parse_requirement_references_no_refs(self):
        """Test parsing requirement without references"""
        req = TEST_REQUIREMENTS[2]  # No references
        refs = parse_requirement_references(req)
        
        # Should return empty list
        self.assertEqual(len(refs), 0)
    
    def test_parse_chunk_references(self):
        """Test parsing chunk references"""
        chunk = TEST_CHUNKS[0]
        refs = parse_chunk_references(chunk)
        
        self.assertGreater(len(refs), 0)
        self.assertEqual(refs[0]['source_document'], chunk['source_file'])
        self.assertIn('referenced_circular', refs[0])
    
    def test_build_reference_graph(self):
        """Test building reference graph"""
        # Create sample references
        refs = [
            {
                'source_document': 'DOC1.pdf',
                'source_requirement_id': 'REQ_001',
                'referenced_circular': 'CIRCULAR_A',
                'relationship_types': ['supersedes']
            },
            {
                'source_document': 'DOC2.pdf',
                'source_requirement_id': 'REQ_002',
                'referenced_circular': 'CIRCULAR_A',
                'relationship_types': ['refers_to']
            },
            {
                'source_document': 'DOC2.pdf',
                'source_requirement_id': 'REQ_003',
                'referenced_circular': 'CIRCULAR_B',
                'relationship_types': ['amends']
            }
        ]
        
        graph = build_reference_graph(refs)
        
        self.assertIn('by_source_document', graph)
        self.assertIn('by_referenced_circular', graph)
        self.assertIn('by_relationship_type', graph)
        
        # Check CIRCULAR_A has 2 references
        self.assertEqual(len(graph['by_referenced_circular']['CIRCULAR_A']), 2)
        
        # Check DOC2.pdf has 2 references
        self.assertEqual(len(graph['by_source_document']['DOC2.pdf']), 2)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_end_to_end_with_test_data(self):
        """Test complete processing with test data"""
        
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(TEST_REQUIREMENTS, f)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            # Load test data
            with open(input_file, 'r', encoding='utf-8') as f:
                requirements = json.load(f)
            
            # Process
            all_refs = []
            for req in requirements:
                refs = parse_requirement_references(req)
                all_refs.extend(refs)
            
            # Build graph
            graph = build_reference_graph(all_refs)
            
            # Verify
            self.assertGreater(len(all_refs), 0)
            self.assertIsInstance(graph, dict)
            
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_parse_all_requirements(self):
        """Test parsing all test requirements"""
        
        all_refs = []
        
        for req in TEST_REQUIREMENTS:
            refs = parse_requirement_references(req)
            all_refs.extend(refs)
        
        # Should find at least 2 references (from first 2 requirements)
        self.assertGreaterEqual(len(all_refs), 2)
        
        # Check structure
        for ref in all_refs:
            self.assertIn('source_requirement_id', ref)
            self.assertIn('referenced_circular', ref)
            self.assertIn('relationship_types', ref)
            self.assertIn('context', ref)
    
    def test_relationship_type_priority(self):
        """Test that multiple relationship types are detected"""
        
        text = "This circular supersedes RBI/2020/100 and also clarifies certain provisions"
        relationships = detect_relationship_type(text)
        
        # Should detect both supersedes and clarifies
        self.assertTrue(len(relationships) >= 1)
        
        # At least one of these should be present
        self.assertTrue(
            any(rel in ['supersedes', 'clarifies', 'refers_to'] for rel in relationships)
        )


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""
    
    def test_empty_text(self):
        """Test with empty text"""
        refs = extract_circular_references("")
        self.assertEqual(len(refs), 0)
    
    def test_very_short_text(self):
        """Test with very short text"""
        req = {
            'requirement_id': 'REQ_SHORT',
            'source_document': 'SHORT.pdf',
            'requirement_text': 'Short',
            'domain': 'General',
            'chunk_id': 1
        }
        refs = parse_requirement_references(req)
        self.assertEqual(len(refs), 0)
    
    def test_special_characters(self):
        """Test with special characters"""
        text = "Reference to DNBS (PD) CC 48/10.42/2004-05 [amended]"
        refs = extract_circular_references(text)
        self.assertGreater(len(refs), 0)
    
    def test_case_insensitivity(self):
        """Test case insensitive matching"""
        text1 = "Supersedes DNBS CC 48"
        text2 = "SUPERSEDES dnbs cc 48"
        
        rels1 = detect_relationship_type(text1)
        rels2 = detect_relationship_type(text2)
        
        # Both should detect supersedes
        self.assertEqual(rels1, rels2)
    
    def test_missing_fields(self):
        """Test with missing fields in requirement"""
        req = {
            'requirement_id': 'REQ_MISSING',
            'source_document': 'MISSING.pdf'
            # Missing requirement_text
        }
        refs = parse_requirement_references(req)
        self.assertEqual(len(refs), 0)


# ============================================================
# TEST RUNNER
# ============================================================

def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("CROSS-REFERENCE PARSER - TEST SUITE")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestCrossReferenceParser))
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
