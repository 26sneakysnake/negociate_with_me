#!/usr/bin/env python3
"""Test script to check if all imports work correctly"""

import sys
import traceback

print("Testing imports...")

try:
    print("1. Testing config...")
    from config import get_settings
    print("   ✓ config OK")

    print("2. Testing models...")
    from models import NegotiationContext, Strategy, TranscriptAnalysis, Analysis, Session
    print("   ✓ models OK")

    print("3. Testing database...")
    from database import get_db, Base, engine
    print("   ✓ database OK")

    print("4. Testing crud...")
    import crud
    print("   ✓ crud OK")

    print("5. Testing services...")
    from services.mistral_service import MistralService
    from services.qdrant_service import QdrantService
    from services.elevenlabs_service import ElevenLabsService
    print("   ✓ services OK")

    print("6. Testing routers...")
    from routers import sessions, templates
    print("   ✓ routers OK")

    print("\n✅ All imports successful!")

except Exception as e:
    print(f"\n❌ Import failed!")
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
