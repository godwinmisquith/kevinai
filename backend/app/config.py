"""Configuration settings for Kevin AI."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # LLM Settings
    default_model: str = "gpt-4-turbo-preview"
    max_tokens: int = 4096
    temperature: float = 0.7

    # Database
    database_url: str = "sqlite+aiosqlite:///./kevin.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Workspace
    workspace_dir: str = "/tmp/kevin-workspace"

    # Browser
    browser_headless: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
