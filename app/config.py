from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    groq_api_key: str = "test-key"
    database_url: str = "sqlite:///./journal.db"
    # llama-3.3-70b-versatile is free on Groq's free tier
    groq_model: str = "llama-3.3-70b-versatile"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
