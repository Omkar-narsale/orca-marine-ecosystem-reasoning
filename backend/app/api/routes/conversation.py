from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.schemas.agentic import AgenticQueryRequest, AgenticQueryResponse, ConversationContext, LocationPayload
from backend.app.agents.orchestrator import orchestrator, SESSION_CONTEXT_CACHE
from backend.app.agents.conversation_manager import conversation_manager
from backend.app.services.state.result_registry import result_registry
from backend.app.core.tracing import generate_request_id

router = APIRouter(prefix="/conversation", tags=["Conversational Marine Intelligence"])

class ConversationalMessageRequest(BaseModel):
    message: str = Field(..., description="Natural language user query")
    session_id: Optional[str] = Field("default_session", description="Unique conversation session identifier")
    conversation_id: Optional[str] = Field(None, description="Alias for session_id")
    language: Optional[str] = Field("en", description="Target language: en, hi, mr")
    location: Optional[LocationPayload] = Field(None, description="Live browser / device geolocation payload")
    context: Optional[ConversationContext] = None
    request_id: Optional[str] = None
    is_demo_mode: bool = False

@router.post("/message", response_model=AgenticQueryResponse, summary="Send message in multi-turn marine conversation")
async def send_conversational_message(request: ConversationalMessageRequest):
    """
    Processes a multi-turn conversational marine question.
    Resolves contextual pronouns, follow-ups, and time shifts before running multi-agent reasoning.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message text must not be empty.")

    sess_id = request.conversation_id or request.session_id or "default_session"
    req_id = request.request_id or generate_request_id()

    ctx = request.context
    if request.location:
        if not ctx:
            ctx = ConversationContext(conversation_id=sess_id, live_location=request.location)
        else:
            ctx.live_location = request.location

    response = await orchestrator.run(
        query=request.message,
        context=ctx,
        session_id=sess_id,
        target_language=request.language,
        request_id=req_id,
        is_demo_mode=request.is_demo_mode
    )
    return response

@router.get("/sessions", summary="Get all conversational sessions")
async def get_all_sessions():
    """Returns all conversation sessions with metadata for conversation history sidebar."""
    return conversation_manager.get_all_sessions()

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
    """Clears conversational memory, result registry, and database records for a given session."""
    # Clear orchestrator session context cache
    if session_id in SESSION_CONTEXT_CACHE:
        del SESSION_CONTEXT_CACHE[session_id]
    # Clear conversation manager (in-memory + DB)
    conversation_manager.clear_session(session_id)
    # Clear result registry (in-memory)
    result_registry.clear_session(session_id)
    return {"status": "success", "message": f"Session '{session_id}' cleared from memory and database."}

