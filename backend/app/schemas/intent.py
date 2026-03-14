"""FlightSearchIntent — the contract between LLM interpretation and flight search."""

from datetime import date

from pydantic import BaseModel


class FlightSearchIntent(BaseModel):
    """Structured interface between the LLM and flight search layers."""

    origin_airports: list[str]
    destination_airports: list[str]
    departure_date_start: date
    departure_date_end: date
    return_date_start: date | None = None
    return_date_end: date | None = None
    max_budget_usd: float | None = None
    max_stops: int | None = None
    passengers: int = 1
    cabin_class: str = "ECONOMY"
    preference: str = "balanced"
