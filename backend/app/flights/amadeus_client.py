"""Amadeus API wrapper for flight search."""

import logging

from amadeus import Client, ResponseError

from app.config import settings
from app.schemas.flight import FlightOption, FlightSegment
from app.schemas.intent import FlightSearchIntent

logger = logging.getLogger(__name__)


def _get_client() -> Client:
    """Create an Amadeus API client."""
    hostname = "test" if settings.amadeus_env == "test" else "production"
    return Client(
        client_id=settings.amadeus_api_key,
        client_secret=settings.amadeus_api_secret,
        hostname=hostname,
    )


def _parse_segment(segment: dict) -> FlightSegment:
    """Parse an Amadeus segment into our model."""
    return FlightSegment(
        airline=segment.get("carrierCode", ""),
        flight_number=f"{segment.get('carrierCode', '')}{segment.get('number', '')}",
        departure_airport=segment["departure"]["iataCode"],
        arrival_airport=segment["arrival"]["iataCode"],
        departure_time=segment["departure"]["at"],
        arrival_time=segment["arrival"]["at"],
        duration=segment.get("duration", ""),
    )


def _parse_duration_minutes(duration_str: str) -> int:
    """Parse ISO 8601 duration (e.g. 'PT2H30M') to total minutes."""
    duration_str = duration_str.replace("PT", "")
    hours = 0
    minutes = 0
    if "H" in duration_str:
        parts = duration_str.split("H")
        hours = int(parts[0])
        duration_str = parts[1]
    if "M" in duration_str:
        minutes = int(duration_str.replace("M", ""))
    return hours * 60 + minutes


def _parse_flight_offer(offer: dict) -> FlightOption:
    """Parse an Amadeus flight offer into a FlightOption."""
    price = float(offer["price"]["total"])
    currency = offer["price"].get("currency", "USD")

    itineraries = offer.get("itineraries", [])

    outbound = itineraries[0] if itineraries else {}
    outbound_segments = [_parse_segment(s) for s in outbound.get("segments", [])]
    outbound_duration = _parse_duration_minutes(outbound.get("duration", "PT0M"))

    return_segments = None
    return_duration = 0
    if len(itineraries) > 1:
        ret = itineraries[1]
        return_segments = [_parse_segment(s) for s in ret.get("segments", [])]
        return_duration = _parse_duration_minutes(ret.get("duration", "PT0M"))

    stops = max(0, len(outbound_segments) - 1)
    total_duration = outbound_duration + return_duration

    airline = outbound_segments[0].airline if outbound_segments else ""

    return FlightOption(
        price=price,
        currency=currency,
        total_duration_minutes=total_duration,
        stops=stops,
        outbound_segments=outbound_segments,
        return_segments=return_segments,
        airline=airline,
    )


def search_flights(intent: FlightSearchIntent) -> list[FlightOption]:
    """Search flights using the Amadeus API.

    Searches across all origin/destination airport pairs and merges results.
    """
    client = _get_client()
    all_options: list[FlightOption] = []

    cabin_map = {
        "ECONOMY": "ECONOMY",
        "PREMIUM_ECONOMY": "PREMIUM_ECONOMY",
        "BUSINESS": "BUSINESS",
        "FIRST": "FIRST",
    }
    travel_class = cabin_map.get(intent.cabin_class, "ECONOMY")

    for origin in intent.origin_airports:
        for destination in intent.destination_airports:
            try:
                params: dict = {
                    "originLocationCode": origin,
                    "destinationLocationCode": destination,
                    "departureDate": intent.departure_date_start.isoformat(),
                    "adults": intent.passengers,
                    "travelClass": travel_class,
                    "max": 10,
                    "currencyCode": "USD",
                }

                if intent.return_date_start:
                    params["returnDate"] = intent.return_date_start.isoformat()

                if intent.max_budget_usd:
                    params["maxPrice"] = int(intent.max_budget_usd)

                if intent.max_stops is not None:
                    if intent.max_stops == 0:
                        params["nonStop"] = "true"

                response = client.shopping.flight_offers_search.get(**params)
                offers = response.data if response.data else []

                for offer in offers:
                    try:
                        option = _parse_flight_offer(offer)
                        all_options.append(option)
                    except (KeyError, ValueError, IndexError) as e:
                        logger.warning("Failed to parse flight offer: %s", e)

            except ResponseError as e:
                logger.warning(
                    "Amadeus API error for %s→%s: %s",
                    origin,
                    destination,
                    e,
                )

    return all_options
