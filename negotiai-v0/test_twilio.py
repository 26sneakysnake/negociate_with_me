"""
Test script to verify Twilio + ElevenLabs configuration
Run this to test phone calls without going through the full flow
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twilio_config():
    """Test Twilio configuration"""

    print("\n" + "="*70)
    print("🧪 TESTING TWILIO CONFIGURATION")
    print("="*70 + "\n")

    # Get credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    public_url = os.getenv('PUBLIC_URL')

    print("📋 Configuration:")
    print(f"   TWILIO_ACCOUNT_SID: {account_sid[:10]}..." if account_sid else "   ❌ MISSING")
    print(f"   TWILIO_AUTH_TOKEN: {auth_token[:10]}..." if auth_token else "   ❌ MISSING")
    print(f"   TWILIO_PHONE_NUMBER: {phone_number}")
    print(f"   PUBLIC_URL: {public_url}\n")

    if not account_sid or not auth_token:
        print("❌ Twilio credentials missing!")
        return False

    if 'your_' in account_sid or 'your_' in auth_token:
        print("❌ Twilio credentials are still placeholders!")
        return False

    # Test Twilio connection
    try:
        print("🔌 Testing Twilio connection...")
        client = Client(account_sid, auth_token)

        # Get account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio account connected: {account.friendly_name}")
        print(f"   Status: {account.status}")

        return True

    except Exception as e:
        print(f"❌ Twilio connection failed: {e}")
        return False


def test_phone_call(to_number: str):
    """Test sending a real phone call"""

    print("\n" + "="*70)
    print("📞 TESTING PHONE CALL")
    print("="*70 + "\n")

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    public_url = os.getenv('PUBLIC_URL')

    if not all([account_sid, auth_token, from_number]):
        print("❌ Missing Twilio configuration")
        return

    # Remove trailing slash from public_url
    if public_url and public_url.endswith('/'):
        public_url = public_url[:-1]

    print(f"📱 Calling {to_number} from {from_number}...")
    print(f"   TwiML URL: {public_url}/api/call/twiml/test_agent\n")

    try:
        client = Client(account_sid, auth_token)

        # Create call
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url=f"{public_url}/api/call/twiml/test_agent",
            status_callback=f"{public_url}/api/call/status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            status_callback_method='POST'
        )

        print(f"✅ Call initiated!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   Direction: {call.direction}")
        print(f"\n⏳ Waiting for call to connect...")
        print(f"   You should receive the call in ~10 seconds")
        print(f"   Note: First call may ask for TwiML at {public_url}/api/call/twiml/test_agent")

        return call.sid

    except Exception as e:
        print(f"❌ Call failed: {e}")
        print(f"\nPossible issues:")
        print(f"   - Phone number format incorrect (should be +33... or +1...)")
        print(f"   - Twilio account in trial mode (needs verified numbers)")
        print(f"   - PUBLIC_URL not accessible from internet")
        return None


if __name__ == "__main__":
    import sys

    # Test configuration
    config_ok = test_twilio_config()

    if not config_ok:
        print("\n❌ Configuration test failed. Fix the issues above and try again.\n")
        sys.exit(1)

    # Test phone call if number provided
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
        test_phone_call(phone_number)
    else:
        print("\n" + "="*70)
        print("✅ CONFIGURATION TEST PASSED")
        print("="*70)
        print("\nTo test a phone call, run:")
        print(f"   python test_twilio.py +33612345678")
        print("\n")
