from typing import Any, AsyncGenerator

import pytest

from app.llm.agent_runner import run_agent_session
from app.llm.provider import handle_tool_call
from app.schemas.flight import FlightOption, FlightSegment


class DummyMessage:
    """Minimal stand-in for Agent SDK message objects used in tests."""

    def __init__(self, result: str | None = None) -> None:
        self.result = result


async def _dummy_query(prompt: Any, options: Any) -> AsyncGenerator[Any, None]:
    """Fake query function that yields a ResultMessage so run_agent_session sets assistant_text."""
    from claude_agent_sdk.types import ResultMessage

    _ = prompt, options  # unused in this simple stub
    yield ResultMessage(
        subtype="result",
        duration_ms=0,
        duration_api_ms=0,
        is_error=False,
        num_turns=1,
        session_id="test",
        result="Test response from dummy agent",
    )


@pytest.mark.asyncio
async def test_run_agent_session_uses_dummy_query(monkeypatch: pytest.MonkeyPatch) -> None:
    """run_agent_session should surface the final result text from the agent."""

    from app.llm import agent_runner

    monkeypatch.setattr(agent_runner, "query", _dummy_query)

    text, flights, parsed = await run_agent_session(
        [{"role": "user", "content": "Find me a cheap flight."}]
    )

    assert "Test response from dummy agent" in text
    assert flights is None
    assert parsed is None


def test_search_flights_handle_tool_call_returns_valid_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """search_flights via handle_tool_call returns (json_str, list[FlightOption])."""
    dummy_flight = FlightOption(
        price=100.0,
        currency="USD",
        total_duration_minutes=60,
        stops=0,
        outbound_segments=[
            FlightSegment(
                airline="TestAir",
                flight_number="TA123",
                departure_airport="JFK",
                arrival_airport="LAX",
                departure_time="2025-01-01T10:00:00",
                arrival_time="2025-01-01T13:00:00",
                duration="3h",
            )
        ],
        return_segments=None,
        score=0.9,
        airline="TestAir",
    )

    def fake_search(_intent):
        return [dummy_flight]

    # Patch where handle_tool_call imports it from
    monkeypatch.setattr("app.llm.provider.search_flights", fake_search)

    result_json, flights = handle_tool_call(
        "search_flights",
        {
            "origin_airports": ["JFK"],
            "destination_airports": ["LAX"],
            "departure_date_start": "2025-01-01",
            "departure_date_end": "2025-01-02",
        },
    )

    assert isinstance(result_json, str)
    assert isinstance(flights, list)
    assert len(flights) == 1
    assert isinstance(flights[0], FlightOption)
    assert flights[0].airline == "TestAir"

