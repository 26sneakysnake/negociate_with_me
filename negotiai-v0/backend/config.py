# backend/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import field_validator

class Settings(BaseSettings):
    # API Keys
    MISTRAL_API_KEY: str
    QDRANT_URL: str = "https://your-cluster.qdrant.io"
    QDRANT_API_KEY: str
    ELEVENLABS_API_KEY: str

    # ElevenLabs Phone Number ID (get from ElevenLabs dashboard)
    ELEVENLABS_AGENT_PHONE_NUMBER_ID: str = ""

    # App Config
    APP_NAME: str = "NegotiAI v0"
    DEBUG: bool = True
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Mistral Config
    MISTRAL_MODEL: str = "mistral-large-latest"

    # Qdrant Config
    QDRANT_COLLECTION: str = "negotiation_tactics"
    VECTOR_SIZE: int = 1024

    @field_validator('MISTRAL_API_KEY', 'QDRANT_API_KEY', 'ELEVENLABS_API_KEY', mode='before')
    @classmethod
    def validate_api_keys(cls, v: str, info) -> str:
        # Allow app to start even with placeholder keys - services will just be unavailable
        if not v or 'your_' in v.lower() or '_here' in v.lower():
            print(
                f"\n⚠️ WARNING: {info.field_name} is not configured!\n"
                f"   The service will be unavailable. Edit .env to add a real API key.\n"
            )
            return v  # Return the value anyway to allow startup
        return v

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    try:
        return Settings()
    except Exception as e:
        print("\n" + "="*70)
        print("⚠️  CONFIGURATION ERROR")
        print("="*70)
        print(str(e))
        print("\nPlease update your .env file with real API keys:")
        print("  - MISTRAL_API_KEY from https://console.mistral.ai/")
        print("  - QDRANT_URL and QDRANT_API_KEY from https://cloud.qdrant.io/")
        print("  - ELEVENLABS_API_KEY from https://elevenlabs.io/")
        print("="*70 + "\n")
        raise
