from app.agents.base import BaseAgent


class InterviewAgent(BaseAgent):
    """Mock interviews + spoken English coaching with structured feedback."""
    name = "interview"
    temperature = 0.6
    max_tokens = 1200
