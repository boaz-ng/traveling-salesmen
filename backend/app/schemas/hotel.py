"""Hotel result models returned to the frontend."""

from pydantic import BaseModel


class HotelOption(BaseModel):
    """A hotel search result."""

    name: str
    price_per_night: float | None = None
    currency: str = "USD"
    rating: float | None = None
    stars: int | None = None
    address: str = ""
    description: str = ""
    amenities: list[str] | None = None
    image_url: str | None = None
    booking_url: str | None = None
