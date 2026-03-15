"""Live airport delay status from the FAA NAS (National Airspace System) API.

The FAA endpoint is free, requires no API key, and returns general delay/closure
information for US airports. International airports return None (no data).
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

FAA_STATUS_URL = "https://soa.smext.faa.gov/asws/api/airport/status/{airport_code}"

_DELAY_CACHE: dict[str, dict[str, Any] | None] = {}


async def get_airport_delays(airport_code: str) -> dict[str, Any] | None:
    """Fetch live delay info for a US airport.

    Returns a dict with keys:
      - airport: IATA code
      - name: airport name
      - delay: bool
      - delay_reason: str or None
      - avg_delay_minutes: int or None
      - status_text: human-readable summary
    Returns None for non-US airports or on error.
    """
    code = airport_code.strip().upper()
    if not code or len(code) != 3:
        return None

    if code in _DELAY_CACHE:
        return _DELAY_CACHE[code]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                FAA_STATUS_URL.format(airport_code=code),
                headers={"Accept": "application/json"},
            )
            if resp.status_code != 200:
                _DELAY_CACHE[code] = None
                return None

            data = resp.json()

        name = data.get("Name", code)
        delay = bool(data.get("Delay", False))
        status_items = data.get("Status", [])

        reason = None
        avg_mins = None
        parts: list[str] = []

        for item in status_items if isinstance(status_items, list) else []:
            r = item.get("Reason", "")
            if r:
                reason = r
            avg = item.get("AvgDelay", "")
            if avg:
                try:
                    avg_mins = int("".join(c for c in avg if c.isdigit()) or "0")
                except ValueError:
                    pass
            typ = item.get("Type", "")
            if typ:
                parts.append(f"{typ}: {r}" if r else typ)

        if delay:
            status_text = "; ".join(parts) if parts else "Delays reported"
            if avg_mins:
                status_text += f" (avg {avg_mins} min)"
        else:
            status_text = "No delays reported"

        result: dict[str, Any] = {
            "airport": code,
            "name": name,
            "delay": delay,
            "delay_reason": reason,
            "avg_delay_minutes": avg_mins,
            "status_text": status_text,
        }
        _DELAY_CACHE[code] = result
        return result

    except Exception:
        logger.debug("FAA status fetch failed for %s", code, exc_info=True)
        _DELAY_CACHE[code] = None
        return None


def clear_delay_cache() -> None:
    """Clear cached FAA responses (useful between requests or for testing)."""
    _DELAY_CACHE.clear()
