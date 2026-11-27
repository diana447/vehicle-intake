from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    ENVIRONMENT: str
    DATABASE_URL: str
    JWT_SECRET: str
    ACCOUNTING_URL: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
