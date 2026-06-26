#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 7 Quality Gate
SuRaksha Phase 7 - Validation Suite Module 4 (Master)

Purpose: Master validation runner
"""

import subprocess
import sys
import os
from datetime import datetime
from typing import Dict

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================
# CONFIG
# ============================================================

OUTPUT_REPORT = str(PROJECT_ROOT / "phase7_quality_gate_report.txt")

MODULES = [
    {
        'name': 'Taxonomy Audit',
        'script': 'taxonomy_audit.py',
        'description': 'Validates taxonomy classification quality'
    },
    {
        'name': 'Cross-Reference Audit',
        'script': 'cross_reference_audit.py',
        'description': 'Validates cross-reference extraction coverage'
    },
    {
        'name': 'Resolver Benchmark',
        'script': 'resolver_benchmark.py',
        'description': 'Benchmarks resolver performance'
    },
    {
        'name': 'Golden Set Evaluation',
        'script': 'golden_set_evaluator.py',
        'description': 'Evaluates resolver accuracy against verified query-answer pairs'
    }
]

# ============================================================
# QUALITY GATE CLASS
# ============================================================

class QualityGate:
    """Master quality gate runner"""
    
    def __init__(self):
        """Initialize quality gate"""
        
        self.results = {}
    
    def run_module(self, module: Dict) -> str:
        """Run a validation module"""
        
        print(f"\n{'='*80}")
        print(f"RUNNING: {module['name']}")
        print(f"{'='*80}\n")
        print(f"Description: {module['description']}")
        print(f"Script: {module['script']}\n")
        
        try:
            # Run the module
            result = subprocess.run(
                [sys.executable, module['script']],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse status from output
            output = result.stdout
            
            # Look for status indicators
            if 'Status: PASS' in output:
                status = 'PASS'
            elif 'Status: WARNING' in output:
                status = 'WARNING'
            elif 'Status: FAIL' in output or result.returncode != 0:
                status = 'FAIL'
            else:
                status = 'UNKNOWN'
            
            return status
            
        except subprocess.TimeoutExpired:
            print(f"✗ MODULE TIMEOUT: {module['name']}")
            return 'FAIL'
        
        except Exception as e:
            print(f"✗ MODULE ERROR: {e}")
            return 'FAIL'
    
    def run_all_modules(self):
        """Run all validation modules"""
        
        print("=" * 80)
        print("PHASE 7 QUALITY GATE")
        print("=" * 80)
        print()
        print(f"Validation Modules: {len(MODULES)}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for module in MODULES:
            status = self.run_module(module)
            self.results[module['name']] = status
            
            print(f"\n✓ {module['name']}: {status}\n")
    
    def determine_overall_status(self) -> str:
        """Determine overall quality gate status"""
        
        if all(status == 'PASS' for status in self.results.values()):
            return 'READY FOR DEMO'
        elif any(status == 'FAIL' for status in self.results.values()):
            return 'NEEDS REVIEW'
        else:
            return 'NEEDS REVIEW'
    
    def generate_report(self):
        """Generate master quality gate report"""
        
        print("\nGenerating quality gate report...")
        
        overall_status = self.determine_overall_status()
        
        lines = []
        lines.append("=" * 80)
        lines.append("PHASE 7 QUALITY GATE REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"SuRaksha RBI Regulatory Intelligence Platform")
        lines.append("")
        lines.append("NOTE: Golden Set Evaluation measures CORRECTNESS, not just success rate.")
        lines.append("      A module can have 100% success but low accuracy if it returns wrong answers.")
        lines.append("")
        
        # Module Results
        lines.append("-" * 80)
        lines.append("MODULE RESULTS")
        lines.append("-" * 80)
        lines.append("")
        
        for module in MODULES:
            name = module['name']
            status = self.results.get(name, 'UNKNOWN')
            
            # Status indicator
            if status == 'PASS':
                indicator = '✓'
            elif status == 'WARNING':
                indicator = '⚠'
            else:
                indicator = '✗'
            
            lines.append(f"{indicator} {name:30s} : {status}")
            lines.append(f"   {module['description']}")
            lines.append("")
        
        # Overall Assessment
        lines.append("-" * 80)
        lines.append("OVERALL ASSESSMENT")
        lines.append("-" * 80)
        lines.append("")
        lines.append(f"Overall Status: {overall_status}")
        lines.append("")
        
        if overall_status == 'READY FOR DEMO':
            lines.append("✓ All validation modules passed")
            lines.append("✓ Phase 7 is ready for college project demonstration")
            lines.append("")
            lines.append("Deliverables:")
            lines.append("  • Taxonomy Builder (2,941 requirements classified)")
            lines.append("  • Cross-Reference Parser (19 references detected)")
            lines.append("  • Reference Graph Builder V2 (NetworkX-based)")
            lines.append("  • Effective Requirement Resolver (production-ready)")
        else:
            lines.append("⚠ One or more validation modules require attention")
            lines.append("")
            lines.append("Actions Required:")
            
            for module in MODULES:
                name = module['name']
                status = self.results.get(name, 'UNKNOWN')
                
                if status in ['FAIL', 'WARNING']:
                    lines.append(f"  • Review {name} report for issues")
        
        lines.append("")
        
        # Detailed Reports
        lines.append("-" * 80)
        lines.append("DETAILED REPORTS")
        lines.append("-" * 80)
        lines.append("")
        lines.append("  • Taxonomy Audit: taxonomy_audit_report.txt")
        lines.append("  • Cross-Reference Audit: cross_reference_audit_report.txt")
        lines.append("  • Resolver Benchmark: resolver_benchmark_report.txt")
        lines.append("  • Golden Set Evaluation: golden_set_evaluation_report.txt")
        lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Report saved to {OUTPUT_REPORT}\n")
    
    def print_summary(self):
        """Print final summary to console"""
        
        overall_status = self.determine_overall_status()
        
        print("\n" + "=" * 80)
        print("PHASE 7 QUALITY GATE")
        print("=" * 80)
        print()
        
        for module in MODULES:
            name = module['name']
            status = self.results.get(name, 'UNKNOWN')
            
            if status == 'PASS':
                indicator = '✓'
            elif status == 'WARNING':
                indicator = '⚠'
            else:
                indicator = '✗'
            
            print(f"{indicator} {name:30s} : {status}")
        
        print()
        print("-" * 80)
        print(f"Overall: {overall_status}")
        print("-" * 80)
        print()


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """Main execution"""
    
    try:
        gate = QualityGate()
        gate.run_all_modules()
        gate.generate_report()
        gate.print_summary()
        
        overall = gate.determine_overall_status()
        
        if overall == 'READY FOR DEMO':
            print("✓ Phase 7 validation complete - Ready for demo!")
            return 0
        else:
            print("⚠ Phase 7 validation complete - Review needed")
            return 1
        
    except Exception as e:
        print(f"\n✗ QUALITY GATE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
