import json
import os
import tempfile
import unittest
from taxonomy_builder import (
    classify_domain,
    classify_obligation_type,
    generate_requirement_id,
    extract_effective_status,
    normalize_text,
    calculate_match_score,
    build_taxonomy
)

# ============================================================
# TEST DATA
# ============================================================

TEST_REQUIREMENTS = [
    {
        "source_file": "TEST001.pdf",
        "chunk_id": 1,
        "requirement": "Banks shall maintain KYC records for a period of ten years after the business relationship is ended.",
        "obligation_type": "Informational",
        "entity": "banks",
        "deadline": "ten years"
    },
    {
        "source_file": "TEST002.pdf",
        "chunk_id": 2,
        "requirement": "NBFCs must report all cash transactions exceeding Rs. 10 lakh to FIU-IND by 15th of the succeeding month.",
        "obligation_type": "Informational",
        "entity": "nbfcs",
        "deadline": "15th of the succeeding month"
    },
    {
        "source_file": "TEST003.pdf",
        "chunk_id": 3,
        "requirement": "Financial institutions should implement continuous SIEM monitoring for cyber threats.",
        "obligation_type": "Informational",
        "entity": "financial institutions",
        "deadline": ""
    },
    {
        "source_file": "TEST004.pdf",
        "chunk_id": 4,
        "requirement": "Banks shall verify the identity of beneficial owners for all corporate accounts.",
        "obligation_type": "Informational",
        "entity": "banks",
        "deadline": ""
    },
    {
        "source_file": "TEST005.pdf",
        "chunk_id": 5,
        "requirement": "Banks shall not open accounts without proper customer due diligence.",
        "obligation_type": "Informational",
        "entity": "banks",
        "deadline": ""
    },
    {
        "source_file": "TEST006.pdf",
        "chunk_id": 6,
        "requirement": "If the customer is a PEP, enhanced due diligence should be performed.",
        "obligation_type": "Informational",
        "entity": "banks",
        "deadline": ""
    },
    {
        "source_file": "TEST007.pdf",
        "chunk_id": 7,
        "requirement": "Banks are advised to formulate a comprehensive cybersecurity policy with Board approval.",
        "obligation_type": "Informational",
        "entity": "banks",
        "deadline": ""
    }
]

# ============================================================
# UNIT TESTS
# ============================================================

class TestTaxonomyBuilder(unittest.TestCase):
    """Unit tests for taxonomy_builder.py"""
    
    def test_normalize_text(self):
        """Test text normalization"""
        self.assertEqual(normalize_text("  TEST  "), "test")
        self.assertEqual(normalize_text("UPPER CASE"), "upper case")
        self.assertEqual(normalize_text(""), "")
    
    def test_calculate_match_score(self):
        """Test keyword match scoring"""
        text = "Banks must maintain KYC records"
        keywords = ["kyc", "maintain", "records"]
        score = calculate_match_score(text, keywords)
        self.assertGreater(score, 0)
        
        # Test no match
        score_no_match = calculate_match_score(text, ["xyz", "abc"])
        self.assertEqual(score_no_match, 0)
    
    def test_classify_domain_kyc(self):
        """Test KYC domain classification"""
        req = "Banks shall verify customer identity documents for KYC compliance"
        domain, subdomain = classify_domain(req)
        self.assertEqual(domain, "KYC")
        self.assertIn(subdomain, ["Customer Identification", "Customer Due Diligence", "Other"])
    
    def test_classify_domain_aml(self):
        """Test AML domain classification"""
        req = "All suspicious transactions must be reported to FIU-IND"
        domain, subdomain = classify_domain(req)
        self.assertEqual(domain, "AML")
        self.assertIn(subdomain, ["STR Reporting", "Transaction Monitoring", "Other"])
    
    def test_classify_domain_cybersecurity(self):
        """Test Cybersecurity domain classification"""
        req = "Implement SIEM for continuous security monitoring"
        domain, subdomain = classify_domain(req)
        self.assertEqual(domain, "Cybersecurity")
        self.assertIn(subdomain, ["Security Monitoring", "Other"])
    
    def test_classify_domain_record_retention(self):
        """Test Record Retention domain classification"""
        req = "Maintain transaction records for ten years"
        domain, subdomain = classify_domain(req)
        self.assertEqual(domain, "Record Retention")
    
    def test_classify_domain_reporting(self):
        """Test Reporting domain classification"""
        req = "Submit monthly compliance report to RBI"
        domain, subdomain = classify_domain(req)
        self.assertEqual(domain, "Reporting")
    
    def test_classify_domain_governance(self):
        """Test Governance domain classification"""
        req = "Board shall approve the cybersecurity policy framework"
        domain, subdomain = classify_domain(req)
        self.assertEqual(domain, "Governance")
    
    def test_classify_obligation_mandatory(self):
        """Test mandatory obligation classification"""
        req = "Banks shall maintain records"
        obligation = classify_obligation_type(req, "")
        self.assertEqual(obligation, "Mandatory")
        
        req2 = "NBFCs must report transactions"
        obligation2 = classify_obligation_type(req2, "")
        self.assertEqual(obligation2, "Mandatory")
    
    def test_classify_obligation_recommended(self):
        """Test recommended obligation classification"""
        req = "Banks should implement best practices"
        obligation = classify_obligation_type(req, "")
        self.assertEqual(obligation, "Recommended")
        
        req2 = "NBFCs are advised to enhance controls"
        obligation2 = classify_obligation_type(req2, "")
        self.assertEqual(obligation2, "Recommended")
    
    def test_classify_obligation_prohibited(self):
        """Test prohibited obligation classification"""
        req = "Banks shall not open accounts without KYC"
        obligation = classify_obligation_type(req, "")
        self.assertEqual(obligation, "Prohibited")
        
        req2 = "NBFCs must not engage in prohibited activities"
        obligation2 = classify_obligation_type(req2, "")
        self.assertEqual(obligation2, "Prohibited")
    
    def test_classify_obligation_conditional(self):
        """Test conditional obligation classification"""
        req = "If the customer is a PEP, enhanced due diligence is required"
        obligation = classify_obligation_type(req, "")
        self.assertEqual(obligation, "Conditional")
        
        req2 = "Where transactions exceed threshold, reporting is mandatory"
        obligation2 = classify_obligation_type(req2, "")
        self.assertEqual(obligation2, "Conditional")
    
    def test_generate_requirement_id(self):
        """Test requirement ID generation"""
        req_id = generate_requirement_id("TEST001.pdf", 5, "Sample requirement text")
        
        # Check format
        self.assertTrue(req_id.startswith("REQ_"))
        self.assertIn("TEST001", req_id)
        self.assertIn("0005", req_id)
        
        # Check uniqueness
        req_id2 = generate_requirement_id("TEST001.pdf", 5, "Different requirement text")
        self.assertNotEqual(req_id, req_id2)
        
        # Check consistency
        req_id3 = generate_requirement_id("TEST001.pdf", 5, "Sample requirement text")
        self.assertEqual(req_id, req_id3)
    
    def test_extract_effective_status_active(self):
        """Test active status detection"""
        req = "Banks shall maintain KYC records"
        status = extract_effective_status(req, "TEST.pdf", "")
        self.assertEqual(status, "Active")
    
    def test_extract_effective_status_superseded(self):
        """Test superseded status detection"""
        req = "This circular has been superseded by RBI/2024/01"
        status = extract_effective_status(req, "TEST.pdf", "")
        self.assertEqual(status, "Superseded")
        
        req2 = "These guidelines are no longer applicable"
        status2 = extract_effective_status(req2, "TEST.pdf", "")
        self.assertEqual(status2, "Superseded")
    
    def test_extract_effective_status_proposed(self):
        """Test proposed status detection"""
        req = "This is a draft guideline under consultation"
        status = extract_effective_status(req, "TEST.pdf", "")
        self.assertEqual(status, "Proposed")


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_build_taxonomy_full_pipeline(self):
        """Test complete taxonomy building pipeline"""
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(TEST_REQUIREMENTS, f)
            input_file = f.name
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            # Build taxonomy
            taxonomy_data = build_taxonomy(input_file, output_file)
            
            # Verify output file exists
            self.assertTrue(os.path.exists(output_file))
            
            # Verify number of records
            self.assertEqual(len(taxonomy_data), len(TEST_REQUIREMENTS))
            
            # Load and verify output
            with open(output_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(len(loaded_data), len(TEST_REQUIREMENTS))
            
            # Verify required fields
            for entry in loaded_data:
                self.assertIn("requirement_id", entry)
                self.assertIn("domain", entry)
                self.assertIn("subdomain", entry)
                self.assertIn("obligation_type", entry)
                self.assertIn("source_document", entry)
                self.assertIn("effective_status", entry)
                self.assertIn("requirement_text", entry)
                
                # Verify requirement_id format
                self.assertTrue(entry["requirement_id"].startswith("REQ_"))
                
                # Verify domain is valid
                valid_domains = ["KYC", "AML", "Cybersecurity", "Risk Management", 
                               "Record Retention", "Reporting", "Governance", 
                               "Technology", "General"]
                self.assertIn(entry["domain"], valid_domains)
                
                # Verify obligation type is valid
                valid_obligations = ["Mandatory", "Recommended", "Prohibited", 
                                   "Conditional", "Informational"]
                self.assertIn(entry["obligation_type"], valid_obligations)
                
                # Verify effective status is valid
                valid_statuses = ["Active", "Superseded", "Proposed"]
                self.assertIn(entry["effective_status"], valid_statuses)
        
        finally:
            # Cleanup
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_specific_classifications(self):
        """Test specific requirement classifications"""
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(TEST_REQUIREMENTS, f)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            taxonomy_data = build_taxonomy(input_file, output_file)
            
            # Test 1: Record retention should be classified correctly
            retention_req = [t for t in taxonomy_data 
                           if "ten years" in t["requirement_text"]][0]
            self.assertEqual(retention_req["domain"], "Record Retention")
            self.assertEqual(retention_req["obligation_type"], "Mandatory")
            
            # Test 2: CTR reporting should be AML
            ctr_req = [t for t in taxonomy_data 
                      if "FIU-IND" in t["requirement_text"]][0]
            self.assertEqual(ctr_req["domain"], "AML")
            self.assertEqual(ctr_req["obligation_type"], "Mandatory")
            
            # Test 3: SIEM should be Cybersecurity
            siem_req = [t for t in taxonomy_data 
                       if "SIEM" in t["requirement_text"]][0]
            self.assertEqual(siem_req["domain"], "Cybersecurity")
            self.assertEqual(siem_req["obligation_type"], "Recommended")
            
            # Test 4: Beneficial owner should be KYC
            bo_req = [t for t in taxonomy_data 
                     if "beneficial owner" in t["requirement_text"]][0]
            self.assertEqual(bo_req["domain"], "KYC")
            
            # Test 5: Prohibited should be detected
            prohibited_req = [t for t in taxonomy_data 
                            if "shall not" in t["requirement_text"]][0]
            self.assertEqual(prohibited_req["obligation_type"], "Prohibited")
            
            # Test 6: Conditional should be detected
            conditional_req = [t for t in taxonomy_data 
                             if t["requirement_text"].startswith("If")][0]
            self.assertEqual(conditional_req["obligation_type"], "Conditional")
            
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


# ============================================================
# TEST SUITE RUNNER
# ============================================================

def run_tests():
    """Run all tests"""
    
    print("=" * 80)
    print("TAXONOMY BUILDER - TEST SUITE")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestTaxonomyBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
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
