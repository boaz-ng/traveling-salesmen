"""Qwen LLM provider (OpenAI-compatible API)."""

import json
import logging

from openai import OpenAI

from app.config import settings
from app.llm.prompts import SYSTEM_PROMPT
from app.llm.provider import MAX_TOOL_ROUNDS, LLMProvider, handle_tool_call
from app.llm.tools import OPENAI_TOOLS
from app.schemas.flight import FlightOption

logger = logging.getLogger(__name__)

QWEN_DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
QWEN_DEFAULT_MODEL = "qwen-plus"


class QwenProvider(LLMProvider):
    """LLM provider backed by Qwen via the OpenAI-compatible API."""

    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url or QWEN_DEFAULT_BASE_URL,
        )
        self._model = settings.llm_model or QWEN_DEFAULT_MODEL

    def run_conversation(
        self,
        messages: list[dict],
    ) -> tuple[str, list[FlightOption] | None]:
        flight_results: list[FlightOption] | None = None

        # Build a working copy of messages in OpenAI format.
        # The session stores simple {"role": ..., "content": ...} dicts for
        # user / assistant text turns.  Tool-call and tool-result turns are
        # appended inside this loop and are also kept on the session list so
        # that multi-turn tool use works correctly within one request.
        api_messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=4096,
                messages=api_messages,
                tools=OPENAI_TOOLS,
            )

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                # Append the assistant message (with tool_calls) to history
                tool_calls_dicts = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]
                assistant_msg: dict = {
                    "role": "assistant",
                    "content": choice.message.content or "",
                    "tool_calls": tool_calls_dicts,
                }
                messages.append(assistant_msg)
                api_messages.append(assistant_msg)

                # Execute each tool and append results
                for tc in choice.message.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result_str, flights = handle_tool_call(tc.function.name, args)
                    if flights is not None:
                        flight_results = flights

                    tool_msg: dict = {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result_str,
                    }
                    messages.append(tool_msg)
                    api_messages.append(tool_msg)
            else:
                # Final text response
                assistant_text = choice.message.content or ""
                messages.append({"role": "assistant", "content": assistant_text})
                return assistant_text, flight_results

        return (
            "I'm having trouble processing your request. Could you try rephrasing?",
            flight_results,
        )
