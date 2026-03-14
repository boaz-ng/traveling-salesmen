from typing import Any, AsyncGenerator, Dict, List, Tuple

import pytest

from app.llm.agent_runner import run_agent_session, tool_search_flights
from app.schemas.flight import FlightOption, FlightSegment


class DummyMessage:
    """Minimal stand-in for Agent SDK message objects used in tests."""

    def __init__(self, result: str | None = None) -> None:
        self.result = result


async def _dummy_query(prompt: Any, options: Any) -> AsyncGenerator[DummyMessage, None]:
    """Fake query function that immediately yields a single result message."""
    _ = prompt, options  # unused in this simple stub
    yield DummyMessage(result="Test response from dummy agent")


@pytest.mark.asyncio
async def test_run_agent_session_uses_dummy_query(monkeypatch: pytest.MonkeyPatch) -> None:
    """run_agent_session should surface the final result text from the agent."""

    async def _run_with_dummy(messages: List[Dict[str, Any]]) -> Tuple[str, List[FlightOption] | None]:
        # Inline wrapper that swaps out the real query with our dummy implementation.
        from claude_agent_sdk import query as real_query  # type: ignore[unused-import]

        from app.llm import agent_runner

        async def _wrapped_query(*args: Any, **kwargs: Any):
            return _dummy_query(*args, **kwargs)

        monkeypatch.setattr(agent_runner, "query", _wrapped_query)
        return await agent_runner.run_agent_session(messages)

    text, flights = await _run_with_dummy(
        [{"role": "user", "content": "Find me a cheap flight."}]
    )

    assert "Test response from dummy agent" in text
    assert flights is None


@pytest.mark.asyncio
async def test_tool_search_flights_bridges_to_handle_tool_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """search_flights tool should delegate to handle_tool_call and return text."""
    from app.llm import agent_runner

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

    def fake_handle_tool_call(tool_name: str, tool_input: Dict[str, Any]):
        assert tool_name == "search_flights"
        assert "origin_airports" in tool_input
        return ("[{}]".format(dummy_flight.model_dump_json()), [dummy_flight])

    monkeypatch.setattr(agent_runner, "handle_tool_call", fake_handle_tool_call)

    result = await tool_search_flights(
        {
            "origin_airports": ["JFK"],
            "destination_airports": ["LAX"],
            "departure_date_start": "2025-01-01",
            "departure_date_end": "2025-01-02",
        }
    )

    assert "content" in result
    assert isinstance(result["content"], list)

