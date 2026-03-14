"""Pydantic Settings for environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    anthropic_api_key: str = ""
    amadeus_api_key: str = ""
    amadeus_api_secret: str = ""
    amadeus_env: str = "test"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
