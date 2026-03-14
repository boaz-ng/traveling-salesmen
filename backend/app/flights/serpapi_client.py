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


def _parse_flight_offer(offer: dict) -> FlightOption:
    """Parse a SerpApi flight offer into a FlightOption."""
    price = float(offer.get("price", 0))
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


def search_flights(intent: FlightSearchIntent) -> list[FlightOption]:
    """Search flights using the SerpApi Google Flights API.

    Searches across all origin/destination airport pairs and merges results.
    """
    all_options: list[FlightOption] = []
    travel_class = TRAVEL_CLASS_MAP.get(intent.cabin_class, 1)

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
                }

                if intent.return_date_start:
                    params["return_date"] = intent.return_date_start.isoformat()

                if intent.max_budget_usd:
                    params["max_price"] = int(intent.max_budget_usd)

                if intent.max_stops is not None and intent.max_stops == 0:
                    params["stops"] = 1  # nonstop only in SerpApi

                client = serpapi.Client(api_key=settings.serpapi_api_key)
                results = client.search(params)

                offers = results.get("best_flights", []) + results.get("other_flights", [])
                for offer in offers:
                    try:
                        option = _parse_flight_offer(offer)
                        all_options.append(option)
                    except (KeyError, ValueError, IndexError) as e:
                        logger.warning("Failed to parse flight offer: %s", e)

            except Exception as e:
                logger.warning(
                    "SerpApi error for %s→%s: %s",
                    origin,
                    destination,
                    e,
                )

    return all_options
