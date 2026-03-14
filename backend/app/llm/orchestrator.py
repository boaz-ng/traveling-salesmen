"""Core conversation loop: selects LLM provider and delegates."""

import logging

from app.config import settings
from app.llm.provider import LLMProvider
from app.schemas.flight import FlightOption

logger = logging.getLogger(__name__)

_provider_instance: LLMProvider | None = None


def get_provider() -> LLMProvider:
    """Return the configured LLM provider (cached after first call)."""
    global _provider_instance  # noqa: PLW0603
    if _provider_instance is not None:
        return _provider_instance

    name = settings.llm_provider.lower()
    if name == "anthropic":
        from app.llm.anthropic_provider import AnthropicProvider

        _provider_instance = AnthropicProvider()
    elif name == "qwen":
        from app.llm.qwen_provider import QwenProvider

        _provider_instance = QwenProvider()
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{settings.llm_provider}'. "
            "Supported values: 'qwen', 'anthropic'."
        )

    logger.info("Using LLM provider: %s", name)
    return _provider_instance


def run_conversation(
    messages: list[dict],
) -> tuple[str, list[FlightOption] | None]:
    """Run the conversation loop with the configured LLM provider.

    Args:
        messages: The full message history for this session.

    Returns:
        (assistant_text_response, flight_results_or_none)
    """
    provider = get_provider()
    return provider.run_conversation(messages)
