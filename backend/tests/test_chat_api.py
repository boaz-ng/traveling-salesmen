"""Tests for the FastAPI chat endpoint and health check."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.session import sessions

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestChatEndpoint:
    """Tests for the POST /chat endpoint."""

    def setup_method(self):
        sessions.clear()

    @patch("app.routers.chat.run_agent_session")
    def test_chat_returns_response(self, mock_run):
        async def _ret(*args, **kwargs):
            return ("Hello! Where would you like to fly?", None, None)
        mock_run.side_effect = _ret

        response = client.post(
            "/chat",
            json={"message": "Hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["response"] == "Hello! Where would you like to fly?"
        assert data["flights"] is None

    @patch("app.routers.chat.run_agent_session")
    def test_chat_preserves_session_id(self, mock_run):
        async def _ret(*args, **kwargs):
            return ("Got it.", None, None)
        mock_run.side_effect = _ret

        response = client.post(
            "/chat",
            json={"session_id": "test-session", "message": "Hi"},
        )
        data = response.json()
        assert data["session_id"] == "test-session"

    @patch("app.routers.chat.run_agent_session")
    def test_chat_generates_session_id_when_missing(self, mock_run):
        async def _ret(*args, **kwargs):
            return ("Welcome!", None, None)
        mock_run.side_effect = _ret

        response = client.post(
            "/chat",
            json={"message": "Hi"},
        )
        data = response.json()
        assert data["session_id"]  # non-empty
        assert len(data["session_id"]) > 0

    @patch("app.routers.chat.run_agent_session")
    def test_chat_returns_flights_when_present(self, mock_run):
        from app.schemas.flight import FlightOption, FlightSegment

        flight = FlightOption(
            price=350.0,
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
            score=0.2,
            airline="AA",
        )

        async def _ret(*args, **kwargs):
            return ("Here are your options:", [flight], None)
        mock_run.side_effect = _ret

        response = client.post(
            "/chat",
            json={"message": "fly from NYC to Miami"},
        )
        data = response.json()
        assert data["flights"] is not None
        assert len(data["flights"]) == 1
        assert data["flights"][0]["price"] == 350.0
        assert data["flights"][0]["airline"] == "AA"

    @patch("app.routers.chat.run_agent_session", new_callable=AsyncMock)
    def test_chat_session_accumulates_messages(self, mock_run):
        # AsyncMock: each await returns the next side_effect value (the 3-tuple)
        mock_run.side_effect = [
            ("First response", None, None),
            ("Second response", None, None),
        ]

        resp1 = client.post("/chat", json={"session_id": "acc", "message": "msg1"})
        sid = resp1.json()["session_id"]

        client.post("/chat", json={"session_id": sid, "message": "msg2"})

        # Session should have user + assistant messages from both turns
        assert sid in sessions
        history = sessions[sid]
        user_msgs = [m for m in history if m.get("role") == "user"]
        assert len(user_msgs) == 2

    def test_chat_missing_message_returns_422(self):
        response = client.post("/chat", json={"session_id": "x"})
        assert response.status_code == 422

    def test_chat_empty_body_returns_422(self):
        response = client.post("/chat", json={})
        assert response.status_code == 422
