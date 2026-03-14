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
]
