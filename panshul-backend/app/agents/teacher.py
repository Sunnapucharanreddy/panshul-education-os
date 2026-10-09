from app.agents.base import BaseAgent


class TeacherAgent(BaseAgent):
    """Personalized AI teacher — uses student memory for adaptive explanations."""
    name = "teacher"
    temperature = 0.6
    max_tokens = 1400
