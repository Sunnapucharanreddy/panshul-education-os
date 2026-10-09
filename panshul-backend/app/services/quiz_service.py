"""Quiz generation (via QuizAgent JSON) and attempt scoring/recording."""
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.quiz import QuizAgent
from app.agents.state import AgentState
from app.core.exceptions import ProviderError
from app.repositories.session_repo import SessionRepository


def _parse_quiz(content: str) -> dict:
    """Accept raw JSON or a fenced ```json block from the model."""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        fence = text.rfind("```")
        if fence != -1:
            text = text[:fence]
        text = text.strip()
    return json.loads(text)


class QuizService:
    def __init__(self, db: AsyncSession, quiz_agent: QuizAgent) -> None:
        self.sessions = SessionRepository(db)
        self.agent = quiz_agent

    async def generate(self, user_id: str, topic: str,
                       difficulty: str = "medium", memory_context: str = "None yet") -> dict:
        state: AgentState = {
            "user_id": user_id,
            "message": f"Generate a {difficulty} quiz on: {topic}",
            "memory_context": memory_context,
        }
        result = await self.agent.run(state)
        try:
            quiz = _parse_quiz(result["agent_response"])
        except json.JSONDecodeError as exc:
            raise ProviderError("Quiz generation returned invalid JSON") from exc
        return quiz

    async def submit(self, user_id: str, topic: str, difficulty: str,
                     total: int, correct: int) -> dict:
        attempt = await self.sessions.record_quiz(user_id, topic, difficulty, total, correct)
        return {"attempt_id": attempt.id, "score_pct": attempt.score_pct}

    async def progress(self, user_id: str) -> dict:
        return await self.sessions.progress_summary(user_id)
