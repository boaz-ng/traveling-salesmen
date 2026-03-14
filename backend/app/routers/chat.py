"""POST /chat endpoint."""

from fastapi import APIRouter

from app.llm.orchestrator import run_conversation
from app.schemas.chat import ChatRequest, ChatResponse
from app.session import get_or_create_session

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle a chat message: retrieve session, run orchestrator, return response."""
    session_id, messages = get_or_create_session(request.session_id)

    messages.append({"role": "user", "content": request.message})

    response_text, flights = run_conversation(messages)

    return ChatResponse(
        session_id=session_id,
        response=response_text,
        flights=flights,
    )
