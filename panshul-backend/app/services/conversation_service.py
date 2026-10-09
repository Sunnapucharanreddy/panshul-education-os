"""The core use-case: one student message in -> orchestrated agent reply out.
Persists both turns, injects memory context, and records new memories."""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import Orchestrator
from app.agents.state import AgentState
from app.core.exceptions import NotFoundError
from app.repositories.session_repo import SessionRepository
from app.services.memory_service import MemoryService
from app.services.video_intent import requested_video_topic
from app.services.youtube_service import YouTubeSearchUnavailable, YouTubeService

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, db: AsyncSession, orchestrator: Orchestrator,
                 memory: MemoryService | None = None,
                 youtube: YouTubeService | None = None) -> None:
        self.sessions = SessionRepository(db)
        self.orchestrator = orchestrator
        self.memory = memory
        self.youtube = youtube or YouTubeService()

    async def list_sessions(self, user_id: str, limit: int = 30,
                            offset: int = 0) -> dict:
        items, has_more = await self.sessions.list_user_sessions(user_id, limit, offset)
        return {"items": items, "limit": limit, "offset": offset, "has_more": has_more}

    async def get_session_history(self, user_id: str, session_id: str,
                                  limit: int = 500, offset: int = 0) -> dict:
        history = await self.sessions.get_user_session_history(user_id, session_id, limit, offset)
        if history is None:
            raise NotFoundError("Conversation not found")
        return history

    async def send_message(self, user_id: str, message: str,
                           session_id: str | None = None,
                           agent: str | None = None) -> dict:
        session = await self.sessions.get_or_create_session(user_id, session_id)
        turns = await self.sessions.recent_turns(session.id, limit=10)

        history = [{"role": t.role, "content": t.content} for t in turns]
        video_topic = requested_video_topic(message, history)
        if video_topic is not None:
            videos: list[dict[str, str | None]] = []
            if not video_topic:
                video_status = "topic_required"
                response_text = "What topic would you like a YouTube video to explain?"
            else:
                try:
                    videos = await self.youtube.search(video_topic)
                    video_status = "success" if videos else "no_results"
                    response_text = (
                        f"Here are some YouTube explanations for {video_topic}."
                        if videos else f"I couldn't find a matching YouTube video for {video_topic}."
                    )
                except YouTubeSearchUnavailable:
                    video_status = "unavailable"
                    response_text = "YouTube video search is temporarily unavailable. Please try again later."

            await self.sessions.add_turn(session.id, "user", message)
            await self.sessions.add_turn(session.id, "assistant", response_text, agent="youtube")
            return {
                "session_id": session.id,
                "agent": "youtube",
                "response": response_text,
                "videos": videos,
                "video_search_status": video_status,
            }

        memory_context = "None yet"
        if self.memory is not None:
            # The embedder loads its model lazily, so an unavailable backend only
            # shows up here — recall is an enhancement, never a reason to fail.
            try:
                memory_context = await self.memory.recall(user_id, message)
            except Exception:
                logger.warning("Memory recall unavailable; continuing without it",
                               exc_info=True)

        state: AgentState = {
            "user_id": user_id,
            "session_id": session.id,
            "message": message,
            "history": history,
            "memory_context": memory_context,
        }
        if agent is not None:
            state["requested_intent"] = agent
        result = await self.orchestrator.handle(state)

        await self.sessions.add_turn(session.id, "user", message)
        await self.sessions.add_turn(session.id, "assistant",
                                     result["agent_response"], agent=result["intent"])
        return {
            "session_id": session.id,
            "agent": result["intent"],
            "response": result["agent_response"],
        }
