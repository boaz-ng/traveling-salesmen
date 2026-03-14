"""Contract tests — verify the interfaces between modules.

These tests ensure that the boundaries between team-owned modules stay
compatible.  Each test exercises a "seam" without calling external APIs,
so they run fast and can be executed by any team member.

Seams tested:
  • LLM ↔ Flights  (handle_tool_call produces what scoring/amadeus expect)
  • LLM ↔ Schemas  (tool schemas match FlightSearchIntent fields)
  • API ↔ Orchestrator (run_conversation signature & return shape)
  • Schemas ↔ Flights (FlightOption from amadeus_client is schema-valid)
"""

from datetime import date
from unittest.mock import patch

from app.flights.regions import resolve_region
from app.flights.scoring import score_flights
from app.llm.provider import handle_tool_call
from app.llm.tools import ANTHROPIC_TOOLS, OPENAI_TOOLS
from app.schemas.chat import ChatResponse
from app.schemas.flight import FlightOption, FlightSegment
from app.schemas.intent import FlightSearchIntent

# ── LLM ↔ Schemas contract ─────────────────────────────────────────────────


class TestLLMSchemasContract:
    """Tool schemas must stay in sync with FlightSearchIntent fields."""

    def _search_tool_properties(self, tools: list[dict], key: str) -> dict:
        """Extract the search_flights tool's parameter properties."""
        for t in tools:
            name = t.get("name") or t.get("function", {}).get("name")
            if name == "search_flights":
                schema = t.get("input_schema") or t.get("function", {}).get("parameters")
                return schema[key]
        raise AssertionError("search_flights tool not found")

    def test_anthropic_tool_covers_all_intent_fields(self):
        props = self._search_tool_properties(ANTHROPIC_TOOLS, "properties")
        for field_name in FlightSearchIntent.model_fields:
            assert field_name in props, f"Missing tool param for FlightSearchIntent.{field_name}"

    def test_openai_tool_covers_all_intent_fields(self):
        props = self._search_tool_properties(OPENAI_TOOLS, "properties")
        for field_name in FlightSearchIntent.model_fields:
            assert field_name in props, f"Missing tool param for FlightSearchIntent.{field_name}"

    def test_required_fields_match_intent(self):
        """The tool's required array should match the Intent fields that have no default."""
        required = self._search_tool_properties(ANTHROPIC_TOOLS, "required")
        for field_name, field_info in FlightSearchIntent.model_fields.items():
            if field_info.is_required():
                assert field_name in required, (
                    f"FlightSearchIntent.{field_name} is required but is not "
                    "listed as required in the tool schema"
                )


# ── LLM ↔ Flights contract ─────────────────────────────────────────────────


class TestLLMFlightsContract:
    """handle_tool_call → region resolver / scoring must produce valid data."""

    def test_resolve_region_returns_list_of_iata_strings(self):
        result_str, _ = handle_tool_call("resolve_region", {"region": "nyc"})
        import json

        data = json.loads(result_str)
        assert "airports" in data
        assert all(isinstance(c, str) and len(c) == 3 for c in data["airports"])

    @patch("app.llm.provider.search_flights")
    def test_search_tool_returns_schema_valid_flights(self, mock_search):
        seg = FlightSegment(
            airline="DL",
            flight_number="DL400",
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_time="2025-06-20T08:00:00",
            arrival_time="2025-06-20T11:00:00",
            duration="PT5H",
        )
        mock_search.return_value = [
            FlightOption(
                price=300.0,
                currency="USD",
                total_duration_minutes=300,
                stops=0,
                outbound_segments=[seg],
                airline="DL",
            )
        ]

        _, flights = handle_tool_call(
            "search_flights",
            {
                "origin_airports": ["JFK"],
                "destination_airports": ["LAX"],
                "departure_date_start": "2025-06-20",
                "departure_date_end": "2025-06-25",
            },
        )
        assert flights is not None
        for f in flights:
            # Must be a valid FlightOption (schema-valid)
            assert isinstance(f, FlightOption)
            assert f.price > 0
            assert f.score is not None  # scoring was applied


# ── Flights ↔ Schemas contract ──────────────────────────────────────────────


class TestFlightsSchemasContract:
    """Flight search layer must produce schema-valid objects."""

    def test_scoring_preserves_flight_option_validity(self):
        seg = FlightSegment(
            airline="UA",
            flight_number="UA200",
            departure_airport="SFO",
            arrival_airport="ORD",
            departure_time="2025-07-01T06:00:00",
            arrival_time="2025-07-01T12:00:00",
            duration="PT4H",
        )
        flights = [
            FlightOption(
                price=250.0, total_duration_minutes=240, stops=0,
                outbound_segments=[seg], airline="UA",
            ),
            FlightOption(
                price=180.0, total_duration_minutes=360, stops=1,
                outbound_segments=[seg, seg], airline="UA",
            ),
        ]
        scored = score_flights(flights, "balanced")
        for f in scored:
            # Re-validate by constructing a new FlightOption from the dict
            data = f.model_dump()
            FlightOption(**data)  # raises on invalid

    def test_region_resolver_output_usable_as_intent_airports(self):
        codes = resolve_region("northeast")
        # Codes must be usable as origin_airports in FlightSearchIntent
        intent = FlightSearchIntent(
            origin_airports=codes,
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        assert intent.origin_airports == codes


# ── API ↔ Orchestrator contract ─────────────────────────────────────────────


class TestAPIOrchestratorContract:
    """The chat router and orchestrator must agree on signatures."""

    def test_run_conversation_returns_expected_tuple(self):
        """Verify the return type expected by the chat router."""
        from app.llm.orchestrator import run_conversation
        from app.llm.provider import LLMProvider

        class FakeProvider(LLMProvider):
            def run_conversation(self, messages):
                messages.append({"role": "assistant", "content": "fake"})
                return "fake response", None

        with patch("app.llm.orchestrator._provider_instance", FakeProvider()):
            text, flights = run_conversation(
                [{"role": "user", "content": "hello"}]
            )
            assert isinstance(text, str)
            assert flights is None or isinstance(flights, list)

    def test_chat_response_accepts_orchestrator_output(self):
        """ChatResponse must be constructable from orchestrator return values."""
        text = "Here are your flights"
        seg = FlightSegment(
            airline="AA", flight_number="AA100",
            departure_airport="JFK", arrival_airport="MIA",
            departure_time="2025-06-20T08:00:00",
            arrival_time="2025-06-20T11:00:00",
            duration="PT3H",
        )
        flights = [
            FlightOption(
                price=300.0, total_duration_minutes=180, stops=0,
                outbound_segments=[seg], airline="AA", score=0.1,
            )
        ]
        # This mirrors exactly what the chat router does
        resp = ChatResponse(session_id="abc", response=text, flights=flights)
        assert resp.response == text
        assert resp.flights is not None
