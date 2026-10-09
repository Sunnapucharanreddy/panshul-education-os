from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.learning import ChatSession, ChatTurn, QuizAttempt


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_session(self, user_id: str, session_id: str | None) -> ChatSession:
        if session_id:
            session = await self.db.get(ChatSession, session_id)
            if session and session.user_id == user_id:
                return session
        session = ChatSession(user_id=user_id)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def add_turn(self, session_id: str, role: str, content: str,
                       agent: str | None = None) -> None:
        self.db.add(ChatTurn(session_id=session_id, role=role, content=content, agent=agent))
        await self.db.commit()

    async def recent_turns(self, session_id: str, limit: int = 10) -> list[ChatTurn]:
        res = await self.db.execute(
            select(ChatTurn).where(ChatTurn.session_id == session_id)
            .order_by(ChatTurn.created_at.desc()).limit(limit)
        )
        return list(reversed(res.scalars().all()))

    async def list_user_sessions(self, user_id: str, limit: int = 30,
                                 offset: int = 0) -> tuple[list[dict], bool]:
        last_activity = (
            select(func.max(ChatTurn.created_at))
            .where(ChatTurn.session_id == ChatSession.id)
            .correlate(ChatSession).scalar_subquery()
        )
        sessions_result = await self.db.execute(
            select(ChatSession).where(ChatSession.user_id == user_id)
            .order_by(func.coalesce(last_activity, ChatSession.created_at).desc(),
                      ChatSession.id.desc())
            .offset(offset).limit(limit + 1)
        )
        sessions = list(sessions_result.scalars().all())
        has_more = len(sessions) > limit
        sessions = sessions[:limit]
        if not sessions:
            return [], has_more

        session_ids = [session.id for session in sessions]
        turns_result = await self.db.execute(
            select(ChatTurn).where(ChatTurn.session_id.in_(session_ids))
            .order_by(ChatTurn.created_at.asc(), ChatTurn.id.asc())
        )
        turns_by_session: dict[str, list[ChatTurn]] = {session_id: [] for session_id in session_ids}
        for turn in turns_result.scalars().all():
            turns_by_session[turn.session_id].append(turn)

        items = []
        for session in sessions:
            turns = turns_by_session[session.id]
            first_user = next((turn.content for turn in turns if turn.role == "user"), None)
            last_turn = turns[-1] if turns else None
            inferred_agent = next((turn.agent for turn in turns
                                   if turn.role == "assistant" and turn.agent), None)
            items.append({
                "session_id": session.id,
                "created_at": session.created_at,
                "updated_at": last_turn.created_at if last_turn else session.created_at,
                "agent": inferred_agent or session.agent or "teacher",
                "title": _preview(first_user, 90) or "New conversation",
                "preview": _preview(last_turn.content if last_turn else first_user, 140),
                "message_count": len(turns),
            })
        return items, has_more

    async def get_user_session_history(self, user_id: str, session_id: str,
                                       limit: int = 500, offset: int = 0) -> dict | None:
        # Ownership is checked in the query itself; a foreign session is indistinguishable
        # from a missing one and its turns are never queried.
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id,
                                      ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if session is None:
            return None

        count_result = await self.db.execute(
            select(func.count()).select_from(ChatTurn).where(ChatTurn.session_id == session.id)
        )
        total = int(count_result.scalar_one())
        turns_result = await self.db.execute(
            select(ChatTurn).where(ChatTurn.session_id == session.id)
            .order_by(ChatTurn.created_at.asc(), ChatTurn.id.asc())
            .offset(offset).limit(limit)
        )
        turns = list(turns_result.scalars().all())
        first_user = next((turn.content for turn in turns if turn.role == "user"), None)
        inferred_agent = next((turn.agent for turn in turns
                               if turn.role == "assistant" and turn.agent), None)
        return {
            "session_id": session.id,
            "created_at": session.created_at,
            "updated_at": turns[-1].created_at if turns else session.created_at,
            "agent": inferred_agent or session.agent or "teacher",
            "title": _preview(first_user, 90) or "New conversation",
            "total_messages": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(turns) < total,
            "messages": [{
                "id": turn.id,
                "role": turn.role,
                "content": turn.content,
                "agent": turn.agent,
                "created_at": turn.created_at,
            } for turn in turns],
        }

    async def record_quiz(self, user_id: str, topic: str, difficulty: str,
                          total: int, correct: int) -> QuizAttempt:
        attempt = QuizAttempt(user_id=user_id, topic=topic, difficulty=difficulty,
                              total=total, correct=correct,
                              score_pct=round(100 * correct / max(total, 1), 1))
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)
        return attempt

    async def progress_summary(self, user_id: str) -> dict:
        res = await self.db.execute(
            select(QuizAttempt.topic,
                   func.count().label("attempts"),
                   func.avg(QuizAttempt.score_pct).label("avg_score"))
            .where(QuizAttempt.user_id == user_id)
            .group_by(QuizAttempt.topic)
        )
        rows = res.all()
        return {
            "topics": [
                {"topic": r.topic, "attempts": r.attempts,
                 "avg_score": round(float(r.avg_score), 1)}
                for r in rows
            ]
        }


def _preview(value: str | None, max_length: int) -> str:
    if not value:
        return ""
    clean = " ".join(value.split())
    return clean if len(clean) <= max_length else clean[:max_length - 1].rstrip() + "…"
