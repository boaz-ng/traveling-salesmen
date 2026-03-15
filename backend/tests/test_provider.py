"""Tests for the LLM provider abstraction and orchestrator factory."""

from unittest.mock import patch

import pytest

from app.llm.provider import handle_tool_call
from app.llm.tools import ANTHROPIC_TOOLS, OPENAI_TOOLS


class TestHandleToolCall:
    """Tests for the shared handle_tool_call function."""

    def test_resolve_region_known(self):
        result_str, flights = handle_tool_call("resolve_region", {"region": "nyc"})
        assert flights is None
        assert "JFK" in result_str
        assert "EWR" in result_str

    def test_resolve_region_unknown(self):
        result_str, flights = handle_tool_call("resolve_region", {"region": "narnia"})
        assert flights is None
        assert "error" in result_str

    def test_unknown_tool(self):
        result_str, flights = handle_tool_call("unknown_tool", {})
        assert flights is None
        assert "Unknown tool" in result_str

    @patch("app.llm.provider.search_flights")
    def test_search_flights_tool(self, mock_search):
        from app.schemas.flight import FlightOption, FlightSegment

        mock_search.return_value = [
            FlightOption(
                price=300.0,
                currency="USD",
                total_duration_minutes=180,
                stops=0,
                outbound_segments=[
                    FlightSegment(
                        airline="AA",
                        flight_number="AA100",
                        departure_airport="JFK",
                        arrival_airport="MIA",
                        departure_time="2025-06-20T08:00:00",
                        arrival_time="2025-06-20T11:00:00",
                        duration="PT3H",
                    )
                ],
                airline="AA",
            )
        ]

        result_str, flights = handle_tool_call(
            "search_flights",
            {
                "origin_airports": ["JFK"],
                "destination_airports": ["MIA"],
                "departure_date_start": "2025-06-20",
                "departure_date_end": "2025-06-25",
            },
        )
        assert flights is not None
        assert len(flights) == 1
        assert flights[0].price == 300.0


class TestToolFormats:
    """Tests that both tool formats contain the same tools."""

    def test_anthropic_tools_has_both_tools(self):
        names = [t["name"] for t in ANTHROPIC_TOOLS]
        assert "resolve_region" in names
        assert "search_flights" in names

    def test_openai_tools_has_both_tools(self):
        names = [t["function"]["name"] for t in OPENAI_TOOLS]
        assert "resolve_region" in names
        assert "search_flights" in names

    def test_openai_tools_have_function_type(self):
        for tool in OPENAI_TOOLS:
            assert tool["type"] == "function"
            assert "function" in tool
            assert "parameters" in tool["function"]

    def test_schemas_match_between_formats(self):
        for at, ot in zip(ANTHROPIC_TOOLS, OPENAI_TOOLS):
            assert at["name"] == ot["function"]["name"]
            assert at["description"] == ot["function"]["description"]
            assert at["input_schema"] == ot["function"]["parameters"]


class TestProviderFactory:
    """Tests for the orchestrator's provider factory.

    The app now uses agent_runner.run_agent_session (Claude Agent SDK) instead of
    orchestrator.get_provider(). These tests are skipped; provider selection is
    only relevant when using the legacy direct-API path.
    """

    @pytest.mark.skip(reason="orchestrator no longer has get_provider(); app uses agent_runner")
    def test_factory_creates_qwen_provider(self):
        pass

    @pytest.mark.skip(reason="orchestrator no longer has get_provider(); app uses agent_runner")
    def test_factory_creates_anthropic_provider(self):
        pass

    @pytest.mark.skip(reason="orchestrator no longer has get_provider(); app uses agent_runner")
    def test_factory_raises_on_unknown_provider(self):
        pass
