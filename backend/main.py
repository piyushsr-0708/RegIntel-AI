"""
FastAPI Main Application
Offline Authentication & Compliance Workflow Backend
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from .routers import auth_router, admin_router, department_router, assignment_batch_router
from .routers import assignment_center_router, department_workspace_router
from .utils.seed_data import seed_database

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="RegIntel AI - Compliance Backend",
    description="Offline Authentication & Compliance Workflow Management System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(department_router.router, prefix="/api")
app.include_router(assignment_batch_router.router, prefix="/api")
app.include_router(assignment_center_router.router, prefix="/api")
app.include_router(department_workspace_router.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "RegIntel AI - Compliance Backend",
        "version": "1.0.0",
        "status": "online",
        "docs": "/api/docs"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "compliance-backend"}


@app.on_event("startup")
def on_startup():
    """
    Startup event - Seed database with default data if needed
    """
    print("\n" + "="*60)
    print("REGINTEL AI - COMPLIANCE BACKEND STARTING")
    print("="*60)
    
    # Create tables if they don't exist
    print("\n* Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Seed database
    db = next(get_db())
    try:
        seed_database(db)
        print("* Database seeding completed successfully")
    except Exception as e:
        print(f"\n⚠️  ERROR during database seeding:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n⚠️  Backend started but database may not be properly seeded!")
    finally:
        db.close()
    
    print("\n* Backend is ready!")
    print("* API Documentation: http://localhost:8000/api/docs")
    print("* Alternative Docs: http://localhost:8000/api/redoc")
    print("="*60 + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
