from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    difficulty: str = Field("medium", pattern=r"^(easy|medium|hard)$")


class QuizSubmitRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    total: int = Field(..., ge=1, le=50)
    correct: int = Field(..., ge=0)


class QuizSubmitResponse(BaseModel):
    attempt_id: str
    score_pct: float
