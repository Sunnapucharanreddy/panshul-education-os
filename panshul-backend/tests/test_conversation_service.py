from types import SimpleNamespace

import pytest

from app.services.conversation_service import ConversationService


class FakeSessions:
    def __init__(self):
        self.saved_turns = []

    async def get_or_create_session(self, user_id, session_id):
        return SimpleNamespace(id="session-1")

    async def recent_turns(self, session_id, limit=10):
        return []

    async def add_turn(self, *args, **kwargs):
        self.saved_turns.append((args, kwargs))


class FakeOrchestrator:
    def __init__(self):
        self.states = []

    async def handle(self, state):
        self.states.append(state)
        return {**state, "intent": state.get("requested_intent", "teacher"),
                "agent_response": "real agent response"}


class FakeYouTube:
    def __init__(self):
        self.topics = []

    async def search(self, topic):
        self.topics.append(topic)
        return [{
            "video_id": "result-id",
            "title": "A real search result fixture",
            "channel_title": "Video channel",
            "thumbnail_url": None,
            "url": "https://www.youtube.com/watch?v=result-id",
        }]


@pytest.mark.asyncio
async def test_explicit_workspace_agent_is_forwarded_to_existing_orchestrator():
    orchestrator = FakeOrchestrator()
    service = ConversationService(None, orchestrator)
    service.sessions = FakeSessions()

    response = await service.send_message("user-1", "Help me plan.", agent="career")

    assert orchestrator.states[0]["requested_intent"] == "career"
    assert response["agent"] == "career"
    assert response["response"] == "real agent response"


@pytest.mark.asyncio
async def test_youtube_video_intent_takes_precedence_over_workspace_selection():
    orchestrator = FakeOrchestrator()
    youtube = FakeYouTube()
    service = ConversationService(None, orchestrator, youtube=youtube)
    service.sessions = FakeSessions()

    response = await service.send_message(
        "user-1", "Give me a YouTube video explaining TCP congestion control.",
        agent="teacher",
    )

    assert youtube.topics == ["TCP congestion control"]
    assert response["agent"] == "youtube"
    assert response["video_search_status"] == "success"
    assert response["videos"][0]["video_id"] == "result-id"
    assert orchestrator.states == []
