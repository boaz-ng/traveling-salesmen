"""Region-to-airport-codes resolution."""

REGION_MAP: dict[str, list[str]] = {
    # Northeast
    "northeast": ["JFK", "EWR", "LGA", "BOS", "PHL"],
    "new york": ["JFK", "EWR", "LGA"],
    "nyc": ["JFK", "EWR", "LGA"],
    "boston": ["BOS"],
    "boston area": ["BOS", "PVD"],
    "philadelphia": ["PHL"],
    "philly": ["PHL"],
    # Southeast
    "southeast": ["MIA", "FLL", "MCO", "ATL"],
    "florida": ["MIA", "FLL", "MCO", "TPA"],
    "miami": ["MIA", "FLL"],
    "miami area": ["MIA", "FLL"],
    "orlando": ["MCO"],
    "atlanta": ["ATL"],
    # Midwest
    "midwest": ["ORD", "MDW", "DTW", "MSP"],
    "chicago": ["ORD", "MDW"],
    "detroit": ["DTW"],
    "minneapolis": ["MSP"],
    # Southwest
    "southwest": ["DFW", "IAH", "AUS", "PHX"],
    "texas": ["DFW", "IAH", "AUS", "SAT"],
    "dallas": ["DFW"],
    "houston": ["IAH", "HOU"],
    "austin": ["AUS"],
    "phoenix": ["PHX"],
    # West Coast
    "west coast": ["LAX", "SFO", "OAK", "SJC", "SEA"],
    "california": ["LAX", "SFO", "OAK", "SJC"],
    "los angeles": ["LAX"],
    "la": ["LAX"],
    "san francisco": ["SFO", "OAK", "SJC"],
    "sf": ["SFO"],
    "seattle": ["SEA"],
    "portland": ["PDX"],
    # Major international
    "london": ["LHR", "LGW", "STN"],
    "paris": ["CDG", "ORY"],
    "tokyo": ["NRT", "HND"],
    # Caribbean / warm destinations
    "caribbean": ["SJU", "CUN", "MBJ", "PUJ"],
    "cancun": ["CUN"],
    "hawaii": ["HNL", "OGG", "KOA"],
}


def resolve_region(region: str) -> list[str]:
    """Resolve a region name or city to a list of IATA airport codes.

    Handles:
    - Known region/city names (case-insensitive lookup)
    - Direct IATA airport codes (3-letter uppercase pass-through)
    - Comma-separated codes (e.g. "JFK,LAX")
    """
    normalized = region.strip().lower()

    if normalized in REGION_MAP:
        return REGION_MAP[normalized]

    # Check if it's a direct IATA code (3-letter uppercase)
    upper = region.strip().upper()
    if len(upper) == 3 and upper.isalpha():
        return [upper]

    # Check for comma-separated codes
    if "," in region:
        codes = [c.strip().upper() for c in region.split(",") if c.strip()]
        if all(len(c) == 3 and c.isalpha() for c in codes):
            return codes

    return []
