from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://paperchat:paperchat123@localhost:5432/paperchat_db"

    # Mammouth AI API (compatible OpenAI)
    OPENAI_API_KEY: str = "SECRET_REMOVED"
    OPENAI_API_BASE: str = "https://api.mammouth.ai/v1"

    # App
    APP_NAME: str = "PaperChat RAG"
    DEBUG: bool = True

    class Config:
        # Cherche .env à la racine du projet (2 niveaux au-dessus de ce fichier)
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
