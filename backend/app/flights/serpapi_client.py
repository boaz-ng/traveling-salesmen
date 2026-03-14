"""SerpApi Google Flights wrapper for flight search."""

import logging

import serpapi

from app.config import settings
from app.schemas.flight import FlightOption, FlightSegment
from app.schemas.intent import FlightSearchIntent

logger = logging.getLogger(__name__)

TRAVEL_CLASS_MAP = {
    "ECONOMY": 1,
    "PREMIUM_ECONOMY": 2,
    "BUSINESS": 3,
    "FIRST": 4,
}


def _parse_segment(leg: dict) -> FlightSegment:
    """Parse a SerpApi flight leg into our model."""
    departure = leg.get("departure_airport", {})
    arrival = leg.get("arrival_airport", {})
    flight_number = leg.get("flight_number", "")
    airline_code = flight_number.split(" ")[0] if " " in flight_number else flight_number

    return FlightSegment(
        airline=airline_code,
        flight_number=flight_number.replace(" ", ""),
        departure_airport=departure.get("id", ""),
        arrival_airport=arrival.get("id", ""),
        departure_time=departure.get("time", ""),
        arrival_time=arrival.get("time", ""),
        duration=str(leg.get("duration", "")),
    )


def _parse_flight_offer(offer: dict) -> FlightOption | None:
    """Parse a SerpApi flight offer into a FlightOption. Returns None if price is missing."""
    raw_price = offer.get("price")
    if not raw_price:
        return None
    price = float(raw_price)
    legs = offer.get("flights", [])

    outbound_segments = [_parse_segment(leg) for leg in legs]
    total_duration = int(offer.get("total_duration", 0))
    stops = max(0, len(outbound_segments) - 1)
    airline = outbound_segments[0].airline if outbound_segments else ""

    return FlightOption(
        price=price,
        currency="USD",
        total_duration_minutes=total_duration,
        stops=stops,
        outbound_segments=outbound_segments,
        return_segments=None,
        airline=airline,
    )


def _results_to_dict(results) -> dict:
    """Normalize SerpAPI response to a dict for .get() access."""
    if isinstance(results, dict):
        return results
    if hasattr(results, "get"):
        return results
    if hasattr(results, "__dict__"):
        return getattr(results, "__dict__", {})
    return dict(results) if hasattr(results, "keys") else {}


def search_flights(intent: FlightSearchIntent) -> list[FlightOption]:
    """Search flights using the SerpApi Google Flights API.

    Searches across all origin/destination airport pairs and merges results.
    """
    if not (settings.serpapi_api_key or "").strip():
        raise ValueError(
            "SERPAPI_API_KEY is not set. Add it to .env or set the environment variable."
        )

    all_options: list[FlightOption] = []
    travel_class = TRAVEL_CLASS_MAP.get(intent.cabin_class, 1)
    is_one_way = intent.return_date_start is None

    for origin in intent.origin_airports:
        for destination in intent.destination_airports:
            try:
                params: dict = {
                    "engine": "google_flights",
                    "departure_id": origin,
                    "arrival_id": destination,
                    "outbound_date": intent.departure_date_start.isoformat(),
                    "adults": intent.passengers,
                    "travel_class": travel_class,
                    "currency": "USD",
                    "type": 2 if is_one_way else 1,  # 1=round trip, 2=one-way
                }

                if not is_one_way and intent.return_date_start:
                    params["return_date"] = intent.return_date_start.isoformat()

                if intent.max_budget_usd:
                    params["max_price"] = int(intent.max_budget_usd)

                if intent.max_stops is not None and intent.max_stops == 0:
                    params["stops"] = 1  # nonstop only in SerpApi

                client = serpapi.Client(api_key=settings.serpapi_api_key)
                raw = client.search(params)
                results = _results_to_dict(raw)

                offers = results.get("best_flights", []) + results.get("other_flights", [])
                for offer in offers:
                    try:
                        option = _parse_flight_offer(offer)
                        if option is not None:
                            all_options.append(option)
                    except (KeyError, ValueError, IndexError) as e:
                        logger.warning("Failed to parse flight offer: %s", e)

            except ValueError:
                raise
            except Exception as e:
                logger.warning(
                    "SerpApi error for %s→%s: %s",
                    origin,
                    destination,
                    e,
                    exc_info=True,
                )
                if "api_key" in str(e).lower() or "401" in str(e) or "invalid" in str(e).lower():
                    raise ValueError(
                        "SerpAPI request failed (check SERPAPI_API_KEY in .env): " + str(e)
                    ) from e

    return all_options
