"""Abstract LLM provider base class and shared tool-call handler."""

import json
import logging
from abc import ABC, abstractmethod

from app.flights.serpapi_client import search_flights
from app.flights.regions import resolve_region
from app.flights.scoring import score_flights
from app.schemas.flight import FlightOption
from app.schemas.intent import FlightSearchIntent

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 10


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Each provider implements the conversation loop with tool-use handling
    in its own API format, but delegates tool execution to the shared
    ``handle_tool_call`` helper.
    """

    @abstractmethod
    def run_conversation(
        self,
        messages: list[dict],
    ) -> tuple[str, list[FlightOption] | None]:
        """Run a conversation loop, handling tool calls until a final text response.

        *messages* is the session's message history (mutated in-place to
        append new entries).  Returns ``(assistant_text, flight_results)``.
        """


def handle_tool_call(
    tool_name: str,
    tool_input: dict,
) -> tuple[str, list[FlightOption] | None]:
    """Execute a tool call and return ``(result_json, flights_or_none)``."""
    if tool_name == "resolve_region":
        region = tool_input.get("region", "")
        codes = resolve_region(region)
        if codes:
            result = {"airports": codes}
        else:
            result = {"error": f"Could not resolve region: {region}"}
        return json.dumps(result), None

    if tool_name == "search_flights":
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
