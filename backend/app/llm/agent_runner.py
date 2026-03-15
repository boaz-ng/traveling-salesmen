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
from app.config import settings

logger = logging.getLogger(__name__)
from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

from app.llm.prompts import SYSTEM_PROMPT
from app.llm.provider import handle_tool_call
from app.llm.tools import (
    _GET_AIRPORT_DELAYS_DESCRIPTION,
    _GET_AIRPORT_DELAYS_PARAMS,
    _GET_AIRPORT_INFO_DESCRIPTION,
    _GET_AIRPORT_INFO_PARAMS,
    _RESOLVE_REGION_DESCRIPTION,
    _RESOLVE_REGION_PARAMS,
    _SEARCH_FLIGHTS_DESCRIPTION,
    _SEARCH_FLIGHTS_PARAMS,
    _SEARCH_HOTELS_DESCRIPTION,
    _SEARCH_HOTELS_PARAMS,
    _UPDATE_REQUIREMENTS_DESCRIPTION,
    _UPDATE_REQUIREMENTS_PARAMS,
)
from app.schemas.chat import ParsedRequirements
from app.schemas.flight import FlightOption
from app.schemas.hotel import HotelOption

_last_flights: List[FlightOption] | None = None
_last_hotels: List[HotelOption] | None = None
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
    "get_airport_delays",
    _GET_AIRPORT_DELAYS_DESCRIPTION,
    _GET_AIRPORT_DELAYS_PARAMS,
)
async def tool_get_airport_delays(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool that fetches live FAA delay status (async)."""
    from app.flights.live_status import get_airport_delays
    airport_code = args.get("airport_code", "")
    result = await get_airport_delays(airport_code)
    if result:
        text = json.dumps(result)
    else:
        text = json.dumps({"status": "no_data", "message": f"No delay data available for {airport_code}"})
    return {
        "content": [{"type": "text", "text": text}]
    }


@tool(
    "get_airport_info",
    _GET_AIRPORT_INFO_DESCRIPTION,
    _GET_AIRPORT_INFO_PARAMS,
)
async def tool_get_airport_info(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool that returns static airport info (terminals, lounges, tips)."""
    result_json, _ = handle_tool_call("get_airport_info", args)
    return {
        "content": [{"type": "text", "text": result_json}]
    }


@tool(
    "search_hotels",
    _SEARCH_HOTELS_DESCRIPTION,
    _SEARCH_HOTELS_PARAMS,
)
async def tool_search_hotels(args: Dict[str, Any]) -> Dict[str, Any]:
    """MCP tool that searches hotels via SerpApi."""
    global _last_hotels
    result_json, hotels = handle_tool_call("search_hotels", args)
    if hotels:
        _last_hotels = hotels
    return {
        "content": [{"type": "text", "text": result_json}]
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
    tools=[tool_resolve_region, tool_search_flights, tool_get_airport_delays, tool_get_airport_info, tool_search_hotels, tool_update_requirements],
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


def _system_prompt_with_context(origin_missing: bool | None) -> str:
    """Add context about missing origin so the agent asks when the user has not provided it."""
    if not origin_missing:
        return SYSTEM_PROMPT
    hint = (
        "\n\nContext: The user has not yet provided a departure city (origin). "
        "If their message does not include one, ask once for it (e.g. \"Which city are you flying from?\" "
        "or \"Please share your departure city or use the location button.\") before calling search_flights."
    )
    return SYSTEM_PROMPT + hint


async def run_agent_session(
    messages: List[Dict[str, Any]],
    origin_missing: bool | None = None,
) -> Tuple[str, List[FlightOption] | None, List[HotelOption] | None, ParsedRequirements | None]:
    """Run a conversation turn via the Claude Agent SDK.

    Args:
        messages: Existing chat history for this session.
        origin_missing: If True, the UI reports the user has not provided a departure city.

    Returns:
        (assistant_text, flight_results_or_none, hotel_results_or_none, parsed_requirements_or_none)
    """
    global _last_flights, _last_hotels, _last_requirements
    _last_flights = None
    _last_hotels = None
    _last_requirements = None

    # Ensure the Claude Code CLI subprocess gets the API key (it reads from env)
    env: Dict[str, str] = {}
    if settings.anthropic_api_key and settings.anthropic_api_key.strip():
        env["ANTHROPIC_API_KEY"] = settings.anthropic_api_key.strip()

    stderr_lines: List[str] = []

    def _stderr_callback(line: str) -> None:
        stderr_lines.append(line)
        logger.info("Claude CLI stderr: %s", line)

    options = ClaudeAgentOptions(
        system_prompt=_system_prompt_with_context(origin_missing),
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
        err_detail = str(e)
        if stderr_lines:
            err_detail += "\nCLI stderr:\n" + "\n".join(stderr_lines)
        logger.exception("Agent session failed: %s", err_detail)
        raise RuntimeError(
            "The assistant could not complete your request. "
            "Check that ANTHROPIC_API_KEY is set in .env and that the Claude Code CLI is installed (npm install -g @anthropic-ai/claude-code). "
            "See server logs for details."
        ) from e

    return assistant_text, _last_flights, _last_hotels, _last_requirements

