from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/prices"
    redis_url: str = "redis://localhost:6379/0"
    deribit_base_url: str = "https://www.deribit.com/api/v2"
    request_timeout: float = 10.0
    collection_interval_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Config:
    return Config()