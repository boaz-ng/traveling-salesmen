"""Tests for flight scoring."""

from app.flights.scoring import score_flights
from app.schemas.flight import FlightOption, FlightSegment


def _make_flight(price: float, duration_minutes: int, stops: int) -> FlightOption:
    """Helper to create a FlightOption for testing."""
    return FlightOption(
        price=price,
        currency="USD",
        total_duration_minutes=duration_minutes,
        stops=stops,
        outbound_segments=[
            FlightSegment(
                airline="AA",
                flight_number="AA100",
                departure_airport="JFK",
                arrival_airport="LAX",
                departure_time="2025-06-20T08:00:00",
                arrival_time="2025-06-20T11:00:00",
                duration="PT5H",
            )
        ],
        airline="AA",
    )


class TestScoring:
    """Tests for the scoring function."""

    def test_empty_list(self):
        result = score_flights([], "balanced")
        assert result == []

    def test_single_flight_scores_zero(self):
        flights = [_make_flight(300.0, 180, 0)]
        scored = score_flights(flights, "balanced")
        assert len(scored) == 1
        assert scored[0].score == 0.0

    def test_cheapest_wins_with_cost_preference(self):
        flights = [
            _make_flight(500.0, 180, 0),
            _make_flight(200.0, 360, 2),
            _make_flight(350.0, 240, 1),
        ]
        scored = score_flights(flights, "cost")
        assert scored[0].price == 200.0

    def test_fastest_wins_with_comfort_preference(self):
        flights = [
            _make_flight(200.0, 600, 2),
            _make_flight(500.0, 180, 0),
            _make_flight(350.0, 300, 1),
        ]
        scored = score_flights(flights, "comfort")
        # Direct flight with shortest duration should win with comfort preference
        assert scored[0].price == 500.0
        assert scored[0].stops == 0

    def test_balanced_preference(self):
        flights = [
            _make_flight(200.0, 600, 2),
            _make_flight(500.0, 180, 0),
            _make_flight(300.0, 240, 1),
        ]
        scored = score_flights(flights, "balanced")
        # All flights should have scores
        assert all(f.score is not None for f in scored)
        # Should be sorted by score ascending
        for i in range(len(scored) - 1):
            assert scored[i].score <= scored[i + 1].score

    def test_scores_are_normalized(self):
        flights = [
            _make_flight(200.0, 180, 0),
            _make_flight(800.0, 720, 3),
        ]
        scored = score_flights(flights, "balanced")
        # Best flight should score 0.0, worst should score 1.0
        assert scored[0].score == 0.0
        assert scored[1].score == 1.0

    def test_unknown_preference_defaults_to_balanced(self):
        flights = [
            _make_flight(300.0, 240, 1),
            _make_flight(200.0, 360, 2),
        ]
        scored = score_flights(flights, "unknown")
        # Should not crash, should use balanced weights
        assert all(f.score is not None for f in scored)

    def test_identical_flights_score_zero(self):
        flights = [
            _make_flight(300.0, 240, 1),
            _make_flight(300.0, 240, 1),
        ]
        scored = score_flights(flights, "balanced")
        assert scored[0].score == 0.0
        assert scored[1].score == 0.0
