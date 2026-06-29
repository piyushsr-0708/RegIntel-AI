#!/usr/bin/env python
"""Database audit script for Executive Dashboard consistency check"""

from database import SessionLocal
from models import Assignment, Requirement, Department
from sqlalchemy import func

db = SessionLocal()

print("=" * 60)
print("DATABASE AUDIT - EXECUTIVE DASHBOARD CONSISTENCY CHECK")
print("=" * 60)

print("\n=== ASSIGNMENTS TABLE ===")
total_assignments = db.query(Assignment).count()
print(f"Total Assignments: {total_assignments}")

published = db.query(Assignment).filter(Assignment.is_published == True).count()
print(f"  Published (is_published=True): {published}")

unpublished = db.query(Assignment).filter(Assignment.is_published == False).count()
print(f"  Unpublished (is_published=False): {unpublished}")
print(f"  Verification: {published} + {unpublished} = {published + unpublished} (should equal {total_assignments})")

print("\n=== ASSIGNMENT STATUS ===")
pending = db.query(Assignment).filter(Assignment.status == 'pending').count()
print(f"  Pending: {pending}")

in_progress = db.query(Assignment).filter(Assignment.status == 'in_progress').count()
print(f"  In Progress: {in_progress}")

completed = db.query(Assignment).filter(Assignment.status == 'completed').count()
print(f"  Completed: {completed}")
print(f"  Verification: {pending} + {in_progress} + {completed} = {pending + in_progress + completed} (should equal {total_assignments})")

print("\n=== PUBLISHED ASSIGNMENTS STATUS ===")
published_pending = db.query(Assignment).filter(
    Assignment.is_published == True,
    Assignment.status == 'pending'
).count()
print(f"  Published + Pending: {published_pending}")

published_completed = db.query(Assignment).filter(
    Assignment.is_published == True,
    Assignment.status == 'completed'
).count()
print(f"  Published + Completed: {published_completed}")
print(f"  Published + Remaining: {published_pending}")

print("\n=== DEPARTMENTS ===")
dept_count = db.query(Department).count()
print(f"Total Departments: {dept_count}")

dept_with_published = db.query(func.count(func.distinct(Assignment.department_id))).filter(
    Assignment.is_published == True
).scalar()
print(f"Departments with Published Assignments: {dept_with_published}")

dept_with_any = db.query(func.count(func.distinct(Assignment.department_id))).scalar()
print(f"Departments with Any Assignments: {dept_with_any}")

print("\n=== PRIORITY DISTRIBUTION (ALL ASSIGNMENTS) ===")
# Get priorities from Assignment.priority or fallback to Requirement.priority
assignments_with_reqs = db.query(Assignment, Requirement).outerjoin(Requirement).all()
priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

for a, r in assignments_with_reqs:
    p = a.priority if a.priority else (r.priority if r else "Medium")
    if p in priority_counts:
        priority_counts[p] += 1
    else:
        priority_counts["Medium"] += 1  # Default to Medium

print(f"  Critical: {priority_counts['Critical']}")
print(f"  High: {priority_counts['High']}")
print(f"  Medium: {priority_counts['Medium']}")
print(f"  Low: {priority_counts['Low']}")
total_priority = sum(priority_counts.values())
print(f"  Total: {total_priority} (should equal {total_assignments})")

print("\n=== DEADLINES ===")
assignments_with_due_date = db.query(Assignment).filter(Assignment.due_date != None).count()
print(f"Assignments with due_date field: {assignments_with_due_date}")

requirements_with_deadline = db.query(Requirement).filter(Requirement.deadline != None).count()
print(f"Requirements with deadline field: {requirements_with_deadline}")

print("\n=== DEPARTMENT BREAKDOWN ===")
departments = db.query(Department).all()
for dept in departments:
    total = db.query(Assignment).filter(Assignment.department_id == dept.id).count()
    published_dept = db.query(Assignment).filter(
        Assignment.department_id == dept.id,
        Assignment.is_published == True
    ).count()
    completed_dept = db.query(Assignment).filter(
        Assignment.department_id == dept.id,
        Assignment.status == 'completed'
    ).count()
    
    if total > 0:
        print(f"\n  {dept.name} (ID: {dept.id}):")
        print(f"    Total: {total}")
        print(f"    Published: {published_dept}")
        print(f"    Completed: {completed_dept}")
        print(f"    Remaining: {published_dept - completed_dept}")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)

db.close()
