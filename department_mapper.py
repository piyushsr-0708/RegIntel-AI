import os
import sys
import re

# Load DOMAIN_RULES safely from taxonomy_builder
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from taxonomy_builder import DOMAIN_RULES
except ImportError:
    DOMAIN_RULES = {}

class DepartmentMapper:
    """
    Maps regulatory domains to specific banking departments.
    """
    
    MAPPING = {
        "KYC": "KYC Operations",
        "AML": "AML Compliance Cell",
        "Cybersecurity": "Information Security Department",
        "Technology": "IT Department",
        "Risk Management": "Risk Management Department",
        "Governance": "Board & Compliance Department",
        "Reporting": "Regulatory Reporting Department",
        "Record Retention": "Records Management Department",
        "General": "Compliance Department"
    }

    @staticmethod
    def get_department(domain: str) -> str:
        """
        Returns the appropriate banking department for a given regulatory domain.
        Defaults to 'Compliance Department' if domain is unknown.
        """
        return DepartmentMapper.MAPPING.get(domain, "Compliance Department")

    @staticmethod
    def assign_department_with_confidence(domain: str, subdomain: str, requirement_text: str) -> dict:
        """
        Assigns a department and returns a confidence score with matched keywords.
        """
        department = DepartmentMapper.get_department(domain)
        text_lower = requirement_text.lower()
        confidence = 0
        matched_keywords = []
        
        if domain in DOMAIN_RULES:
            # Check domain keywords
            domain_keywords = DOMAIN_RULES[domain].get("keywords", [])
            for kw in domain_keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    confidence += 5
                    matched_keywords.append(kw)
                    
            # Check subdomain keywords
            if subdomain in DOMAIN_RULES[domain].get("subdomains", {}):
                sub_keywords = DOMAIN_RULES[domain]["subdomains"][subdomain]
                sub_matched = False
                for kw in sub_keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', text_lower) and kw not in matched_keywords:
                        confidence += 10
                        matched_keywords.append(kw)
                        sub_matched = True
                
                if sub_matched:
                    confidence += 20  # Strong signal for matching subdomain
        
        # Reward exact phrase matches (keywords with spaces)
        exact_phrases = [kw for kw in matched_keywords if " " in kw]
        confidence += len(exact_phrases) * 5
        
        # Deduplicate keywords
        matched_keywords = list(set(matched_keywords))
        
        # If keywords matched, add base score. If not, fallback to General Compliance.
        if matched_keywords:
            confidence += 50
        else:
            confidence = 30
            department = "Compliance Department"
        
        # Cap confidence at 100
        confidence = min(100, confidence)
            
        return {
            "department": department,
            "confidence_score": confidence,
            "matched_keywords": matched_keywords[:5]  # Limit to top 5 matches
        }
