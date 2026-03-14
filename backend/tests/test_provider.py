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
    """Tests for the orchestrator's provider factory."""

    def test_factory_creates_qwen_provider(self):
        from app.llm import orchestrator

        orchestrator._provider_instance = None
        with patch("app.llm.orchestrator.settings") as mock_settings:
            mock_settings.llm_provider = "qwen"
            mock_settings.qwen_api_key = "test-key"
            mock_settings.qwen_base_url = ""
            mock_settings.llm_model = ""
            provider = orchestrator.get_provider()
            from app.llm.qwen_provider import QwenProvider

            assert isinstance(provider, QwenProvider)
        orchestrator._provider_instance = None

    def test_factory_creates_anthropic_provider(self):
        from app.llm import orchestrator

        orchestrator._provider_instance = None
        with patch("app.llm.orchestrator.settings") as mock_settings:
            mock_settings.llm_provider = "anthropic"
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = ""
            provider = orchestrator.get_provider()
            from app.llm.anthropic_provider import AnthropicProvider

            assert isinstance(provider, AnthropicProvider)
        orchestrator._provider_instance = None

    def test_factory_raises_on_unknown_provider(self):
        from app.llm import orchestrator

        orchestrator._provider_instance = None
        with patch("app.llm.orchestrator.settings") as mock_settings:
            mock_settings.llm_provider = "unknown"
            with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
                orchestrator.get_provider()
        orchestrator._provider_instance = None
