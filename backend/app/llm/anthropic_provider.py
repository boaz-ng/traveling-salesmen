"""Anthropic (Claude) LLM provider."""

import logging

from anthropic import Anthropic

from app.config import settings
from app.llm.prompts import SYSTEM_PROMPT
from app.llm.provider import MAX_TOOL_ROUNDS, LLMProvider, handle_tool_call
from app.llm.tools import ANTHROPIC_TOOLS
from app.schemas.flight import FlightOption

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """LLM provider backed by the Anthropic (Claude) API."""

    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.llm_model or "claude-sonnet-4-20250514"

    def run_conversation(
        self,
        messages: list[dict],
    ) -> tuple[str, list[FlightOption] | None]:
        flight_results: list[FlightOption] | None = None

        for _ in range(MAX_TOOL_ROUNDS):
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=ANTHROPIC_TOOLS,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                assistant_content: list[dict] = []
                for block in response.content:
                    if block.type == "text":
                        assistant_content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_content.append(
                            {
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            }
                        )

                messages.append({"role": "assistant", "content": assistant_content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result_str, flights = handle_tool_call(block.name, block.input)
                        if flights is not None:
                            flight_results = flights
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_str,
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
            else:
                text_parts = [
                    block.text for block in response.content if block.type == "text"
                ]
                assistant_text = "\n".join(text_parts)
                messages.append({"role": "assistant", "content": assistant_text})
                return assistant_text, flight_results

        return (
            "I'm having trouble processing your request. Could you try rephrasing?",
            flight_results,
        )
