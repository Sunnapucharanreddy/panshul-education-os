from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id, get_quiz_service
from app.schemas.quiz import QuizGenerateRequest, QuizSubmitRequest, QuizSubmitResponse
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/generate", summary="Generate an adaptive quiz")
async def generate(body: QuizGenerateRequest,
                   user_id: Annotated[str, Depends(get_current_user_id)],
                   svc: Annotated[QuizService, Depends(get_quiz_service)]):
    return await svc.generate(user_id, body.topic, body.difficulty)


@router.post("/submit", response_model=QuizSubmitResponse)
async def submit(body: QuizSubmitRequest,
                 user_id: Annotated[str, Depends(get_current_user_id)],
                 svc: Annotated[QuizService, Depends(get_quiz_service)]):
    return await svc.submit(user_id, body.topic, body.difficulty, body.total, body.correct)


@router.get("/progress", summary="Per-topic learning analytics")
async def progress(user_id: Annotated[str, Depends(get_current_user_id)],
                   svc: Annotated[QuizService, Depends(get_quiz_service)]):
    return await svc.progress(user_id)
