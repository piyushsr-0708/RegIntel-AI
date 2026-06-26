"""
Test Suite for Taxonomy Audit Module
"""

import unittest
import json
import os
from taxonomy_audit import TaxonomyAuditor, DOMAIN_KEYWORDS

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTaxonomyAudit(unittest.TestCase):
    """Test taxonomy audit functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.taxonomy_file = str(PROJECT_ROOT / "data/requirements/requirements_taxonomy.json")
        cls.auditor = TaxonomyAuditor(cls.taxonomy_file)
    
    def test_01_load_requirements(self):
        """Test requirements loading"""
        self.assertGreater(len(self.auditor.requirements), 0)
        self.assertEqual(len(self.auditor.requirements), 2941)
    
    def test_02_analyze_distributions(self):
        """Test distribution analysis"""
        self.auditor.analyze_distributions()
        
        self.assertGreater(len(self.auditor.domain_distribution), 0)
        self.assertGreater(len(self.auditor.obligation_distribution), 0)
    
    def test_03_domain_keywords_defined(self):
        """Test domain keywords are defined"""
        self.assertIn('AML', DOMAIN_KEYWORDS)
        self.assertIn('KYC', DOMAIN_KEYWORDS)
        self.assertIn('Cybersecurity', DOMAIN_KEYWORDS)
        
        self.assertGreater(len(DOMAIN_KEYWORDS['AML']), 0)
    
    def test_04_check_consistency(self):
        """Test consistency checking"""
        self.auditor.analyze_distributions()
        self.auditor.check_consistency()
        
        # Misclassifications list should exist
        self.assertIsInstance(self.auditor.misclassifications, list)
    
    def test_05_sample_requirements(self):
        """Test requirement sampling"""
        samples = self.auditor.sample_requirements('AML', count=10)
        
        self.assertIsInstance(samples, list)
        self.assertLessEqual(len(samples), 10)
    
    def test_06_generate_samples_file(self):
        """Test samples file generation"""
        self.auditor.analyze_distributions()
        self.auditor.generate_samples_file()
        
        output_file = str(PROJECT_ROOT / "taxonomy_audit_samples.txt")
        self.assertTrue(os.path.exists(output_file))
    
    def test_07_generate_report(self):
        """Test report generation"""
        self.auditor.analyze_distributions()
        self.auditor.check_consistency()
        status = self.auditor.generate_report()
        
        self.assertIn(status, ['PASS', 'WARNING', 'FAIL'])
        
        output_file = str(PROJECT_ROOT / "taxonomy_audit_report.txt")
        self.assertTrue(os.path.exists(output_file))
    
    def test_08_run_full_audit(self):
        """Test complete audit run"""
        status = self.auditor.run_audit()
        self.assertIn(status, ['PASS', 'WARNING', 'FAIL'])


def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("TAXONOMY AUDIT TEST SUITE")
    print("=" * 80)
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTaxonomyAudit)
    
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
