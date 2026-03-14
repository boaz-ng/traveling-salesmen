"""Flight scoring and ranking."""

from app.schemas.flight import FlightOption

PREFERENCE_WEIGHTS: dict[str, dict[str, float]] = {
    "cost": {"w_cost": 0.7, "w_time": 0.2, "w_stops": 0.1},
    "comfort": {"w_cost": 0.2, "w_time": 0.4, "w_stops": 0.4},
    "balanced": {"w_cost": 0.4, "w_time": 0.35, "w_stops": 0.25},
}


def _normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-1 range. Returns 0.0 if min == max."""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)


def score_flights(
    flights: list[FlightOption], preference: str = "balanced"
) -> list[FlightOption]:
    """Score and sort flights. Lower score is better.

    score = w_cost * norm_price + w_time * norm_duration + w_stops * norm_stops
    """
    if not flights:
        return flights

    weights = PREFERENCE_WEIGHTS.get(preference, PREFERENCE_WEIGHTS["balanced"])

    prices = [f.price for f in flights]
    durations = [f.total_duration_minutes for f in flights]
    stops = [f.stops for f in flights]

    min_price, max_price = min(prices), max(prices)
    min_duration, max_duration = min(durations), max(durations)
    min_stops, max_stops = min(stops), max(stops)

    for flight in flights:
        norm_price = _normalize(flight.price, min_price, max_price)
        norm_duration = _normalize(flight.total_duration_minutes, min_duration, max_duration)
        norm_stops = _normalize(flight.stops, min_stops, max_stops)

        flight.score = (
            weights["w_cost"] * norm_price
            + weights["w_time"] * norm_duration
            + weights["w_stops"] * norm_stops
        )

    flights.sort(key=lambda f: f.score if f.score is not None else float("inf"))
    return flights
