"""Chat request / response models."""

from pydantic import BaseModel

from app.schemas.flight import FlightOption


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""

    session_id: str | None = None
    message: str


class ParsedRequirements(BaseModel):
    """Structured snapshot of the agent's current understanding of the trip."""

    origin: str | None = None
    destination: str | None = None
    origin_airports: list[str] | None = None
    destination_airports: list[str] | None = None
    departure_dates: str | None = None
    return_dates: str | None = None
    budget: str | None = None
    passengers: int | None = None
    cabin_class: str | None = None
    preference: str | None = None


class ChatResponse(BaseModel):
    """Response returned to the frontend."""

    session_id: str
    response: str
    flights: list[FlightOption] | None = None
    parsed_intent: ParsedRequirements | None = None
