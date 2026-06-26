import json
import os
from collections import Counter
from deadline_tracker import DeadlineTracker

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent


class MapDashboardFeed:
    """
    Generates enhanced dashboard metrics from the maps_output.json.
    """
    
    def __init__(self, maps_file: str, output_dir: str):
        self.maps_file = maps_file
        self.output_dir = output_dir

    def generate_feed(self):
        print("=" * 80)
        print("DASHBOARD FEED GENERATOR (ENHANCED)")
        print("=" * 80)
        
        with open(self.maps_file, 'r', encoding='utf-8') as f:
            maps = json.load(f)
            
        total_maps = len(maps)
        critical_maps = sum(1 for m in maps if m.get("priority") == "Critical")
        high_maps = sum(1 for m in maps if m.get("priority") == "High")
        
        departments = set(m.get("department") for m in maps)
        departments_impacted = len(departments)
        
        upcoming_deadlines = sum(1 for m in maps if m.get("deadline") != "TBD")
        
        dept_risk_scores = Counter()
        for m in maps:
            dept_risk_scores[m.get("department")] += m.get("impact_score", 0)
            
        top_risk_department = dept_risk_scores.most_common(1)[0][0] if dept_risk_scores else "None"

        # Top critical MAPs for dashboard table
        top_critical_maps = [
            {
                "map_id": m["map_id"], 
                "task_title": m["task_title"], 
                "department": m["department"],
                "impact_score": m["impact_score"],
                "deadline": m["deadline"]
            }
            for m in sorted(maps, key=lambda x: x["impact_score"], reverse=True)[:10]
        ]
        
        # Compliance Summary status counts
        compliance_summary = {
            "pending_tasks": sum(1 for m in maps if m.get("status") == "Pending"),
            "in_progress_tasks": sum(1 for m in maps if m.get("status") == "In Progress"),
            "completed_tasks": sum(1 for m in maps if m.get("status") == "Completed"),
            "overdue_tasks": sum(1 for m in maps if DeadlineTracker.determine_urgency(m.get("deadline")) == "Overdue")
        }

        dashboard_metrics = {
            "total_maps": total_maps,
            "critical_maps": critical_maps,
            "high_maps": high_maps,
            "departments_impacted": departments_impacted,
            "upcoming_deadlines": upcoming_deadlines,
            "top_risk_department": top_risk_department,
            "department_risk_scores": dict(dept_risk_scores),
            "top_critical_maps": top_critical_maps,
            "compliance_summary": compliance_summary
        }

        output_file = os.path.join(self.output_dir, "dashboard_metrics.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_metrics, f, indent=2)
            
        print(f"Generated Enhanced Dashboard Metrics:")
        # Print a condensed version to avoid terminal spam
        condensed_output = dict(dashboard_metrics)
        condensed_output["top_critical_maps"] = f"[{len(top_critical_maps)} records hidden for brevity]"
        print(json.dumps(condensed_output, indent=2))
        print(f"Saved to {output_file}")
        print("=" * 80)

if __name__ == "__main__":
    feed = MapDashboardFeed(
        maps_file=str(PROJECT_ROOT / "maps/maps_output.json"),
        output_dir=str(PROJECT_ROOT / "maps")
    )
    feed.generate_feed()
