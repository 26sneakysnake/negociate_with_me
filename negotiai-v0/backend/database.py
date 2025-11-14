# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings
import os

settings = get_settings()

# Get DATABASE_URL from environment or settings
# Use SQLite as fallback if PostgreSQL is not available
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./negotiai.db")

# Create engine
# Add check_same_thread=False for SQLite compatibility
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
