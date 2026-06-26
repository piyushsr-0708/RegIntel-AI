import unittest
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from department_mapper import DepartmentMapper
from map_generator import MAPGenerator
from deadline_tracker import DeadlineTracker

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestMAPIntelligence(unittest.TestCase):
    
    def setUp(self):
        self.gen = MAPGenerator("dummy.json", "dummy_dir")
        
    def test_intelligent_title_generation(self):
        # 1. FIU nodal officer communication (Should NOT be STR reporting)
        title1 = self.gen.generate_intelligent_title(
            "AML", "STR Reporting", "FIU-IND shall appoint a nodal officer..."
        )
        self.assertEqual(title1, "Communicate with FIU-IND")
        
        # 2. Board Governance
        title2 = self.gen.generate_intelligent_title(
            "Governance", "Policy Framework", "Nominate a Director on the Board as Designated Director"
        )
        self.assertEqual(title2, "Appoint Designated Director for Compliance")
        
        # 3. Sanctions screening
        title3 = self.gen.generate_intelligent_title(
            "Risk Management", "Market Risk", "Cross-border transactions should be screened against sanctions lists."
        )
        self.assertEqual(title3, "Screen Cross-Border Transactions Against Sanctions Lists")

    def test_banned_titles(self):
        # Load the generated JSON and ensure banned titles do not exist
        output_path = str(PROJECT_ROOT / "maps/maps_output.json")
        
        banned_titles = [
            "STR Reporting",
            "AML Compliance Measures",
            "KYC Compliance Measures",
            "Reporting Compliance Measures",
            "General Compliance Measures"
        ]
        
        # We only test if the file exists. If it hasn't been generated yet during the run, we skip.
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                maps = json.load(f)
                
            for m in maps:
                title = m["task_title"]
                for banned in banned_titles:
                    self.assertNotIn(
                        banned.lower(), 
                        title.lower(), 
                        f"Banned title '{banned}' found in generated MAP: {title}"
                    )
        
if __name__ == '__main__':
    unittest.main()
