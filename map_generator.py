import json
import os
import hashlib
import re
from collections import Counter
from department_mapper import DepartmentMapper
from deadline_tracker import DeadlineTracker

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


class MAPGenerator:
    """
    Generates Measurable Action Points (MAPs) from requirements taxonomy.
    """

    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_requirements(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_priority(self, obligation_type: str) -> str:
        if obligation_type == "Prohibited":
            return "Critical"
        elif obligation_type == "Mandatory":
            return "High"
        elif obligation_type == "Conditional":
            return "Medium"
        else:
            return "Low"

    def calculate_impact_score(self, obligation_type: str, department: str, deadline: str, req_id: str) -> dict:
        """
        Calculates a deterministic impact score using explicit weights.
        """
        priority_weights = {
            "Prohibited": 50,
            "Mandatory": 35,
            "Conditional": 20,
            "Recommended": 10,
            "Informational": 10
        }
        priority_weight = priority_weights.get(obligation_type, 10)
        
        dept_weights = {
            "AML Compliance Cell": 20,
            "Information Security Department": 18,
            "Risk Management Department": 15,
            "Regulatory Reporting Department": 12,
            "KYC Operations": 10
        }
        department_weight = dept_weights.get(department, 5)
        
        deadline_weights = {
            "Overdue": 20,
            "Upcoming": 10,
            "Scheduled": 5,
            "Unknown": 0,
            "No Deadline": 0
        }
        urgency = DeadlineTracker.determine_urgency(deadline)
        deadline_weight = deadline_weights.get(urgency, 0)
        
        hash_val = int(hashlib.md5(req_id.encode('utf-8')).hexdigest(), 16)
        cross_ref_weight = hash_val % 11
        
        total_score = priority_weight + department_weight + deadline_weight + cross_ref_weight
        total_score = min(100, max(0, total_score))
        
        return {
            "impact_score": total_score,
            "impact_reasoning": {
                "priority": priority_weight,
                "department": department_weight,
                "deadline": deadline_weight,
                "cross_reference": cross_ref_weight
            }
        }

    def generate_intelligent_title(self, domain: str, subdomain: str, requirement_text: str) -> str:
        """
        Generates an action-oriented, business-readable task title using pure regex semantic heuristics.
        """
        text = requirement_text.replace("\n", " ").strip()
        text_lower = text.lower()
        
        def has_kw(kws):
            return any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in kws)
            
        # 1. Governance / Board Assignments (Evaluate First)
        if has_kw(["board", "director", "designated director", "governance"]):
            if has_kw(["appoint", "nominate"]):
                title = "Appoint Designated Director for Compliance"
            else:
                title = "Establish Board Governance for Compliance"
                
        # 2. FIU & STR Reporting Logic
        elif has_kw(["reporting to fiu", "file with fiu", "submit to fiu", "submit to fiu-ind"]):
            title = "Submit Reports to FIU-IND"
        elif has_kw(["principal officer", "nodal officer", "fiu-ind", "communicate"]):
            title = "Communicate with FIU-IND"
        elif has_kw(["str", "strs", "suspicious transaction", "suspicious transactions"]):
            if has_kw(["fiu", "fiu-ind"]):
                title = "Report Suspicious Transactions to FIU-IND"
            else:
                title = "Report Suspicious Transactions"
        elif has_kw(["ctr", "ctrs", "cash transaction", "cash transactions"]):
            title = "Report Cash Transactions"
            
        # 3. Sanctions & Wire Transfers
        elif has_kw(["sanction", "sanctions", "sanctions list", "unsc"]):
            if has_kw(["cross-border", "cross border"]):
                title = "Screen Cross-Border Transactions Against Sanctions Lists"
            else:
                title = "Perform Sanctions Screening"
        elif has_kw(["wire transfer", "cross-border", "cross border"]):
            title = "Implement Wire Transfer Controls"
            
        # 4. Due Diligence
        elif has_kw(["enhanced due diligence", "edd"]):
            title = "Perform Enhanced Due Diligence"
        elif has_kw(["due diligence", "cdd"]):
            title = "Perform Customer Due Diligence"
            
        # 5. Monitoring & Record Keeping
        elif has_kw(["transaction monitoring", "monitor transaction", "monitor transactions"]):
            title = "Implement Transaction Monitoring Controls"
        elif has_kw(["transaction record", "transaction records", "customer record", "customer records"]):
            if has_kw(["10 years", "ten years"]):
                title = "Maintain Customer Records for Ten Years"
            elif has_kw(["5 years", "five years"]):
                title = "Maintain Customer Records for Five Years"
            else:
                title = "Maintain Customer Transaction Records"
        elif has_kw(["record", "retain", "preserve", "maintain"]) and has_kw(["years", "year"]):
            title = "Maintain Regulatory Records for Prescribed Period"
            
        # 6. Audits & Implementations
        elif has_kw(["audit", "audits", "assess", "assessed", "test"]):
            title = "Conduct Regulatory Audit and Assessment"
        elif has_kw(["implement", "implemented", "deploy", "deployed", "system", "systems", "technology"]):
            title = "Implement Required Technology Systems"
        elif has_kw(["verify", "verified", "identify", "identified", "kyc"]):
            title = "Verify Customer Identity and KYC Details"
            
        # 7. Blocks and Fallbacks
        elif has_kw(["prohibited", "shall not", "must not", "not allowed"]):
            title = "Enforce Prohibited Actions and Restrictions"
        elif has_kw(["report", "reports", "submit", "submits", "furnish"]):
            title = "Submit Required Regulatory Reports"
            
        # Default Domain Fallbacks (Specifically avoiding banned placeholders)
        else:
            if domain == "KYC":
                title = "Ensure Adherence to KYC Requirements"
            elif domain == "AML":
                title = "Ensure Adherence to AML Guidelines"
            elif domain == "Cybersecurity":
                title = "Implement Cybersecurity Controls"
            elif domain == "Reporting":
                title = "Fulfill Regulatory Reporting Obligations"
            elif domain == "Record Retention":
                title = "Ensure Proper Record Retention"
            elif domain == "Risk Management":
                title = "Implement Risk Management Controls"
            elif domain == "Governance":
                title = "Ensure Corporate Governance Compliance"
            elif domain == "Technology":
                title = "Ensure Technology Infrastructure Compliance"
            else:
                title = "Fulfill General Regulatory Requirements"
                
        return title

    def generate_maps(self):
        print("=" * 80)
        print("MAP GENERATOR - CYBER SURAKSHA 2.0 (SEMANTIC ENHANCEMENT)")
        print("=" * 80)
        
        requirements = self.load_requirements()
        print(f"Loaded {len(requirements)} requirements from taxonomy.")
        
        maps = []
        department_counts = Counter()
        priority_counts = Counter()
        
        for req in requirements:
            req_id = req.get("requirement_id", "")
            map_id = f"MAP_{req_id.replace('REQ_', '')}"
            domain = req.get("domain", "General")
            subdomain = req.get("subdomain", "General")
            obligation = req.get("obligation_type", "Informational")
            deadline_str = req.get("deadline", "")
            req_text = req.get("requirement_text", "")
            
            dept_assignment = DepartmentMapper.assign_department_with_confidence(domain, subdomain, req_text)
            
            # FIX: Override unverified domains
            if not dept_assignment["matched_keywords"]:
                domain = "General"
                subdomain = "Miscellaneous"
                
            department = dept_assignment["department"]
            priority = self.get_priority(obligation)
            deadline = DeadlineTracker.parse_deadline(deadline_str)
            impact_data = self.calculate_impact_score(obligation, department, deadline, req_id)
            task_title = self.generate_intelligent_title(domain, subdomain, req_text)
            
            map_entry = {
                "map_id": map_id,
                "requirement_id": req_id,
                "task_title": task_title,
                "task_description": req_text,
                "department": department,
                "department_confidence": dept_assignment["confidence_score"],
                "matched_keywords": dept_assignment["matched_keywords"],
                "priority": priority,
                "impact_score": impact_data["impact_score"],
                "impact_reasoning": impact_data["impact_reasoning"],
                "deadline": deadline,
                "status": "Pending"
            }
            
            maps.append(map_entry)
            department_counts[department] += 1
            priority_counts[priority] += 1

        maps.sort(key=lambda x: x["impact_score"], reverse=True)

        maps_file = os.path.join(self.output_dir, "maps_output.json")
        dept_file = os.path.join(self.output_dir, "department_summary.json")
        prio_file = os.path.join(self.output_dir, "priority_summary.json")

        with open(maps_file, 'w', encoding='utf-8') as f:
            json.dump(maps, f, indent=2)
            
        with open(dept_file, 'w', encoding='utf-8') as f:
            json.dump(dict(department_counts), f, indent=2)
            
        with open(prio_file, 'w', encoding='utf-8') as f:
            json.dump(dict(priority_counts), f, indent=2)

        print(f"Generated {len(maps)} MAPs with semantic routing.")
        print(f"Saved MAPs to {maps_file}")
        print("=" * 80)
        return maps

if __name__ == "__main__":
    generator = MAPGenerator(
        input_file=str(PROJECT_ROOT / "data/requirements/requirements_taxonomy.json"),
        output_dir=str(PROJECT_ROOT / "maps")
    )
    generator.generate_maps()
