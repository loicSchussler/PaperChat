from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Mammouth AI API (compatible OpenAI)
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str = "https://api.mammouth.ai/v1"
    OPENAI_CHAT_MODEL: str = "gpt-4.1-nano"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # App
    APP_NAME: str = "PaperChat RAG"
    DEBUG: bool = True

    class Config:
        # Search for .env at the project root (2 levels above this file)
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
