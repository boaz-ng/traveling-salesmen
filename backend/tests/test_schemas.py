"""Tests for Pydantic schema models."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.flight import FlightOption, FlightSegment
from app.schemas.intent import FlightSearchIntent

# ── FlightSearchIntent ──────────────────────────────────────────────────────


class TestFlightSearchIntent:
    """Tests for the FlightSearchIntent schema."""

    def test_minimal_valid_intent(self):
        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        assert intent.origin_airports == ["JFK"]
        assert intent.passengers == 1
        assert intent.cabin_class == "ECONOMY"
        assert intent.preference == "balanced"
        assert intent.return_date_start is None
        assert intent.max_budget_usd is None
        assert intent.max_stops is None

    def test_full_intent(self):
        intent = FlightSearchIntent(
            origin_airports=["JFK", "EWR"],
            destination_airports=["MIA", "FLL"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
            return_date_start=date(2025, 6, 27),
            return_date_end=date(2025, 6, 30),
            max_budget_usd=400.0,
            max_stops=1,
            passengers=2,
            cabin_class="BUSINESS",
            preference="cost",
        )
        assert intent.max_budget_usd == 400.0
        assert intent.passengers == 2
        assert intent.cabin_class == "BUSINESS"
        assert intent.preference == "cost"
        assert intent.return_date_start == date(2025, 6, 27)

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            FlightSearchIntent(
                origin_airports=["JFK"],
                # missing destination_airports, departure dates
            )

    def test_date_string_coercion(self):
        """Pydantic should coerce ISO date strings to date objects."""
        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["LAX"],
            departure_date_start="2025-06-20",
            departure_date_end="2025-06-25",
        )
        assert intent.departure_date_start == date(2025, 6, 20)

    def test_serialization_round_trip(self):
        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["LAX"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        data = intent.model_dump()
        restored = FlightSearchIntent(**data)
        assert restored == intent


# ── FlightSegment / FlightOption ────────────────────────────────────────────


class TestFlightModels:
    """Tests for flight result models."""

    def _make_segment(self) -> FlightSegment:
        return FlightSegment(
            airline="AA",
            flight_number="AA100",
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_time="2025-06-20T08:00:00",
            arrival_time="2025-06-20T11:00:00",
            duration="PT5H",
        )

    def test_flight_segment_fields(self):
        seg = self._make_segment()
        assert seg.airline == "AA"
        assert seg.departure_airport == "JFK"
        assert seg.arrival_airport == "LAX"

    def test_flight_option_minimal(self):
        seg = self._make_segment()
        option = FlightOption(
            price=299.99,
            total_duration_minutes=300,
            stops=0,
            outbound_segments=[seg],
        )
        assert option.price == 299.99
        assert option.currency == "USD"
        assert option.score is None
        assert option.return_segments is None
        assert option.airline == ""

    def test_flight_option_with_score(self):
        seg = self._make_segment()
        option = FlightOption(
            price=350.0,
            total_duration_minutes=300,
            stops=1,
            outbound_segments=[seg],
            score=0.45,
            airline="AA",
        )
        assert option.score == 0.45
        assert option.airline == "AA"

    def test_flight_option_serialization(self):
        seg = self._make_segment()
        option = FlightOption(
            price=400.0,
            total_duration_minutes=360,
            stops=1,
            outbound_segments=[seg],
            return_segments=[seg],
            score=0.5,
            airline="DL",
        )
        data = option.model_dump()
        assert data["price"] == 400.0
        assert len(data["outbound_segments"]) == 1
        assert len(data["return_segments"]) == 1
        restored = FlightOption(**data)
        assert restored == option


# ── ChatRequest / ChatResponse ──────────────────────────────────────────────


class TestChatModels:
    """Tests for chat request/response models."""

    def test_chat_request_with_session(self):
        req = ChatRequest(session_id="abc-123", message="find flights")
        assert req.session_id == "abc-123"
        assert req.message == "find flights"

    def test_chat_request_without_session(self):
        req = ChatRequest(message="hello")
        assert req.session_id is None

    def test_chat_request_missing_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_response_without_flights(self):
        resp = ChatResponse(
            session_id="abc",
            response="How can I help?",
        )
        assert resp.flights is None

    def test_chat_response_with_flights(self):
        seg = FlightSegment(
            airline="UA",
            flight_number="UA500",
            departure_airport="SFO",
            arrival_airport="JFK",
            departure_time="2025-07-01T06:00:00",
            arrival_time="2025-07-01T14:30:00",
            duration="PT5H30M",
        )
        flight = FlightOption(
            price=250.0,
            total_duration_minutes=330,
            stops=0,
            outbound_segments=[seg],
            score=0.1,
            airline="UA",
        )
        resp = ChatResponse(
            session_id="abc",
            response="Here are your flights",
            flights=[flight],
        )
        assert resp.flights is not None
        assert len(resp.flights) == 1
        assert resp.flights[0].price == 250.0

    def test_chat_response_serialization(self):
        resp = ChatResponse(
            session_id="xyz",
            response="test",
            flights=None,
        )
        data = resp.model_dump()
        assert data["session_id"] == "xyz"
        assert data["flights"] is None
