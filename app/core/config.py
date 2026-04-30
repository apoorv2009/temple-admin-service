from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "temple-admin-service"
    environment: str = "dev"
    database_url: str = "sqlite:///./temple_admin.db"
    registration_service_url: str = "http://localhost:8002"
    identity_service_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
