# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings
import os

settings = get_settings()

# Get DATABASE_URL from environment or settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://negotiai:negotiai_dev@postgres:5432/negotiai")

# Create engine
engine = create_engine(DATABASE_URL)

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
