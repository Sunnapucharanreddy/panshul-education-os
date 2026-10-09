"""Orchestrator routing tests with a fake LLM — no model server needed."""
import pytest

from app.agents.orchestrator import Orchestrator
from app.providers.base import ChatMessage, LLMProvider, LLMResponse


class FakeLLM(LLMProvider):
    def __init__(self, intent: str = "quiz"):
        self.intent = intent
        self.calls: list[list[ChatMessage]] = []

    async def chat(self, messages, *, temperature=0.7, max_tokens=1024, json_mode=False):
        self.calls.append(messages)
        if json_mode:
            return LLMResponse(content=f'{{"intent": "{self.intent}"}}', model="fake")
        return LLMResponse(content="agent reply", model="fake")

    async def stream(self, messages, *, temperature=0.7, max_tokens=1024):
        yield "agent reply"


@pytest.mark.asyncio
async def test_routes_to_classified_agent():
    llm = FakeLLM(intent="career")
    result = await Orchestrator(llm).handle(
        {"user_id": "u1", "message": "What should I study after 12th?",
         "history": [], "memory_context": "None yet"}
    )
    assert result["intent"] == "career"
    assert result["agent_response"] == "agent reply"


@pytest.mark.asyncio
async def test_unknown_intent_falls_back_to_teacher():
    llm = FakeLLM(intent="nonsense")
    result = await Orchestrator(llm).handle(
        {"user_id": "u1", "message": "hello", "history": [], "memory_context": "None yet"}
    )
    assert result["intent"] == "teacher"


@pytest.mark.asyncio
@pytest.mark.parametrize("intent", ["teacher", "career", "interview", "startup"])
async def test_explicit_workspace_agent_skips_classifier(intent):
    llm = FakeLLM(intent="teacher")
    result = await Orchestrator(llm).handle(
        {"user_id": "u1", "message": "Help me get started.", "requested_intent": intent,
         "history": [], "memory_context": "None yet"}
    )
    assert result["intent"] == intent
    # Only the selected agent makes an LLM request; routing did not make a classifier call.
    assert len(llm.calls) == 1
    assert llm.calls[0][0].role == "system"
