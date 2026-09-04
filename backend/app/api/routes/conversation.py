from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.schemas.agentic import AgenticQueryRequest, AgenticQueryResponse, ConversationContext
from backend.app.agents.orchestrator import orchestrator, SESSION_CONTEXT_CACHE
from backend.app.agents.conversation_manager import conversation_manager

router = APIRouter(prefix="/conversation", tags=["Conversational Marine Intelligence"])

class ConversationalMessageRequest(BaseModel):
    message: str = Field(..., description="Natural language user query")
    session_id: str = Field("default_session", description="Unique conversation session identifier")
    language: Optional[str] = Field("en", description="Target language: en, hi, mr")
    context: Optional[ConversationContext] = None

@router.post("/message", response_model=AgenticQueryResponse, summary="Send message in multi-turn marine conversation")
async def send_conversational_message(request: ConversationalMessageRequest):
    """
    Processes a multi-turn conversational marine question.
    Resolves contextual pronouns, follow-ups, and time shifts before running multi-agent reasoning.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message text must not be empty.")

    response = await orchestrator.run(
        query=request.message,
        context=request.context,
        session_id=request.session_id,
        target_language=request.language
    )
    return response

@router.get("/{session_id}", summary="Get conversation history for a session")
async def get_session_history(session_id: str):
    """Returns chronological conversation history between user and ORCA."""
    history = conversation_manager.get_conversation_history(session_id)
    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": history
    }

@router.post("/{session_id}/clear", summary="Clear conversation history")
async def clear_session_history(session_id: str):
    """Clears conversational memory for a given session."""
    if session_id in SESSION_CONTEXT_CACHE:
        del SESSION_CONTEXT_CACHE[session_id]
    if session_id in conversation_manager._conversations:
        del conversation_manager._conversations[session_id]
    return {"status": "success", "message": f"Session '{session_id}' cleared."}
