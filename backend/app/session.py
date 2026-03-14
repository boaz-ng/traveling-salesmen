"""In-memory session store for chat message history."""

import uuid

sessions: dict[str, list[dict]] = {}


def get_or_create_session(session_id: str | None) -> tuple[str, list[dict]]:
    """Retrieve an existing session or create a new one.

    Returns (session_id, message_history).
    """
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    new_id = session_id or str(uuid.uuid4())
    sessions[new_id] = []
    return new_id, sessions[new_id]
