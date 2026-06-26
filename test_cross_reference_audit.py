"""
Test Suite for Cross-Reference Audit Module
"""

import unittest
import json
import os
from cross_reference_audit import CrossReferenceAuditor, REFERENCE_PATTERNS

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCrossReferenceAudit(unittest.TestCase):
    """Test cross-reference audit functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.taxonomy_file = str(PROJECT_ROOT / "data/requirements/requirements_taxonomy.json")
        cls.cross_ref_file = str(PROJECT_ROOT / "cross_references.json")
        cls.auditor = CrossReferenceAuditor(cls.taxonomy_file, cls.cross_ref_file)
    
    def test_01_load_data(self):
        """Test data loading"""
        self.assertGreater(len(self.auditor.requirements), 0)
        self.assertIsNotNone(self.auditor.cross_refs)
    
    def test_02_reference_patterns_defined(self):
        """Test reference patterns are defined"""
        self.assertGreater(len(REFERENCE_PATTERNS), 0)
        
        # Check pattern structure
        for pattern, name in REFERENCE_PATTERNS:
            self.assertIsInstance(pattern, str)
            self.assertIsInstance(name, str)
    
    def test_03_extract_raw_references(self):
        """Test raw reference extraction"""
        self.auditor.extract_raw_references()
        
        self.assertIsInstance(self.auditor.raw_references, list)
        self.assertGreater(len(self.auditor.pattern_stats), 0)
    
    def test_04_load_parsed_references(self):
        """Test parsed reference loading"""
        self.auditor.load_parsed_references()
        
        self.assertIsInstance(self.auditor.parsed_references, set)
    
    def test_05_normalize_reference(self):
        """Test reference normalization"""
        norm1 = self.auditor._normalize_reference("CC No. 46")
        norm2 = self.auditor._normalize_reference("CC No 46")
        
        self.assertEqual(norm1, norm2)
    
    def test_06_find_missed_references(self):
        """Test missed reference detection"""
        self.auditor.extract_raw_references()
        self.auditor.load_parsed_references()
        self.auditor.find_missed_references()
        
        self.assertIsInstance(self.auditor.missed_references, list)
    
    def test_07_calculate_coverage(self):
        """Test coverage calculation"""
        self.auditor.extract_raw_references()
        self.auditor.load_parsed_references()
        
        coverage = self.auditor.calculate_coverage()
        
        self.assertGreaterEqual(coverage, 0)
        self.assertLessEqual(coverage, 100)
    
    def test_08_generate_missed_file(self):
        """Test missed references file generation"""
        self.auditor.extract_raw_references()
        self.auditor.load_parsed_references()
        self.auditor.find_missed_references()
        self.auditor.generate_missed_file()
        
        output_file = str(PROJECT_ROOT / "missed_references.json")
        self.assertTrue(os.path.exists(output_file))
    
    def test_09_generate_report(self):
        """Test report generation"""
        self.auditor.extract_raw_references()
        self.auditor.load_parsed_references()
        self.auditor.find_missed_references()
        status = self.auditor.generate_report()
        
        self.assertIn(status, ['PASS', 'WARNING', 'FAIL'])
        
        output_file = str(PROJECT_ROOT / "cross_reference_audit_report.txt")
        self.assertTrue(os.path.exists(output_file))
    
    def test_10_run_full_audit(self):
        """Test complete audit run"""
        status = self.auditor.run_audit()
        self.assertIn(status, ['PASS', 'WARNING', 'FAIL'])


def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("CROSS-REFERENCE AUDIT TEST SUITE")
    print("=" * 80)
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCrossReferenceAudit)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
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
