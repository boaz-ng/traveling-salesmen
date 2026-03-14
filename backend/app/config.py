"""Pydantic Settings for environment variables."""

from pydantic_settings import BaseSettings


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

    # Amadeus flight search
    amadeus_api_key: str = ""
    amadeus_api_secret: str = ""
    amadeus_env: str = "test"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
