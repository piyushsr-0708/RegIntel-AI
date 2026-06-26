"""
Test Suite for Resolver Benchmark Module
"""

import unittest
import os
from resolver_benchmark import TEST_QUERIES

class TestResolverBenchmark(unittest.TestCase):
    """Test resolver benchmark functionality"""
    
    def test_01_test_queries_defined(self):
        """Test that test queries are defined"""
        self.assertGreater(len(TEST_QUERIES), 0)
        self.assertIsInstance(TEST_QUERIES, list)
    
    def test_02_query_format(self):
        """Test query format"""
        for query in TEST_QUERIES:
            self.assertIsInstance(query, str)
            self.assertGreater(len(query), 0)
    
    def test_03_output_files_config(self):
        """Test output files are configured"""
        from resolver_benchmark import OUTPUT_REPORT, OUTPUT_RESULTS
        
        self.assertIsNotNone(OUTPUT_REPORT)
        self.assertIsNotNone(OUTPUT_RESULTS)
    
    def test_04_minimum_query_coverage(self):
        """Test minimum query coverage"""
        # Should have at least 10 queries
        self.assertGreaterEqual(len(TEST_QUERIES), 10)
        
        # Should cover key domains
        query_text = ' '.join(TEST_QUERIES).lower()
        
        self.assertIn('record', query_text)
        self.assertIn('kyc', query_text or 'customer' in query_text)
        self.assertIn('aml', query_text or 'transaction' in query_text)


def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("RESOLVER BENCHMARK TEST SUITE")
    print("=" * 80)
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestResolverBenchmark)
    
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
