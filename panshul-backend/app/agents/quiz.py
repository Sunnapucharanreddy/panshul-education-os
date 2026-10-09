from app.agents.base import BaseAgent


class QuizAgent(BaseAgent):
    """Generates adaptive quizzes as strict JSON (parsed by QuizService)."""
    name = "quiz"
    temperature = 0.4
    max_tokens = 1600
