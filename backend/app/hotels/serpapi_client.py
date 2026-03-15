"""SerpApi Google Hotels wrapper for hotel search."""

import logging

import serpapi

from app.config import settings
from app.schemas.hotel import HotelOption

logger = logging.getLogger(__name__)


def _parse_hotel(raw: dict) -> HotelOption:
    """Parse a SerpApi hotel result into our model."""
    name = raw.get("name", "Unknown Hotel")

    rate_info = raw.get("rate_per_night", {})
    price_str = rate_info.get("lowest", "") if isinstance(rate_info, dict) else ""
    price = None
    if price_str:
        digits = "".join(c for c in str(price_str) if c.isdigit() or c == ".")
        try:
            price = float(digits)
        except ValueError:
            pass

    rating = raw.get("overall_rating")
    if rating is not None:
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            rating = None

    stars = raw.get("hotel_class")
    if stars is not None:
        try:
            stars = int(stars)
        except (ValueError, TypeError):
            stars = None

    amenities = raw.get("amenities") or []
    if isinstance(amenities, list):
        amenities = [str(a) for a in amenities[:10]]
    else:
        amenities = []

    images = raw.get("images", [])
    image_url = None
    if images and isinstance(images, list):
        first = images[0]
        if isinstance(first, dict):
            image_url = first.get("thumbnail") or first.get("original_image")
        elif isinstance(first, str):
            image_url = first

    link = raw.get("link") or raw.get("serpapi_link") or None

    return HotelOption(
        name=name,
        price_per_night=price,
        rating=rating,
        stars=stars,
        address=raw.get("address", ""),
        description=raw.get("description", raw.get("extracted_description", "")),
        amenities=amenities if amenities else None,
        image_url=image_url,
        booking_url=link,
    )


def search_hotels(
    city: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    max_price: float | None = None,
) -> list[HotelOption]:
    """Search hotels using the SerpApi Google Hotels engine.

    Args:
        city: City or location query (e.g. "Miami", "Paris").
        check_in_date: ISO date (YYYY-MM-DD).
        check_out_date: ISO date (YYYY-MM-DD).
        adults: Number of adults (default 2).
        max_price: Optional max price per night in USD.

    Returns:
        List of HotelOption results.
    """
    if not (settings.serpapi_api_key or "").strip():
        raise ValueError("SERPAPI_API_KEY is not set.")

    params: dict = {
        "engine": "google_hotels",
        "q": city,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": "USD",
        "gl": "us",
        "hl": "en",
    }

    if max_price:
        params["max_price"] = int(max_price)

    try:
        client = serpapi.Client(api_key=settings.serpapi_api_key)
        raw = client.search(params)
        results = raw if isinstance(raw, dict) else dict(raw) if hasattr(raw, "keys") else {}

        properties = results.get("properties", [])
        hotels: list[HotelOption] = []
        for prop in properties[:10]:
            try:
                hotels.append(_parse_hotel(prop))
            except Exception as e:
                logger.warning("Failed to parse hotel: %s", e)

        return hotels

    except ValueError:
        raise
    except Exception as e:
        logger.warning("Hotel search failed: %s", e, exc_info=True)
        if "api_key" in str(e).lower() or "401" in str(e):
            raise ValueError(f"SerpAPI hotel request failed (check API key): {e}") from e
        return []
