from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_conversation_service, get_current_user_id
from app.schemas.conversation import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["conversation"])


@router.post("", response_model=ChatResponse,
             summary="Send a message; the orchestrator routes it to the right agent")
async def chat(body: ChatRequest,
               user_id: Annotated[str, Depends(get_current_user_id)],
               svc: Annotated[ConversationService, Depends(get_conversation_service)]):
    return await svc.send_message(user_id, body.message, body.session_id, body.agent)


@router.get("/sessions", summary="List the authenticated student's conversations")
async def list_sessions(
    user_id: Annotated[str, Depends(get_current_user_id)],
    svc: Annotated[ConversationService, Depends(get_conversation_service)],
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await svc.list_sessions(user_id, limit, offset)


@router.get("/sessions/{session_id}", summary="Retrieve an owned conversation")
async def get_session_history(
    session_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    svc: Annotated[ConversationService, Depends(get_conversation_service)],
    limit: int = Query(500, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return await svc.get_session_history(user_id, session_id, limit, offset)
