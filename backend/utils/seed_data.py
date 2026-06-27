"""
Seed database with default users and departments
"""
from sqlalchemy.orm import Session
from .. import models, crud, schemas
from ..security import get_password_hash


def seed_departments(db: Session):
    """Create default departments"""
    departments_data = [
        {"name": "Compliance", "code": "COMP", "description": "Compliance Department"},
        {"name": "Risk Management", "code": "RISK", "description": "Risk Management Department"},
        {"name": "Treasury", "code": "TRES", "description": "Treasury Department"},
        {"name": "Operations", "code": "OPS", "description": "Operations Department"},
        {"name": "Cyber Security", "code": "CYBER", "description": "Cyber Security Department"},
        {"name": "IT", "code": "IT", "description": "Information Technology Department"},
        {"name": "Finance", "code": "FIN", "description": "Finance Department"},
        {"name": "AML", "code": "AML", "description": "Anti-Money Laundering Department"},
        {"name": "Legal", "code": "LEGAL", "description": "Legal Department"},
    ]
    
    created_depts = {}
    for dept_data in departments_data:
        # Check if department already exists
        existing = crud.get_department_by_code(db, dept_data["code"])
        if not existing:
            dept = schemas.DepartmentCreate(**dept_data)
            db_dept = crud.create_department(db, dept)
            created_depts[dept_data["code"]] = db_dept
            print(f"* Created department: {dept_data['name']} ({dept_data['code']})")
        else:
            created_depts[dept_data["code"]] = existing
            print(f"  Department already exists: {dept_data['name']}")
    
    return created_depts


def seed_users(db: Session, departments: dict):
    """Create default users"""
    # Create Head Office admin user
    admin_username = "admin"
    existing_admin = crud.get_user_by_username(db, admin_username)
    
    if not existing_admin:
        admin = schemas.UserCreate(
            username=admin_username,
            password="admin123",
            full_name="Head Office Administrator",
            email="admin@regintel.ai",
            role=schemas.UserRole.HEAD_OFFICE,
            department_id=None
        )
        crud.create_user(db, admin)
        print(f"* Created HEAD_OFFICE user: {admin_username} (password: admin123)")
    else:
        print(f"  HEAD_OFFICE user already exists: {admin_username}")
    
    # Create department users
    dept_users = [
        {"username": "compliance", "dept_code": "COMP", "full_name": "Compliance Manager"},
        {"username": "risk", "dept_code": "RISK", "full_name": "Risk Manager"},
        {"username": "treasury", "dept_code": "TRES", "full_name": "Treasury Manager"},
        {"username": "operations", "dept_code": "OPS", "full_name": "Operations Manager"},
        {"username": "cyber", "dept_code": "CYBER", "full_name": "Cyber Security Manager"},
        {"username": "it", "dept_code": "IT", "full_name": "IT Manager"},
        {"username": "finance", "dept_code": "FIN", "full_name": "Finance Manager"},
        {"username": "aml", "dept_code": "AML", "full_name": "AML Manager"},
        {"username": "legal", "dept_code": "LEGAL", "full_name": "Legal Manager"},
    ]
    
    for user_data in dept_users:
        existing_user = crud.get_user_by_username(db, user_data["username"])
        
        if not existing_user:
            dept = departments.get(user_data["dept_code"])
            if dept:
                user = schemas.UserCreate(
                    username=user_data["username"],
                    password=f"{user_data['username']}123",
                    full_name=user_data["full_name"],
                    email=f"{user_data['username']}@regintel.ai",
                    role=schemas.UserRole.DEPARTMENT,
                    department_id=dept.id
                )
                crud.create_user(db, user)
                print(f"* Created DEPARTMENT user: {user_data['username']} (password: {user_data['username']}123)")
        else:
            print(f"  DEPARTMENT user already exists: {user_data['username']}")


def seed_database(db: Session):
    """Main function to seed database with initial data"""
    print("\n" + "="*60)
    print("SEEDING DATABASE WITH DEFAULT DATA")
    print("="*60 + "\n")
    
    print("Creating departments...")
    departments = seed_departments(db)
    
    print("\nCreating users...")
    seed_users(db, departments)
    
    print("\n" + "="*60)
    print("DATABASE SEEDING COMPLETE")
    print("="*60)
    print("\nDEFAULT CREDENTIALS:")
    print("-" * 60)
    print("HEAD OFFICE:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nDEPARTMENTS:")
    print("  Username: compliance, risk, treasury, operations, cyber,")
    print("            it, finance, aml, legal")
    print("  Password: <username>123 (e.g., compliance123)")
    print("-" * 60 + "\n")
