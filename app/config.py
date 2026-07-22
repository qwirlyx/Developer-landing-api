from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Developer Landing API"
    app_env: str = "local"
    api_prefix: str = "/api"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500"

    owner_email: str = "owner@example.com"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Developer Landing"
    smtp_use_tls: bool = True

    brevo_api_key: str = ""

    openrouter_api_key: str = ""
    openrouter_model: str = ""

    rate_limit_max_requests: int = 5
    rate_limit_window_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
