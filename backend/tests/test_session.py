"""Tests for in-memory session store."""

from app.session import get_or_create_session, sessions


class TestGetOrCreateSession:
    """Tests for session creation and retrieval."""

    def setup_method(self):
        """Clear the session store before each test."""
        sessions.clear()

    def test_create_new_session_with_no_id(self):
        session_id, history = get_or_create_session(None)
        assert session_id  # non-empty string
        assert isinstance(session_id, str)
        assert history == []

    def test_new_session_generates_uuid(self):
        session_id, _ = get_or_create_session(None)
        # UUID4 format: 8-4-4-4-12 hex chars
        parts = session_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8

    def test_create_session_with_provided_id(self):
        session_id, history = get_or_create_session("my-session")
        assert session_id == "my-session"
        assert history == []

    def test_retrieve_existing_session(self):
        session_id, history = get_or_create_session("sess-1")
        history.append({"role": "user", "content": "hello"})

        retrieved_id, retrieved_history = get_or_create_session("sess-1")
        assert retrieved_id == "sess-1"
        assert len(retrieved_history) == 1
        assert retrieved_history[0]["content"] == "hello"

    def test_different_sessions_are_isolated(self):
        _, history_a = get_or_create_session("a")
        _, history_b = get_or_create_session("b")

        history_a.append({"role": "user", "content": "message for a"})

        assert len(history_a) == 1
        assert len(history_b) == 0

    def test_session_stored_in_global_dict(self):
        session_id, _ = get_or_create_session("stored")
        assert session_id in sessions

    def test_history_is_mutable_reference(self):
        """The returned list should be the same object stored in sessions."""
        session_id, history = get_or_create_session("ref-test")
        history.append({"role": "user", "content": "test"})
        assert sessions[session_id] is history
        assert len(sessions[session_id]) == 1

    def test_unknown_id_creates_new_session_with_that_id(self):
        session_id, history = get_or_create_session("brand-new-id")
        assert session_id == "brand-new-id"
        assert history == []
        assert "brand-new-id" in sessions
