"""
Test Suite for Phase 7 Quality Gate Module
"""

import unittest
from phase7_quality_gate import MODULES, QualityGate

class TestPhase7QualityGate(unittest.TestCase):
    """Test quality gate functionality"""
    
    def test_01_modules_defined(self):
        """Test validation modules are defined"""
        self.assertGreater(len(MODULES), 0)
        self.assertEqual(len(MODULES), 3)
    
    def test_02_module_structure(self):
        """Test module structure"""
        for module in MODULES:
            self.assertIn('name', module)
            self.assertIn('script', module)
            self.assertIn('description', module)
    
    def test_03_module_scripts_exist(self):
        """Test module scripts exist"""
        import os
        
        for module in MODULES:
            script = module['script']
            self.assertTrue(os.path.exists(script), 
                          f"Module script not found: {script}")
    
    def test_04_quality_gate_initialization(self):
        """Test quality gate initialization"""
        gate = QualityGate()
        
        self.assertIsNotNone(gate)
        self.assertIsInstance(gate.results, dict)
    
    def test_05_determine_overall_status(self):
        """Test overall status determination"""
        gate = QualityGate()
        
        # Test PASS scenario
        gate.results = {
            'Module 1': 'PASS',
            'Module 2': 'PASS',
            'Module 3': 'PASS'
        }
        self.assertEqual(gate.determine_overall_status(), 'READY FOR DEMO')
        
        # Test FAIL scenario
        gate.results = {
            'Module 1': 'PASS',
            'Module 2': 'FAIL',
            'Module 3': 'PASS'
        }
        self.assertEqual(gate.determine_overall_status(), 'NEEDS REVIEW')
        
        # Test WARNING scenario
        gate.results = {
            'Module 1': 'WARNING',
            'Module 2': 'PASS',
            'Module 3': 'PASS'
        }
        self.assertEqual(gate.determine_overall_status(), 'NEEDS REVIEW')


def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("PHASE 7 QUALITY GATE TEST SUITE")
    print("=" * 80)
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase7QualityGate)
    
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
