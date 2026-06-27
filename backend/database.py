"""
Database configuration and session management
SQLite-based offline database
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database file location
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'compliance.db')}"

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """
    Dependency function to get database session
    Usage: def route(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
