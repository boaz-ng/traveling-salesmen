"""Tool definitions for LLM tool use.

Provides both Anthropic and OpenAI formats from a single source of truth.
"""

# ── Shared JSON-Schema fragments ────────────────────────────────────────────

_RESOLVE_REGION_DESCRIPTION = (
    "Resolve a vague region name, city name, or area into a list of IATA airport codes. "
    "Use this when the user mentions a region like 'northeast', a city like 'New York', "
    "or an area like 'Boston area'."
)

_RESOLVE_REGION_PARAMS = {
    "type": "object",
    "properties": {
        "region": {
            "type": "string",
            "description": (
                "The region, city, or area name to resolve "
                "(e.g., 'northeast', 'new york', 'sf')."
            ),
        }
    },
    "required": ["region"],
}

_SEARCH_FLIGHTS_DESCRIPTION = (
    "Search for flights using structured search parameters. Call this once you have "
    "gathered enough information from the user: origin airports, destination airports, "
    "and departure date range at minimum."
)

_SEARCH_FLIGHTS_PARAMS = {
    "type": "object",
    "properties": {
        "origin_airports": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of origin IATA airport codes (e.g., ['JFK', 'EWR']).",
        },
        "destination_airports": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of destination IATA airport codes.",
        },
        "departure_date_start": {
            "type": "string",
            "description": "Start of departure date range (YYYY-MM-DD).",
        },
        "departure_date_end": {
            "type": "string",
            "description": "End of departure date range (YYYY-MM-DD).",
        },
        "return_date_start": {
            "type": "string",
            "description": "Start of return date range (YYYY-MM-DD), or null for one-way.",
        },
        "return_date_end": {
            "type": "string",
            "description": "End of return date range (YYYY-MM-DD), or null for one-way.",
        },
        "max_budget_usd": {
            "type": "number",
            "description": "Maximum budget in USD, or null for no limit.",
        },
        "max_stops": {
            "type": "integer",
            "description": "Maximum number of stops, or null for any.",
        },
        "passengers": {
            "type": "integer",
            "description": "Number of passengers (default 1).",
            "default": 1,
        },
        "cabin_class": {
            "type": "string",
            "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
            "description": "Cabin class (default ECONOMY).",
            "default": "ECONOMY",
        },
        "preference": {
            "type": "string",
            "enum": ["cost", "comfort", "balanced"],
            "description": "Scoring preference (default balanced).",
            "default": "balanced",
        },
    },
    "required": [
        "origin_airports",
        "destination_airports",
        "departure_date_start",
        "departure_date_end",
    ],
}

_GET_AIRPORT_DELAYS_DESCRIPTION = (
    "Get live delay status for a US airport. Returns whether there are current "
    "delays, the reason, and average delay in minutes. Use when the user asks about "
    "delays or current conditions at an airport."
)

_GET_AIRPORT_DELAYS_PARAMS = {
    "type": "object",
    "properties": {
        "airport_code": {
            "type": "string",
            "description": "IATA airport code (e.g. 'JFK', 'LAX', 'ORD').",
        }
    },
    "required": ["airport_code"],
}

_SEARCH_HOTELS_DESCRIPTION = (
    "Search for hotels in a city or near a destination. Use when the user mentions "
    "accommodation, hotels, or where to stay. Requires a city/location, check-in date, "
    "and check-out date."
)

_SEARCH_HOTELS_PARAMS = {
    "type": "object",
    "properties": {
        "city": {
            "type": "string",
            "description": "City or location query (e.g. 'Miami', 'Paris', 'Tokyo').",
        },
        "check_in_date": {
            "type": "string",
            "description": "Check-in date in ISO format (YYYY-MM-DD).",
        },
        "check_out_date": {
            "type": "string",
            "description": "Check-out date in ISO format (YYYY-MM-DD).",
        },
        "adults": {
            "type": "integer",
            "description": "Number of adults (default 2).",
            "default": 2,
        },
        "max_price": {
            "type": "number",
            "description": "Maximum price per night in USD, or null for no limit.",
        },
    },
    "required": ["city", "check_in_date", "check_out_date"],
}

_GET_AIRPORT_INFO_DESCRIPTION = (
    "Get information about a major airport: terminals, lounges, tips. "
    "Use when the user asks about airport facilities, lounges, or general info."
)

_GET_AIRPORT_INFO_PARAMS = {
    "type": "object",
    "properties": {
        "airport_code": {
            "type": "string",
            "description": "IATA airport code (e.g. 'JFK', 'LAX', 'LHR').",
        }
    },
    "required": ["airport_code"],
}

_UPDATE_REQUIREMENTS_DESCRIPTION = (
    "Report your current structured understanding of the user's trip requirements. "
    "Call this EVERY turn — even if some fields are still unknown — so the UI can "
    "display what has been gathered so far."
)

_UPDATE_REQUIREMENTS_PARAMS = {
    "type": "object",
    "properties": {
        "origin": {
            "type": "string",
            "description": "Human-readable origin (e.g., 'New York City', 'Los Angeles').",
        },
        "destination": {
            "type": "string",
            "description": "Human-readable destination (e.g., 'Tokyo', 'Southeast Asia').",
        },
        "origin_airports": {
            "type": "array",
            "items": {"type": "string"},
            "description": "IATA codes for origin airports, if known (e.g., ['JFK', 'EWR']).",
        },
        "destination_airports": {
            "type": "array",
            "items": {"type": "string"},
            "description": "IATA codes for destination airports, if known.",
        },
        "departure_dates": {
            "type": "string",
            "description": (
                "Departure date range as understood so far "
                "(e.g., 'late June 2025', '2025-06-20 to 2025-06-30')."
            ),
        },
        "return_dates": {
            "type": "string",
            "description": "Return date range, or null for one-way.",
        },
        "budget": {
            "type": "string",
            "description": "Budget constraint as stated by the user (e.g., 'under $400').",
        },
        "passengers": {
            "type": "integer",
            "description": "Number of passengers.",
        },
        "cabin_class": {
            "type": "string",
            "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
            "description": "Cabin class.",
        },
        "preference": {
            "type": "string",
            "enum": ["cost", "comfort", "balanced"],
            "description": "Scoring preference.",
        },
    },
    "required": [],
}

# ── Anthropic format (used by Claude) ───────────────────────────────────────

ANTHROPIC_TOOLS = [
    {
        "name": "resolve_region",
        "description": _RESOLVE_REGION_DESCRIPTION,
        "input_schema": _RESOLVE_REGION_PARAMS,
    },
    {
        "name": "search_flights",
        "description": _SEARCH_FLIGHTS_DESCRIPTION,
        "input_schema": _SEARCH_FLIGHTS_PARAMS,
    },
    {
        "name": "get_airport_delays",
        "description": _GET_AIRPORT_DELAYS_DESCRIPTION,
        "input_schema": _GET_AIRPORT_DELAYS_PARAMS,
    },
    {
        "name": "get_airport_info",
        "description": _GET_AIRPORT_INFO_DESCRIPTION,
        "input_schema": _GET_AIRPORT_INFO_PARAMS,
    },
    {
        "name": "search_hotels",
        "description": _SEARCH_HOTELS_DESCRIPTION,
        "input_schema": _SEARCH_HOTELS_PARAMS,
    },
    {
        "name": "update_requirements",
        "description": _UPDATE_REQUIREMENTS_DESCRIPTION,
        "input_schema": _UPDATE_REQUIREMENTS_PARAMS,
    },
]

# ── OpenAI format (used by Qwen and other OpenAI-compatible providers) ──────

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "resolve_region",
            "description": _RESOLVE_REGION_DESCRIPTION,
            "parameters": _RESOLVE_REGION_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": _SEARCH_FLIGHTS_DESCRIPTION,
            "parameters": _SEARCH_FLIGHTS_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_airport_delays",
            "description": _GET_AIRPORT_DELAYS_DESCRIPTION,
            "parameters": _GET_AIRPORT_DELAYS_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_airport_info",
            "description": _GET_AIRPORT_INFO_DESCRIPTION,
            "parameters": _GET_AIRPORT_INFO_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": _SEARCH_HOTELS_DESCRIPTION,
            "parameters": _SEARCH_HOTELS_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_requirements",
            "description": _UPDATE_REQUIREMENTS_DESCRIPTION,
            "parameters": _UPDATE_REQUIREMENTS_PARAMS,
        },
    },
]
