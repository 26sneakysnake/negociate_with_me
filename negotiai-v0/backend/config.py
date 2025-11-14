# backend/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    MISTRAL_API_KEY: str
    QDRANT_URL: str = "https://your-cluster.qdrant.io"
    QDRANT_API_KEY: str
    ELEVENLABS_API_KEY: str

    # App Config
    APP_NAME: str = "NegotiAI v0"
    DEBUG: bool = True
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Mistral Config
    MISTRAL_MODEL: str = "mistral-large-latest"

    # Qdrant Config
    QDRANT_COLLECTION: str = "negotiation_tactics"
    VECTOR_SIZE: int = 1024

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
