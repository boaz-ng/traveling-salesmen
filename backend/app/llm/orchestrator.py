"""Legacy orchestrator shim kept for backwards compatibility.

The main FastAPI router now uses ``app.llm.agent_runner.run_agent_session``
directly. This module simply delegates there so any remaining imports of
``run_conversation`` continue to work.
"""

from app.llm.agent_runner import run_agent_session
from app.schemas.flight import FlightOption


async def run_conversation(
    messages: list[dict],
) -> tuple[str, list[FlightOption] | None]:
    """Backward-compatible wrapper around ``run_agent_session``."""
    return await run_agent_session(messages)
