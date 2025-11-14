#!/usr/bin/env python3
"""Initialize database tables and load templates"""

import time
import sys
from database import Base, engine
from init_db import load_templates

def init_database(max_retries=5):
    """Initialize database with retry logic"""
    print("🗄️  Initializing database...")

    for attempt in range(max_retries):
        try:
            # Create all tables
            print(f"   Attempt {attempt + 1}/{max_retries}: Creating tables...")
            Base.metadata.create_all(bind=engine)
            print("   ✅ Database tables created successfully!")

            # Load templates
            print("   Loading context templates...")
            load_templates()
            print("   ✅ Templates loaded successfully!")

            return True

        except Exception as e:
            print(f"   ⚠️  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 2s, 4s, 6s, 8s, 10s
                print(f"   Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print("   ❌ Failed to initialize database after all retries")
                return False

    return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
