"""Flight result models returned to the frontend."""

from pydantic import BaseModel


class FlightSegment(BaseModel):
    """A single flight segment (one leg of a trip)."""

    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str


class FlightOption(BaseModel):
    """A complete flight option with scoring."""

    price: float
    currency: str = "USD"
    total_duration_minutes: int
    stops: int
    outbound_segments: list[FlightSegment]
    return_segments: list[FlightSegment] | None = None
    score: float | None = None
    airline: str = ""
    # On-time arrival likelihood 0–1 from historical trends (BTS-style); None if unknown
    on_time_likelihood: float | None = None
