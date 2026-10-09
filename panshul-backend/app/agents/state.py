"""Shared conversation state that flows through the LangGraph orchestrator."""
from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_id: str
    session_id: str
    message: str                 # current user message
    history: list[dict]          # [{"role": ..., "content": ...}]
    memory_context: str          # retrieved student memory (RAG)
    intent: str                  # teacher | quiz | career | interview | startup | smalltalk
    requested_intent: str        # optional validated workspace override
    agent_response: str
    metadata: dict
