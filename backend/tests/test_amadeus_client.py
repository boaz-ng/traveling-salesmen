"""Tests for Amadeus client with mocked API responses."""

from datetime import date
from unittest.mock import MagicMock, patch

from app.flights.amadeus_client import _parse_duration_minutes, _parse_flight_offer, search_flights
from app.schemas.intent import FlightSearchIntent


class TestParseDuration:
    """Tests for ISO 8601 duration parsing."""

    def test_hours_and_minutes(self):
        assert _parse_duration_minutes("PT2H30M") == 150

    def test_hours_only(self):
        assert _parse_duration_minutes("PT5H") == 300

    def test_minutes_only(self):
        assert _parse_duration_minutes("PT45M") == 45

    def test_zero_duration(self):
        assert _parse_duration_minutes("PT0M") == 0


class TestParseFlightOffer:
    """Tests for parsing Amadeus flight offers."""

    def test_parse_one_way_offer(self):
        offer = {
            "price": {"total": "299.99", "currency": "USD"},
            "itineraries": [
                {
                    "duration": "PT5H30M",
                    "segments": [
                        {
                            "carrierCode": "AA",
                            "number": "100",
                            "departure": {"iataCode": "JFK", "at": "2025-06-20T08:00:00"},
                            "arrival": {"iataCode": "LAX", "at": "2025-06-20T11:30:00"},
                            "duration": "PT5H30M",
                        }
                    ],
                }
            ],
        }
        flight = _parse_flight_offer(offer)
        assert flight.price == 299.99
        assert flight.currency == "USD"
        assert flight.total_duration_minutes == 330
        assert flight.stops == 0
        assert flight.airline == "AA"
        assert len(flight.outbound_segments) == 1
        assert flight.return_segments is None

    def test_parse_round_trip_offer(self):
        offer = {
            "price": {"total": "450.00", "currency": "USD"},
            "itineraries": [
                {
                    "duration": "PT5H",
                    "segments": [
                        {
                            "carrierCode": "DL",
                            "number": "200",
                            "departure": {"iataCode": "JFK", "at": "2025-06-20T09:00:00"},
                            "arrival": {"iataCode": "MIA", "at": "2025-06-20T12:00:00"},
                            "duration": "PT3H",
                        }
                    ],
                },
                {
                    "duration": "PT3H15M",
                    "segments": [
                        {
                            "carrierCode": "DL",
                            "number": "201",
                            "departure": {"iataCode": "MIA", "at": "2025-06-27T14:00:00"},
                            "arrival": {"iataCode": "JFK", "at": "2025-06-27T17:15:00"},
                            "duration": "PT3H15M",
                        }
                    ],
                },
            ],
        }
        flight = _parse_flight_offer(offer)
        assert flight.price == 450.0
        assert flight.total_duration_minutes == 300 + 195
        assert flight.return_segments is not None
        assert len(flight.return_segments) == 1

    def test_parse_connecting_flight(self):
        offer = {
            "price": {"total": "199.99", "currency": "USD"},
            "itineraries": [
                {
                    "duration": "PT8H30M",
                    "segments": [
                        {
                            "carrierCode": "UA",
                            "number": "300",
                            "departure": {"iataCode": "JFK", "at": "2025-06-20T06:00:00"},
                            "arrival": {"iataCode": "ORD", "at": "2025-06-20T08:00:00"},
                            "duration": "PT2H",
                        },
                        {
                            "carrierCode": "UA",
                            "number": "301",
                            "departure": {"iataCode": "ORD", "at": "2025-06-20T10:00:00"},
                            "arrival": {"iataCode": "LAX", "at": "2025-06-20T12:30:00"},
                            "duration": "PT4H30M",
                        },
                    ],
                }
            ],
        }
        flight = _parse_flight_offer(offer)
        assert flight.stops == 1
        assert len(flight.outbound_segments) == 2


class TestSearchFlights:
    """Tests for the search_flights function with mocked Amadeus client."""

    @patch("app.flights.amadeus_client._get_client")
    def test_search_returns_parsed_results(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [
            {
                "price": {"total": "350.00", "currency": "USD"},
                "itineraries": [
                    {
                        "duration": "PT5H",
                        "segments": [
                            {
                                "carrierCode": "AA",
                                "number": "100",
                                "departure": {"iataCode": "JFK", "at": "2025-06-20T08:00:00"},
                                "arrival": {"iataCode": "MIA", "at": "2025-06-20T11:00:00"},
                                "duration": "PT3H",
                            }
                        ],
                    }
                ],
            }
        ]
        mock_client.shopping.flight_offers_search.get.return_value = mock_response

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

    @patch("app.flights.amadeus_client._get_client")
    def test_search_handles_api_error(self, mock_get_client):
        from amadeus import ResponseError

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.result = {"errors": [{"detail": "server error"}]}
        mock_client.shopping.flight_offers_search.get.side_effect = ResponseError(mock_resp)

        intent = FlightSearchIntent(
            origin_airports=["JFK"],
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        results = search_flights(intent)
        assert results == []

    @patch("app.flights.amadeus_client._get_client")
    def test_search_multiple_origins(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [
            {
                "price": {"total": "300.00", "currency": "USD"},
                "itineraries": [
                    {
                        "duration": "PT3H",
                        "segments": [
                            {
                                "carrierCode": "DL",
                                "number": "500",
                                "departure": {"iataCode": "JFK", "at": "2025-06-20T10:00:00"},
                                "arrival": {"iataCode": "MIA", "at": "2025-06-20T13:00:00"},
                                "duration": "PT3H",
                            }
                        ],
                    }
                ],
            }
        ]
        mock_client.shopping.flight_offers_search.get.return_value = mock_response

        intent = FlightSearchIntent(
            origin_airports=["JFK", "EWR"],
            destination_airports=["MIA"],
            departure_date_start=date(2025, 6, 20),
            departure_date_end=date(2025, 6, 25),
        )
        results = search_flights(intent)
        # Should call API twice (JFK→MIA and EWR→MIA)
        assert mock_client.shopping.flight_offers_search.get.call_count == 2
        assert len(results) == 2
