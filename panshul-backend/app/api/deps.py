"""Dependency wiring — composition root for requests."""
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import Orchestrator
from app.agents.quiz import QuizAgent
from app.core.config import get_settings
from app.core.security import decode_token
from app.db.session import get_db
from app.providers.registry import get_embedder, get_llm, get_vector_store
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.otp_service import OTPService
from app.services.quiz_service import QuizService
from app.services.youtube_service import YouTubeService

_bearer = HTTPBearer(auto_error=True)
_redis: redis.Redis | None = None
_orchestrator: Orchestrator | None = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator(get_llm())
    return _orchestrator


async def get_current_user_id(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> str:
    return decode_token(creds.credentials, expected_type="access")


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(db, OTPService(get_redis()))


def get_memory_service() -> MemoryService:
    return MemoryService(get_embedder(), get_vector_store())


def get_conversation_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationService:
    # Memory is optional in dev (no GPU): degrade gracefully.
    try:
        memory = get_memory_service()
    except Exception:
        memory = None
    return ConversationService(
        db, get_orchestrator(), memory,
        youtube=YouTubeService(get_settings().youtube_api_key),
    )


def get_quiz_service(db: Annotated[AsyncSession, Depends(get_db)]) -> QuizService:
    return QuizService(db, QuizAgent(get_llm()))
