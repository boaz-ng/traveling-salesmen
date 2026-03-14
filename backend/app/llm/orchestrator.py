"""Core conversation loop: manages message history, calls Claude API with tools."""

import json
import logging

from anthropic import Anthropic

from app.config import settings
from app.flights.amadeus_client import search_flights
from app.flights.regions import resolve_region
from app.flights.scoring import score_flights
from app.llm.prompts import SYSTEM_PROMPT
from app.llm.tools import TOOLS
from app.schemas.flight import FlightOption
from app.schemas.intent import FlightSearchIntent

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOOL_ROUNDS = 10


def _handle_tool_call(tool_name: str, tool_input: dict) -> tuple[str, list[FlightOption] | None]:
    """Execute a tool call and return (result_json, flights_if_search)."""
    if tool_name == "resolve_region":
        region = tool_input.get("region", "")
        codes = resolve_region(region)
        if codes:
            result = {"airports": codes}
        else:
            result = {"error": f"Could not resolve region: {region}"}
        return json.dumps(result), None

    elif tool_name == "search_flights":
        try:
            intent = FlightSearchIntent(**tool_input)
            flights = search_flights(intent)
            scored = score_flights(flights, intent.preference)

            top_flights = scored[:10]
            result = [f.model_dump() for f in top_flights]
            return json.dumps(result, default=str), top_flights
        except Exception as e:
            logger.exception("Flight search failed")
            return json.dumps({"error": str(e)}), None

    return json.dumps({"error": f"Unknown tool: {tool_name}"}), None


def run_conversation(
    messages: list[dict],
) -> tuple[str, list[FlightOption] | None]:
    """Run the conversation loop with Claude, handling tool calls.

    Args:
        messages: The full message history for this session.

    Returns:
        (assistant_text_response, flight_results_or_none)
    """
    client = Anthropic(api_key=settings.anthropic_api_key)
    flight_results: list[FlightOption] | None = None

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Add the assistant message with tool use to history
            assistant_content = []
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

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result_str, flights = _handle_tool_call(block.name, block.input)
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
            # Claude produced a final text response
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)

            assistant_text = "\n".join(text_parts)
            messages.append({"role": "assistant", "content": assistant_text})
            return assistant_text, flight_results

    return "I'm having trouble processing your request. Could you try rephrasing?", flight_results
