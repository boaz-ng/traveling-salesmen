# FlightSearchIntent Schema

The `FlightSearchIntent` is the **team contract** — the structured interface between the LLM interpretation layer and the flight search layer. It is defined as a Pydantic model in `backend/app/schemas/intent.py`.

## Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `origin_airports` | `list[str]` | ✅ | — | IATA airport codes for origin (e.g., `["JFK", "EWR", "LGA"]`) |
| `destination_airports` | `list[str]` | ✅ | — | IATA airport codes for destination |
| `departure_date_start` | `date` | ✅ | — | Start of departure date range |
| `departure_date_end` | `date` | ✅ | — | End of departure date range |
| `return_date_start` | `date \| None` | ❌ | `None` | Start of return date range (null for one-way) |
| `return_date_end` | `date \| None` | ❌ | `None` | End of return date range (null for one-way) |
| `max_budget_usd` | `float \| None` | ❌ | `None` | Maximum budget in USD |
| `max_stops` | `int \| None` | ❌ | `None` | Maximum number of stops allowed |
| `passengers` | `int` | ❌ | `1` | Number of passengers |
| `cabin_class` | `str` | ❌ | `"ECONOMY"` | One of: `ECONOMY`, `PREMIUM_ECONOMY`, `BUSINESS`, `FIRST` |
| `preference` | `str` | ❌ | `"balanced"` | Scoring preference: `"cost"`, `"comfort"`, or `"balanced"` |

## Example

```json
{
  "origin_airports": ["JFK", "EWR", "LGA"],
  "destination_airports": ["MIA", "FLL"],
  "departure_date_start": "2025-06-20",
  "departure_date_end": "2025-06-25",
  "return_date_start": "2025-06-27",
  "return_date_end": "2025-06-30",
  "max_budget_usd": 400.0,
  "max_stops": 1,
  "passengers": 1,
  "cabin_class": "ECONOMY",
  "preference": "cost"
}
```

## How It's Used

1. The **LLM orchestrator** interprets the user's natural language request
2. Claude constructs a `FlightSearchIntent` and passes it via the `search_flights` tool
3. The **Amadeus client** uses the intent to search for flights
4. The **scoring engine** uses the `preference` field to weight results

## Extending

When adding new search parameters:
1. Add the field to `FlightSearchIntent` in `backend/app/schemas/intent.py`
2. Update the tool schema in `backend/app/llm/tools.py`
3. Handle the new field in `backend/app/flights/amadeus_client.py`
4. Update this document
