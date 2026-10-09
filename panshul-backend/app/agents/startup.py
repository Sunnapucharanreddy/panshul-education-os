from app.agents.base import BaseAgent


class StartupAgent(BaseAgent):
    """Startup mentorship — idea validation, MVP planning, pitch feedback."""
    name = "startup"
    temperature = 0.7
    max_tokens = 1400
