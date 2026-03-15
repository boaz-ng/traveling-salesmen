"""Abstract LLM provider base class and shared tool-call handler."""

import json
import logging
from abc import ABC, abstractmethod

from pydantic import ValidationError

from app.flights.on_time_lookup import get_on_time_likelihood
from app.flights.serpapi_client import search_flights
from app.flights.regions import resolve_region
from app.flights.scoring import score_flights
from app.schemas.flight import FlightOption
from app.schemas.intent import FlightSearchIntent

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 10
_AIRPORT_DELAY_SENTINEL = "__AIRPORT_DELAY_ASYNC__"


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
            origin_airports = getattr(intent, "origin_airports", None)
            if not origin_airports or (isinstance(origin_airports, list) and len(origin_airports) == 0):
                return (
                    json.dumps({
                        "error": "origin_required",
                        "message": "Departure city is required. Ask the user for their origin (e.g. 'Which city are you flying from?') or suggest they use the location button.",
                    }),
                    None,
                )
            flights = search_flights(intent)
            for f in flights:
                segs = f.outbound_segments
                origin_ap = segs[0].departure_airport if segs else None
                dest_ap = segs[-1].arrival_airport if segs else None
                f.on_time_likelihood = get_on_time_likelihood(
                    f.airline, origin_airport=origin_ap, destination_airport=dest_ap,
                )
            scored = score_flights(flights, intent.preference)

            top_flights = scored[:10]
            result = [f.model_dump() for f in top_flights]
            return json.dumps(result, default=str), top_flights
        except ValidationError as e:
            errors = e.errors()
            if any(
                "origin_airports" in (err.get("loc") or [])
                for err in errors
            ):
                return (
                    json.dumps({
                        "error": "origin_required",
                        "message": "Departure city is required. Ask the user for their origin (e.g. 'Which city are you flying from?') or suggest they use the location button.",
                    }),
                    None,
                )
            logger.warning("Search flights validation error: %s", e)
            return json.dumps({"error": str(e)}), None
        except Exception as e:
            logger.exception("Flight search failed")
            return json.dumps({"error": str(e)}), None

    if tool_name == "get_airport_delays":
        return _AIRPORT_DELAY_SENTINEL, None

    if tool_name == "get_airport_info":
        from app.flights.airport_info import get_airport_info
        airport_code = tool_input.get("airport_code", "")
        info = get_airport_info(airport_code)
        if info:
            return json.dumps(info), None
        return json.dumps({"error": f"No info available for {airport_code}"}), None

    if tool_name == "search_hotels":
        from app.hotels.serpapi_client import search_hotels as _search_hotels
        try:
            hotels = _search_hotels(
                city=tool_input.get("city", ""),
                check_in_date=tool_input.get("check_in_date", ""),
                check_out_date=tool_input.get("check_out_date", ""),
                adults=tool_input.get("adults", 2),
                max_price=tool_input.get("max_price"),
            )
            result = [h.model_dump() for h in hotels]
            return json.dumps(result, default=str), hotels
        except Exception as e:
            logger.exception("Hotel search failed")
            return json.dumps({"error": str(e)}), None

    return json.dumps({"error": f"Unknown tool: {tool_name}"}), None
