"""Chat request / response models."""

from pydantic import BaseModel

from app.schemas.flight import FlightOption


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""

    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    """Response returned to the frontend."""

    session_id: str
    response: str
    flights: list[FlightOption] | None = None
