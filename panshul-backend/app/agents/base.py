"""Base agent. Concrete agents supply a name (which selects their YAML prompt)
and optionally override build_messages / postprocess."""
import logging
from abc import ABC

from app.agents.state import AgentState
from app.prompts.loader import get_prompt
from app.providers.base import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str = "base"
    temperature: float = 0.7
    max_tokens: int = 1024

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def build_messages(self, state: AgentState) -> list[ChatMessage]:
        system = get_prompt(self.name, "system",
                            memory_context=state.get("memory_context", "None yet"))
        messages = [ChatMessage(role="system", content=system)]
        for turn in state.get("history", [])[-10:]:
            messages.append(ChatMessage(role=turn["role"], content=turn["content"]))
        messages.append(ChatMessage(role="user", content=state["message"]))
        return messages

    async def run(self, state: AgentState) -> AgentState:
        logger.info("agent=%s user=%s", self.name, state.get("user_id"))
        response = await self.llm.chat(
            self.build_messages(state),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        state["agent_response"] = self.postprocess(response.content, state)
        return state

    def postprocess(self, content: str, state: AgentState) -> str:
        return content
