"""Configuration settings for Kevin AI."""

from pydantic_settings import BaseSettings
from typing import Optional, Dict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # LLM Settings - Default model (used as fallback)
    default_model: str = "gpt-4-turbo-preview"
    max_tokens: int = 4096
    temperature: float = 0.7

    # Multi-Model Configuration
    # Fast tier - for simple tasks (file reads, basic queries, formatting)
    fast_model_openai: str = "gpt-3.5-turbo"
    fast_model_anthropic: str = "claude-3-haiku-20240307"
    fast_model_max_tokens: int = 2048

    # Standard tier - for most coding tasks
    standard_model_openai: str = "gpt-4-turbo-preview"
    standard_model_anthropic: str = "claude-3-sonnet-20240229"
    standard_model_max_tokens: int = 4096

    # Premium tier - for complex reasoning
    premium_model_openai: str = "gpt-4"
    premium_model_anthropic: str = "claude-3-opus-20240229"
    premium_model_max_tokens: int = 8192

    # Cost tracking
    enable_cost_tracking: bool = True

    # Model costs per 1K tokens (input/output)
    model_costs: Dict[str, Dict[str, float]] = Field(default_factory=lambda: {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    })

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
