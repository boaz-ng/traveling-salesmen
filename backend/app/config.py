"""Pydantic Settings for environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Always resolve .env relative to the project root, regardless of working directory
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM provider toggle: "qwen" (default) or "anthropic"
    llm_provider: str = "qwen"
    # Optional model override — leave empty to use the provider default
    llm_model: str = ""

    # Anthropic (Claude)
    anthropic_api_key: str = ""

    # Qwen (OpenAI-compatible)
    qwen_api_key: str = ""
    qwen_base_url: str = ""

    # SerpApi flight search
    serpapi_api_key: str = ""

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
