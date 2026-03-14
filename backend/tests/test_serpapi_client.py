"""Tests for SerpApi Google Flights client with mocked API responses."""

from datetime import date
from unittest.mock import MagicMock, patch

from app.flights.serpapi_client import _parse_flight_offer, _parse_segment, search_flights
from app.schemas.intent import FlightSearchIntent


class TestParseSegment:
    """Tests for parsing individual SerpApi flight legs."""

    def test_parses_airline_code_from_flight_number(self):
        leg = {
            "flight_number": "AA 100",
            "departure_airport": {"id": "JFK", "time": "2025-06-20 08:00"},
            "arrival_airport": {"id": "LAX", "time": "2025-06-20 11:30"},
            "duration": 330,
        }
        segment = _parse_segment(leg)
        assert segment.airline == "AA"
        assert segment.flight_number == "AA100"
        assert segment.departure_airport == "JFK"
        assert segment.arrival_airport == "LAX"

    def test_handles_missing_fields(self):
        segment = _parse_segment({})
        assert segment.airline == ""
        assert segment.departure_airport == ""


class TestParseFlightOffer:
    """Tests for parsing SerpApi flight offers."""

    def test_parse_one_way_offer(self):
        offer = {
            "price": 299,
            "total_duration": 330,
            "flights": [
                {
                    "flight_number": "AA 100",
                    "departure_airport": {"id": "JFK", "time": "2025-06-20 08:00"},
                    "arrival_airport": {"id": "LAX", "time": "2025-06-20 11:30"},
                    "duration": 330,
                }
            ],
        }
        flight = _parse_flight_offer(offer)
        assert flight.price == 299.0
        assert flight.currency == "USD"
        assert flight.total_duration_minutes == 330
        assert flight.stops == 0
        assert flight.airline == "AA"
        assert len(flight.outbound_segments) == 1
        assert flight.return_segments is None

    def test_parse_connecting_flight(self):
        offer = {
            "price": 199,
            "total_duration": 510,
            "flights": [
                {
                    "flight_number": "UA 300",
                    "departure_airport": {"id": "JFK", "time": "2025-06-20 06:00"},
                    "arrival_airport": {"id": "ORD", "time": "2025-06-20 08:00"},
                    "duration": 120,
                },
                {
                    "flight_number": "UA 301",
                    "departure_airport": {"id": "ORD", "time": "2025-06-20 10:00"},
                    "arrival_airport": {"id": "LAX", "time": "2025-06-20 12:30"},
                    "duration": 270,
                },
            ],
        }
        flight = _parse_flight_offer(offer)
        assert flight.stops == 1
        assert len(flight.outbound_segments) == 2
        assert flight.total_duration_minutes == 510


class TestSearchFlights:
    """Tests for the search_flights function with mocked SerpApi."""

    @patch("app.flights.serpapi_client.serpapi.Client")
    def test_search_returns_parsed_results(self, mock_google_search):
        mock_search = MagicMock()
        mock_google_search.return_value = mock_search
        mock_search.search.return_value = {
            "best_flights": [
                {
                    "price": 350,
                    "total_duration": 300,
                    "flights": [
                        {
                            "flight_number": "AA 100",
                            "departure_airport": {"id": "JFK", "time": "2025-06-20 08:00"},
                            "arrival_airport": {"id": "MIA", "time": "2025-06-20 11:00"},
                            "duration": 180,
                        }
                    ],
                }
            ],
            "other_flights": [],
        }

        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        results = search_flights(intent)
        assert len(results) == 1
        assert results[0].price == 350.0
        assert results[0].airline == "AA"

    @patch("app.flights.serpapi_client.serpapi.Client")
    def test_search_handles_api_error(self, mock_google_search):
        mock_search = MagicMock()
        mock_google_search.return_value = mock_search
        mock_search.search.side_effect = Exception("API error")

        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        results = search_flights(intent)
        assert results == []

    @patch("app.flights.serpapi_client.serpapi.Client")
    def test_search_multiple_origins(self, mock_google_search):
        mock_search = MagicMock()
        mock_google_search.return_value = mock_search
        mock_search.search.return_value = {
            "best_flights": [
                {
                    "price": 300,
                    "total_duration": 180,
                    "flights": [
                        {
                            "flight_number": "DL 500",
                            "departure_airport": {"id": "JFK", "time": "2025-06-20 10:00"},
                            "arrival_airport": {"id": "MIA", "time": "2025-06-20 13:00"},
                            "duration": 180,
                        }
                    ],
                }
            ],
            "other_flights": [],
        }

        intent = FlightSearchIntent(
            origin_airports=["JFK", "EWR"],
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        results = search_flights(intent)
        # Should call API twice (JFK→MIA and EWR→MIA)
        assert mock_google_search.call_count == 2
        assert len(results) == 2

    @patch("app.flights.serpapi_client.serpapi.Client")
    def test_merges_best_and_other_flights(self, mock_google_search):
        mock_search = MagicMock()
        mock_google_search.return_value = mock_search
        mock_search.search.return_value = {
            "best_flights": [
                {
                    "price": 299,
                    "total_duration": 300,
                    "flights": [
                        {
                            "flight_number": "AA 1",
                            "departure_airport": {"id": "JFK", "time": "2025-06-20 08:00"},
                            "arrival_airport": {"id": "LAX", "time": "2025-06-20 11:00"},
                            "duration": 300,
                        }
                    ],
                }
            ],
            "other_flights": [
                {
                    "price": 399,
                    "total_duration": 360,
                    "flights": [
                        {
                            "flight_number": "UA 2",
                            "departure_airport": {"id": "JFK", "time": "2025-06-20 10:00"},
                            "arrival_airport": {"id": "LAX", "time": "2025-06-20 16:00"},
                            "duration": 360,
                        }
                    ],
                }
            ],
        }

        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["LAX"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        results = search_flights(intent)
        assert len(results) == 2
