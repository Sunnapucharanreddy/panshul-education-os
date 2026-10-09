from app.agents.base import BaseAgent


class CareerAgent(BaseAgent):
    """Career guidance and roadmap generation."""
    name = "career"
    temperature = 0.7
    max_tokens = 1600
