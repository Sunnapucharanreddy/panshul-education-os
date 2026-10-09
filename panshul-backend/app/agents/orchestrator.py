"""LangGraph orchestrator: classify intent -> route to the right agent.

Graph:  classify ──► (teacher | quiz | career | interview | startup)
The router is itself an LLM call using the orchestrator prompt, with a
deterministic fallback to the teacher agent."""
import json
import logging

from langgraph.graph import END, StateGraph

from app.agents.career import CareerAgent
from app.agents.interview import InterviewAgent
from app.agents.quiz import QuizAgent
from app.agents.startup import StartupAgent
from app.agents.state import AgentState
from app.agents.teacher import TeacherAgent
from app.prompts.loader import get_prompt
from app.providers.base import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)

INTENTS = ("teacher", "quiz", "career", "interview", "startup")


class Orchestrator:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm
        self.agents = {
            "teacher": TeacherAgent(llm),
            "quiz": QuizAgent(llm),
            "career": CareerAgent(llm),
            "interview": InterviewAgent(llm),
            "startup": StartupAgent(llm),
        }
        self.graph = self._build()

    async def _classify(self, state: AgentState) -> AgentState:
        requested_intent = state.get("requested_intent")
        if requested_intent in INTENTS:
            state["intent"] = requested_intent
            return state

        system = get_prompt("orchestrator", "system")
        try:
            resp = await self.llm.chat(
                [ChatMessage(role="system", content=system),
                 ChatMessage(role="user", content=state["message"])],
                temperature=0.0, max_tokens=50, json_mode=True,
            )
            intent = json.loads(resp.content).get("intent", "teacher")
        except Exception:
            logger.warning("Intent classification failed, defaulting to teacher")
            intent = "teacher"
        state["intent"] = intent if intent in INTENTS else "teacher"
        return state

    def _build(self):
        g = StateGraph(AgentState)
        g.add_node("classify", self._classify)
        for name, agent in self.agents.items():
            g.add_node(name, agent.run)
            g.add_edge(name, END)
        g.set_entry_point("classify")
        g.add_conditional_edges("classify", lambda s: s["intent"],
                                {name: name for name in self.agents})
        return g.compile()

    async def handle(self, state: AgentState) -> AgentState:
        return await self.graph.ainvoke(state)
