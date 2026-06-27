# Routers package
from . import auth_router, admin_router, department_router, assignment_batch_router
from . import assignment_center_router, department_workspace_router

__all__ = [
    "auth_router", 
    "admin_router", 
    "department_router", 
    "assignment_batch_router",
    "assignment_center_router",
    "department_workspace_router"
]
