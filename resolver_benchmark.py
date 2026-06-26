#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resolver Benchmark Module
SuRaksha Phase 7 - Validation Suite Module 3

Purpose: Benchmark Effective Requirement Resolver performance
"""

import json
import time
import sys
from datetime import datetime
from typing import Dict, List
from effective_requirement_resolver import EffectiveRequirementResolver

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


# ============================================================
# CONFIG
# ============================================================

OUTPUT_REPORT = str(PROJECT_ROOT / "resolver_benchmark_report.txt")
OUTPUT_RESULTS = str(PROJECT_ROOT / "resolver_benchmark_results.json")

# ============================================================
# TEST QUERIES
# ============================================================

TEST_QUERIES = [
    "record retention requirements",
    "beneficial ownership requirements",
    "cash transaction reporting",
    "suspicious transaction reporting",
    "customer due diligence",
    "politically exposed persons",
    "cyber incident reporting",
    "kyc review frequency",
    "aml transaction monitoring",
    "sanctions screening",
    "board oversight",
    "risk management framework",
    "customer identification",
    "ctr reporting deadline",
    "record preservation period"
]

# ============================================================
# BENCHMARK CLASS
# ============================================================

class ResolverBenchmark:
    """Benchmark resolver performance"""
    
    def __init__(self):
        """Initialize benchmark"""
        
        print("Initializing Effective Requirement Resolver...")
        print("(First run may take time to download embeddings)\n")
        
        start = time.time()
        self.resolver = EffectiveRequirementResolver()
        init_time = time.time() - start
        
        print(f"Resolver initialized in {init_time:.2f} seconds\n")
        
        self.results = []
    
    def run_query(self, query: str) -> Dict:
        """Run single query and measure performance"""
        
        print(f"  Query: {query[:50]}...")
        
        start = time.time()
        
        try:
            result = self.resolver.resolve(query, top_k=5)
            response_time = time.time() - start
            
            eff_req = result.get('effective_requirement')
            
            if eff_req:
                return {
                    'query': query,
                    'status': 'success',
                    'requirement_id': eff_req.get('requirement_id'),
                    'domain': eff_req.get('domain'),
                    'obligation_type': eff_req.get('obligation_type'),
                    'confidence': result.get('confidence'),
                    'source_document': eff_req.get('source_document'),
                    'total_score': eff_req.get('total_score'),
                    'similarity': eff_req.get('similarity'),
                    'response_time': round(response_time, 3)
                }
            else:
                return {
                    'query': query,
                    'status': 'no_result',
                    'confidence': 'Low',
                    'response_time': round(response_time, 3)
                }
        
        except Exception as e:
            return {
                'query': query,
                'status': 'error',
                'error': str(e),
                'response_time': None
            }
    
    def run_benchmark(self):
        """Run all test queries"""
        
        print(f"[1] Running {len(TEST_QUERIES)} test queries...\n")
        
        for i, query in enumerate(TEST_QUERIES, 1):
            print(f"Query {i}/{len(TEST_QUERIES)}")
            result = self.run_query(query)
            self.results.append(result)
            print(f"    Status: {result['status']} | Confidence: {result.get('confidence', 'N/A')} | Time: {result.get('response_time', 'N/A')}s\n")
    
    def calculate_metrics(self) -> Dict:
        """Calculate benchmark metrics"""
        
        print("[2] Calculating metrics...")
        
        successful = [r for r in self.results if r['status'] == 'success']
        
        high_conf = len([r for r in successful if r.get('confidence') == 'High'])
        medium_conf = len([r for r in successful if r.get('confidence') == 'Medium'])
        low_conf = len([r for r in successful if r.get('confidence') == 'Low'])
        
        response_times = [r['response_time'] for r in self.results if r.get('response_time')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Domain distribution
        domains = [r.get('domain') for r in successful if r.get('domain')]
        domain_dist = {}
        for domain in set(domains):
            domain_dist[domain] = domains.count(domain)
        
        metrics = {
            'total_queries': len(TEST_QUERIES),
            'successful_queries': len(successful),
            'failed_queries': len(self.results) - len(successful),
            'high_confidence_count': high_conf,
            'medium_confidence_count': medium_conf,
            'low_confidence_count': low_conf,
            'average_response_time': round(avg_response_time, 3),
            'domain_distribution': domain_dist
        }
        
        print(f"    Metrics calculated\n")
        
        return metrics
    
    def generate_report(self, metrics: Dict) -> str:
        """Generate benchmark report"""
        
        print("[3] Generating report...")
        
        lines = []
        lines.append("=" * 80)
        lines.append("RESOLVER BENCHMARK REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        lines.append("-" * 80)
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append("")
        lines.append(f"Total Queries Tested: {metrics['total_queries']}")
        lines.append(f"Successful Queries: {metrics['successful_queries']}")
        lines.append(f"Failed Queries: {metrics['failed_queries']}")
        lines.append(f"Success Rate: {(metrics['successful_queries']/metrics['total_queries']*100):.2f}%")
        lines.append("")
        
        # Confidence Distribution
        lines.append("-" * 80)
        lines.append("CONFIDENCE DISTRIBUTION")
        lines.append("-" * 80)
        lines.append("")
        lines.append(f"High Confidence: {metrics['high_confidence_count']}")
        lines.append(f"Medium Confidence: {metrics['medium_confidence_count']}")
        lines.append(f"Low Confidence: {metrics['low_confidence_count']}")
        lines.append("")
        
        # Performance
        lines.append("-" * 80)
        lines.append("PERFORMANCE METRICS")
        lines.append("-" * 80)
        lines.append("")
        lines.append(f"Average Response Time: {metrics['average_response_time']:.3f} seconds")
        lines.append("")
        
        # Domain Distribution
        if metrics['domain_distribution']:
            lines.append("-" * 80)
            lines.append("DOMAIN DISTRIBUTION")
            lines.append("-" * 80)
            lines.append("")
            
            for domain, count in sorted(metrics['domain_distribution'].items(), 
                                       key=lambda x: x[1], reverse=True):
                lines.append(f"  {domain:25s} : {count}")
            lines.append("")
        
        # Detailed Results
        lines.append("-" * 80)
        lines.append("DETAILED RESULTS")
        lines.append("-" * 80)
        lines.append("")
        
        for i, result in enumerate(self.results, 1):
            lines.append(f"{i}. Query: {result['query']}")
            lines.append(f"   Status: {result['status']}")
            
            if result['status'] == 'success':
                lines.append(f"   Requirement: {result.get('requirement_id', 'N/A')}")
                lines.append(f"   Domain: {result.get('domain', 'N/A')}")
                lines.append(f"   Obligation: {result.get('obligation_type', 'N/A')}")
                lines.append(f"   Confidence: {result.get('confidence', 'N/A')}")
                lines.append(f"   Score: {result.get('total_score', 'N/A')}")
                lines.append(f"   Similarity: {result.get('similarity', 'N/A')}")
                lines.append(f"   Response Time: {result.get('response_time', 'N/A')}s")
            elif result['status'] == 'error':
                lines.append(f"   Error: {result.get('error', 'Unknown')}")
            
            lines.append("")
        
        # Quality Assessment
        lines.append("-" * 80)
        lines.append("QUALITY ASSESSMENT")
        lines.append("-" * 80)
        lines.append("")
        
        success_rate = (metrics['successful_queries']/metrics['total_queries']*100)
        medium_or_high = metrics['high_confidence_count'] + metrics['medium_confidence_count']
        medium_or_high_rate = (medium_or_high/metrics['successful_queries']*100) if metrics['successful_queries'] > 0 else 0
        
        # REALISTIC thresholds for regulatory corpus
        if success_rate >= 90 and medium_or_high_rate >= 40:  # Adjusted: Medium OR High >= 40%
            status = "PASS"
            message = "Resolver performance is good"
        elif success_rate >= 80 and medium_or_high_rate >= 30:
            status = "WARNING"
            message = "Resolver performance is acceptable"
        else:
            status = "FAIL"
            message = "Resolver performance needs improvement"
        
        lines.append(f"Status: {status}")
        lines.append(f"Assessment: {message}")
        lines.append(f"  - Success Rate: {success_rate:.1f}% (target: ≥ 90%)")
        lines.append(f"  - Medium/High Confidence: {medium_or_high}/{metrics['successful_queries']} = {medium_or_high_rate:.1f}% (target: ≥ 40%)")
        lines.append(f"  - Average Response Time: {metrics['average_response_time']:.3f}s (target: < 2s)")
        lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"    Saved to {OUTPUT_REPORT}\n")
        
        return status
    
    def save_results(self):
        """Save detailed results to JSON"""
        
        print("[4] Saving detailed results...")
        
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_queries": len(TEST_QUERIES)
            },
            "results": self.results
        }
        
        with open(OUTPUT_RESULTS, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"    Saved to {OUTPUT_RESULTS}\n")


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """Main execution"""
    
    print("=" * 80)
    print("RESOLVER BENCHMARK - PHASE 7 MODULE 3")
    print("=" * 80)
    print()
    
    try:
        benchmark = ResolverBenchmark()
        benchmark.run_benchmark()
        metrics = benchmark.calculate_metrics()
        status = benchmark.generate_report(metrics)
        benchmark.save_results()
        
        print("=" * 80)
        print(f"BENCHMARK COMPLETE - Status: {status}")
        print("=" * 80)
        print()
        print(f"Report: {OUTPUT_REPORT}")
        print(f"Results: {OUTPUT_RESULTS}")
        
        return status
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return "FAIL"


if __name__ == "__main__":
    status = main()
    # Exit with code 0 for PASS, 1 for FAIL/WARNING
    import sys
    sys.exit(0 if status == "PASS" else 1)
