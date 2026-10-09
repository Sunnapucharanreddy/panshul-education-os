from fastapi import APIRouter

from app.api.v1 import auth, conversation, quiz, voice

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(conversation.router)
api_router.include_router(quiz.router)
api_router.include_router(voice.router)
