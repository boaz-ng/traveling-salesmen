"""Claude Agent SDK runner for the flight search assistant.

This module wires the Claude Agent SDK to the existing domain logic:

- The agent uses the same SYSTEM_PROMPT behavior description.
- Custom tools delegate to ``handle_tool_call`` for ``resolve_region`` and
  ``search_flights`` so we reuse all existing SerpApi integration and scoring.
- ``run_agent_session`` exposes a simple interface compatible with the
  existing orchestrator: it takes a message history and returns
  ``(assistant_text, flights_or_none, parsed_requirements_or_none)``.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool
from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

from app.config import settings
from app.llm.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)
from app.llm.provider import handle_tool_call
from app.llm.tools import (
    _RESOLVE_REGION_DESCRIPTION,
    _RESOLVE_REGION_PARAMS,
    _SEARCH_FLIGHTS_DESCRIPTION,
    _SEARCH_FLIGHTS_PARAMS,
    _UPDATE_REQUIREMENTS_DESCRIPTION,
    _UPDATE_REQUIREMENTS_PARAMS,
)
from app.schemas.chat import ParsedRequirements
from app.schemas.flight import FlightOption

_last_flights: List[FlightOption] | None = None
_last_requirements: ParsedRequirements | None = None


@tool(
    "resolve_region",
    _RESOLVE_REGION_DESCRIPTION,
    _RESOLVE_REGION_PARAMS,
)
async def tool_resolve_region(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool that delegates to the existing resolve_region tool handler."""
    result_json, _ = handle_tool_call("resolve_region", args)
    return {
        "content": [
            {
                "type": "text",
                "text": result_json,
            }
        ]
    }


@tool(
    "search_flights",
    _SEARCH_FLIGHTS_DESCRIPTION,
    _SEARCH_FLIGHTS_PARAMS,
)
async def tool_search_flights(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool that delegates to the existing search_flights tool handler."""
    global _last_flights
    result_json, flights = handle_tool_call("search_flights", args)
    _last_flights = flights
    return {
        "content": [
            {
                "type": "text",
                "text": result_json,
            }
        ]
    }


@tool(
    "update_requirements",
    _UPDATE_REQUIREMENTS_DESCRIPTION,
    _UPDATE_REQUIREMENTS_PARAMS,
)
async def tool_update_requirements(args: Dict[str, Any]) -> Dict[str, Any]:
    """Capture the agent's current understanding of trip requirements."""
    global _last_requirements
    _last_requirements = ParsedRequirements(**{
        k: v for k, v in args.items() if v is not None
    })
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps({"status": "requirements_updated"}),
            }
        ]
    }


flight_tools_server = create_sdk_mcp_server(
    name="flight-tools",
    version="0.1.0",
    tools=[tool_resolve_region, tool_search_flights, tool_update_requirements],
)


def _build_prompt(messages: List[Dict[str, Any]]) -> str:
    """Render the conversation history as a plain-text transcript for Claude."""
    lines: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if not isinstance(content, str):
            continue
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


async def run_agent_session(
    messages: List[Dict[str, Any]],
) -> Tuple[str, List[FlightOption] | None, ParsedRequirements | None]:
    """Run a conversation turn via the Claude Agent SDK.

    Args:
        messages: Existing chat history for this session.

    Returns:
        (assistant_text, flight_results_or_none, parsed_requirements_or_none)
    """
    global _last_flights, _last_requirements
    _last_flights = None
    _last_requirements = None

    # Pass API key to the Claude Code CLI subprocess (it reads from env)
    env: Dict[str, str] = {}
    if settings.anthropic_api_key and settings.anthropic_api_key.strip():
        env["ANTHROPIC_API_KEY"] = settings.anthropic_api_key.strip()

    stderr_lines: List[str] = []

    def _stderr_callback(line: str) -> None:
        stderr_lines.append(line)
        logger.info("Claude CLI stderr: %s", line)

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"flight-tools": flight_tools_server},
        permission_mode="bypassPermissions",
        env=env,
        stderr=_stderr_callback,
    )

    prompt = _build_prompt(messages)
    assistant_text = ""
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        assistant_text += block.text
            elif isinstance(message, ResultMessage) and message.result and not assistant_text:
                assistant_text = message.result
    except Exception as e:
        logger.exception(
            "Agent session failed: %s%s",
            str(e),
            "\nCLI stderr:\n" + "\n".join(stderr_lines) if stderr_lines else "",
        )
        # Return a friendly message instead of raising so we respond 200, not 500
        assistant_text = (
            "I couldn't complete that request. Please check that:\n"
            "1. **ANTHROPIC_API_KEY** is set in your `.env` file (at the project root).\n"
            "2. The Claude Code CLI is installed: `npm install -g @anthropic-ai/claude-code`\n"
            "3. The `claude` command is on your PATH (`claude -v`).\n\n"
            "See the server logs for more details."
        )

    return assistant_text, _last_flights, _last_requirements

