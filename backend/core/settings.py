from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "meridian-support-chatbot"
    env: str = "dev"
    debug: bool = False

    openrouter_api_key: str = Field(min_length=10)
    openrouter_model: str = "anthropic/claude-3.5-haiku"
    openrouter_base_url: HttpUrl = "https://openrouter.ai/api/v1"
    openrouter_site_url: HttpUrl | None = None
    openrouter_site_name: str | None = None
    max_tool_iterations: int = 8

    mcp_server_url: HttpUrl
    mcp_timeout_seconds: int = 30

    clerk_issuer: HttpUrl
    clerk_jwks_url: HttpUrl
    clerk_audience: str | None = None

    cors_origins: list[str] = ["http://localhost:5173"]
    rate_limit_chat: str = "20/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
