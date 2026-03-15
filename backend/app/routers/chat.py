"""POST /chat endpoint."""

from fastapi import APIRouter

from app.llm.agent_runner import run_agent_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.session import get_or_create_session

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle a chat message: retrieve session, run orchestrator, return response."""
    session_id, messages = get_or_create_session(request.session_id)

    messages.append({"role": "user", "content": request.message})

    response_text, flights, hotels, parsed_requirements = await run_agent_session(
        messages, origin_missing=request.origin_missing
    )

    return ChatResponse(
        session_id=session_id,
        response=response_text,
        flights=flights,
        hotels=hotels,
        parsed_intent=parsed_requirements,
    )
