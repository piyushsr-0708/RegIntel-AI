#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golden Set Evaluator
SuRaksha Phase 7 - Final Validation

Purpose: Evaluate resolver accuracy against manually verified query-requirement pairs
Metrics: Top-1, Top-3, Top-5 accuracy
"""

import json
import time
from datetime import datetime
from typing import Dict, List
from effective_requirement_resolver import EffectiveRequirementResolver

# ============================================================
# CONFIG
# ============================================================

GOLDEN_QUERIES_FILE = "golden_queries.json"
OUTPUT_REPORT = "golden_set_evaluation_report.txt"
OUTPUT_RESULTS = "golden_set_evaluation_results.json"

# ============================================================
# EVALUATOR CLASS
# ============================================================

class GoldenSetEvaluator:
    """Evaluate resolver against golden set"""
    
    def __init__(self):
        """Initialize evaluator"""
        
        print("="*80)
        print("GOLDEN SET EVALUATOR - PHASE 7 FINAL VALIDATION")
        print("="*80)
        print()
        
        # Load golden queries
        print("Loading golden queries...")
        with open(GOLDEN_QUERIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.golden_queries = data['golden_queries']
            self.metadata = data['metadata']
        
        print(f"  Loaded {len(self.golden_queries)} golden queries")
        print(f"  Domains covered: {', '.join(self.metadata['domains_covered'])}")
        print()
        
        # Initialize resolver
        print("Initializing Effective Requirement Resolver...")
        self.resolver = EffectiveRequirementResolver()
        print()
        
        self.results = []
    
    def evaluate_query(self, golden: Dict) -> Dict:
        """Evaluate single query"""
        
        query = golden['query']
        expected_req_id = golden['expected_requirement']
        
        print(f"  Query {golden['query_id']}: {query}")
        print(f"    Expected: {expected_req_id}")
        
        start = time.time()
        
        try:
            # Get top 5 results
            result = self.resolver.resolve(query, top_k=5)
            response_time = time.time() - start
            
            # Extract requirement IDs from top 5
            # The resolver returns 'effective_requirement' (top 1) and 'supporting_requirements' (rest)
            top_5_ids = []
            
            if result.get('effective_requirement'):
                top_5_ids.append(result['effective_requirement']['requirement_id'])
            
            if result.get('supporting_requirements'):
                for req in result['supporting_requirements'][:4]:  # Get up to 4 more
                    top_5_ids.append(req['requirement_id'])
            
            # Check accuracy
            top_1_match = top_5_ids[0] == expected_req_id if len(top_5_ids) >= 1 else False
            top_3_match = expected_req_id in top_5_ids[:3] if len(top_5_ids) >= 3 else False
            top_5_match = expected_req_id in top_5_ids if len(top_5_ids) >= 5 else False
            
            # Find position of expected requirement
            if expected_req_id in top_5_ids:
                position = top_5_ids.index(expected_req_id) + 1
            else:
                position = None
            
            print(f"    Returned: {top_5_ids[0] if top_5_ids else 'NONE'}")
            print(f"    Top-1: {'[OK]' if top_1_match else 'MISS'} | Top-3: {'[OK]' if top_3_match else 'MISS'} | Top-5: {'[OK]' if top_5_match else 'MISS'}")
            if position:
                print(f"    Position: {position}")
            print()
            
            return {
                'query_id': golden['query_id'],
                'query': query,
                'expected_requirement': expected_req_id,
                'top_5_returned': top_5_ids,
                'top_1_match': top_1_match,
                'top_3_match': top_3_match,
                'top_5_match': top_5_match,
                'position': position,
                'response_time': round(response_time, 3),
                'domain': golden['domain'],
                'subdomain': golden['subdomain']
            }
        
        except Exception as e:
            print(f"    ERROR: {str(e)}\n")
            return {
                'query_id': golden['query_id'],
                'query': query,
                'expected_requirement': expected_req_id,
                'top_5_returned': [],
                'top_1_match': False,
                'top_3_match': False,
                'top_5_match': False,
                'position': None,
                'response_time': None,
                'error': str(e),
                'domain': golden['domain'],
                'subdomain': golden['subdomain']
            }
    
    def run_evaluation(self):
        """Run evaluation on all golden queries"""
        
        print("="*80)
        print("EVALUATING GOLDEN SET")
        print("="*80)
        print()
        
        for golden in self.golden_queries:
            result = self.evaluate_query(golden)
            self.results.append(result)
    
    def calculate_metrics(self) -> Dict:
        """Calculate accuracy metrics"""
        
        print("="*80)
        print("CALCULATING METRICS")
        print("="*80)
        print()
        
        total = len(self.results)
        
        top_1_correct = sum(1 for r in self.results if r['top_1_match'])
        top_3_correct = sum(1 for r in self.results if r['top_3_match'])
        top_5_correct = sum(1 for r in self.results if r['top_5_match'])
        
        top_1_accuracy = (top_1_correct / total * 100) if total > 0 else 0
        top_3_accuracy = (top_3_correct / total * 100) if total > 0 else 0
        top_5_accuracy = (top_5_correct / total * 100) if total > 0 else 0
        
        # Response times
        response_times = [r['response_time'] for r in self.results if r.get('response_time')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Domain-wise accuracy
        domain_accuracy = {}
        for domain in set(r['domain'] for r in self.results):
            domain_results = [r for r in self.results if r['domain'] == domain]
            domain_top_1 = sum(1 for r in domain_results if r['top_1_match'])
            domain_accuracy[domain] = {
                'total': len(domain_results),
                'top_1_correct': domain_top_1,
                'accuracy': (domain_top_1 / len(domain_results) * 100) if domain_results else 0
            }
        
        # Position distribution
        positions = [r['position'] for r in self.results if r.get('position')]
        position_dist = {i: positions.count(i) for i in range(1, 6)}
        
        metrics = {
            'total_queries': total,
            'top_1_correct': top_1_correct,
            'top_3_correct': top_3_correct,
            'top_5_correct': top_5_correct,
            'top_1_accuracy': round(top_1_accuracy, 2),
            'top_3_accuracy': round(top_3_accuracy, 2),
            'top_5_accuracy': round(top_5_accuracy, 2),
            'average_response_time': round(avg_response_time, 3),
            'domain_accuracy': domain_accuracy,
            'position_distribution': position_dist
        }
        
        print(f"  Top-1 Accuracy: {top_1_accuracy:.2f}% ({top_1_correct}/{total})")
        print(f"  Top-3 Accuracy: {top_3_accuracy:.2f}% ({top_3_correct}/{total})")
        print(f"  Top-5 Accuracy: {top_5_accuracy:.2f}% ({top_5_correct}/{total})")
        print(f"  Avg Response Time: {avg_response_time:.3f}s")
        print()
        
        return metrics
    
    def generate_report(self, metrics: Dict):
        """Generate evaluation report"""
        
        print("="*80)
        print("GENERATING REPORT")
        print("="*80)
        print()
        
        lines = []
        lines.append("="*80)
        lines.append("GOLDEN SET EVALUATION REPORT")
        lines.append("="*80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"SuRaksha RBI Regulatory Intelligence Platform")
        lines.append("")
        
        # Summary
        lines.append("-"*80)
        lines.append("ACCURACY METRICS")
        lines.append("-"*80)
        lines.append("")
        lines.append(f"Total Golden Queries: {metrics['total_queries']}")
        lines.append("")
        lines.append(f"Top-1 Accuracy: {metrics['top_1_accuracy']:.2f}% ({metrics['top_1_correct']}/{metrics['total_queries']})")
        lines.append(f"Top-3 Accuracy: {metrics['top_3_accuracy']:.2f}% ({metrics['top_3_correct']}/{metrics['total_queries']})")
        lines.append(f"Top-5 Accuracy: {metrics['top_5_accuracy']:.2f}% ({metrics['top_5_correct']}/{metrics['total_queries']})")
        lines.append("")
        lines.append(f"Average Response Time: {metrics['average_response_time']:.3f} seconds")
        lines.append("")
        
        # Position distribution
        lines.append("-"*80)
        lines.append("POSITION DISTRIBUTION")
        lines.append("-"*80)
        lines.append("")
        lines.append("Where expected requirement appeared in Top-5:")
        for pos in range(1, 6):
            count = metrics['position_distribution'].get(pos, 0)
            lines.append(f"  Position {pos}: {count} queries")
        lines.append("")
        
        # Domain-wise accuracy
        lines.append("-"*80)
        lines.append("DOMAIN-WISE ACCURACY")
        lines.append("-"*80)
        lines.append("")
        for domain, stats in sorted(metrics['domain_accuracy'].items(), 
                                    key=lambda x: x[1]['accuracy'], reverse=True):
            lines.append(f"{domain:20s}: {stats['accuracy']:5.1f}% ({stats['top_1_correct']}/{stats['total']})")
        lines.append("")
        
        # Detailed results
        lines.append("-"*80)
        lines.append("DETAILED RESULTS")
        lines.append("-"*80)
        lines.append("")
        
        for result in self.results:
            lines.append(f"{result['query_id']}. Query: {result['query']}")
            lines.append(f"   Domain: {result['domain']}/{result['subdomain']}")
            lines.append(f"   Expected: {result['expected_requirement']}")
            
            if result['top_5_returned']:
                lines.append(f"   Returned: {result['top_5_returned'][0]}")
                lines.append(f"   Top-1: {'[OK]' if result['top_1_match'] else 'MISS'} | "
                           f"Top-3: {'[OK]' if result['top_3_match'] else 'MISS'} | "
                           f"Top-5: {'[OK]' if result['top_5_match'] else 'MISS'}")
                
                if result.get('position'):
                    lines.append(f"   Position: {result['position']}")
            else:
                lines.append(f"   ERROR: {result.get('error', 'No results returned')}")
            
            lines.append("")
        
        # Assessment
        lines.append("-"*80)
        lines.append("QUALITY ASSESSMENT")
        lines.append("-"*80)
        lines.append("")
        
        top_1_acc = metrics['top_1_accuracy']
        top_3_acc = metrics['top_3_accuracy']
        
        # Production-ready thresholds
        if top_1_acc >= 70 and top_3_acc >= 85:
            status = "EXCELLENT"
            message = "Resolver demonstrates high accuracy - production ready"
        elif top_1_acc >= 50 and top_3_acc >= 70:
            status = "GOOD"
            message = "Resolver demonstrates acceptable accuracy - suitable for deployment"
        elif top_1_acc >= 30 and top_3_acc >= 50:
            status = "ACCEPTABLE"
            message = "Resolver demonstrates moderate accuracy - needs improvement"
        else:
            status = "NEEDS IMPROVEMENT"
            message = "Resolver accuracy below acceptable thresholds"
        
        lines.append(f"Status: {status}")
        lines.append(f"Assessment: {message}")
        lines.append("")
        lines.append("Benchmark Thresholds:")
        lines.append("  EXCELLENT:        Top-1 >= 70%, Top-3 >= 85%")
        lines.append("  GOOD:             Top-1 >= 50%, Top-3 >= 70%")
        lines.append("  ACCEPTABLE:       Top-1 >= 30%, Top-3 >= 50%")
        lines.append("  NEEDS IMPROVEMENT: Below acceptable thresholds")
        lines.append("")
        
        lines.append("="*80)
        lines.append("END OF REPORT")
        lines.append("="*80)
        
        # Save report
        with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"  Report saved to {OUTPUT_REPORT}")
        print()
        
        return status
    
    def save_results(self):
        """Save detailed results to JSON"""
        
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_queries": len(self.results)
            },
            "results": self.results
        }
        
        with open(OUTPUT_RESULTS, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  Results saved to {OUTPUT_RESULTS}")
        print()


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """Main execution"""
    
    try:
        evaluator = GoldenSetEvaluator()
        evaluator.run_evaluation()
        metrics = evaluator.calculate_metrics()
        status = evaluator.generate_report(metrics)
        evaluator.save_results()
        
        print("="*80)
        print(f"EVALUATION COMPLETE - Status: {status}")
        print("="*80)
        print()
        print(f"Top-1 Accuracy: {metrics['top_1_accuracy']:.2f}%")
        print(f"Top-3 Accuracy: {metrics['top_3_accuracy']:.2f}%")
        print(f"Top-5 Accuracy: {metrics['top_5_accuracy']:.2f}%")
        print()
        print(f"Report: {OUTPUT_REPORT}")
        print(f"Results: {OUTPUT_RESULTS}")
        
        return 0 if status in ["EXCELLENT", "GOOD", "ACCEPTABLE"] else 1
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
