#!/usr/bin/env python3
"""Test if ElevenLabs import works correctly"""

import sys
import traceback

print("Testing ElevenLabs import...")

try:
    print("1. Testing basic elevenlabs import...")
    import elevenlabs
    print(f"   ✓ elevenlabs version: {elevenlabs.__version__}")

    print("2. Testing ElevenLabs client import...")
    from elevenlabs.client import ElevenLabs
    print("   ✓ ElevenLabs client imported successfully")

    print("3. Testing PhoneCallHandler import...")
    from calls.phone_handler import PhoneCallHandler
    print("   ✓ PhoneCallHandler imported successfully")

    print("\n✅ All ElevenLabs imports successful!")

except Exception as e:
    print(f"\n❌ Import failed!")
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
