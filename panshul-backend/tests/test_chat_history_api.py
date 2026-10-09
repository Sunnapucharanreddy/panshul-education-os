import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_conversation_service, get_current_user_id
from app.db.base import Base
from app.db.models.learning import ChatSession, ChatTurn
from app.db.models.user import User
from app.main import app
from app.services.conversation_service import ConversationService


@pytest.fixture
async def history_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        db.add_all([
            User(id="student-a", phone="+10000000001"),
            User(id="student-b", phone="+10000000002"),
        ])
        await db.commit()
        yield db
    await engine.dispose()


@pytest.fixture
async def api_client(history_db):
    service = ConversationService(history_db, orchestrator=None)
    app.dependency_overrides[get_conversation_service] = lambda: service
    app.dependency_overrides[get_current_user_id] = lambda: "student-a"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_sessions_returns_only_current_student_and_paginates(api_client, history_db):
    owned = ChatSession(user_id="student-a")
    another_owned = ChatSession(user_id="student-a")
    third_owned = ChatSession(user_id="student-a")
    foreign = ChatSession(user_id="student-b")
    history_db.add_all([owned, another_owned, third_owned, foreign])
    await history_db.flush()
    history_db.add(ChatTurn(session_id=owned.id, role="user", content="  Explain   algebra "))
    history_db.add(ChatTurn(session_id=owned.id, role="assistant", content="Start with variables.", agent="teacher"))
    await history_db.commit()

    response = await api_client.get("/api/v1/chat/sessions?limit=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert all(item["session_id"] != foreign.id for item in body["items"])
    assert body["has_more"] is True
    full_list = (await api_client.get("/api/v1/chat/sessions?limit=10")).json()
    assert {item["session_id"] for item in full_list["items"]} == {owned.id, another_owned.id, third_owned.id}
    populated = next(item for item in full_list["items"] if item["session_id"] == owned.id)
    assert populated["title"] == "Explain algebra"
    assert populated["agent"] == "teacher"
    assert populated["message_count"] == 2


@pytest.mark.asyncio
async def test_session_detail_returns_turns_in_order_and_empty_history(api_client, history_db):
    populated = ChatSession(user_id="student-a")
    empty = ChatSession(user_id="student-a")
    history_db.add_all([populated, empty])
    await history_db.flush()
    history_db.add_all([
        ChatTurn(id="turn-1", session_id=populated.id, role="user", content="First"),
        ChatTurn(id="turn-2", session_id=populated.id, role="assistant", content="Second", agent="career"),
    ])
    await history_db.commit()

    partial = await api_client.get(f"/api/v1/chat/sessions/{populated.id}?limit=1")
    assert partial.status_code == 200
    assert len(partial.json()["messages"]) == 1
    assert partial.json()["has_more"] is True

    detail = await api_client.get(f"/api/v1/chat/sessions/{populated.id}")
    assert detail.status_code == 200
    assert [turn["id"] for turn in detail.json()["messages"]] == ["turn-1", "turn-2"]
    assert detail.json()["agent"] == "career"
    assert detail.json()["has_more"] is False

    empty_response = await api_client.get(f"/api/v1/chat/sessions/{empty.id}")
    assert empty_response.status_code == 200
    assert empty_response.json()["messages"] == []
    assert empty_response.json()["title"] == "New conversation"


@pytest.mark.asyncio
async def test_foreign_session_is_not_found(api_client, history_db):
    foreign = ChatSession(user_id="student-b")
    history_db.add(foreign)
    await history_db.flush()
    history_db.add(ChatTurn(session_id=foreign.id, role="user", content="Private content"))
    await history_db.commit()

    response = await api_client.get(f"/api/v1/chat/sessions/{foreign.id}")
    assert response.status_code == 404
    assert "Private content" not in response.text


@pytest.mark.asyncio
async def test_history_endpoints_require_authentication(api_client):
    app.dependency_overrides.pop(get_current_user_id, None)
    list_response = await api_client.get("/api/v1/chat/sessions")
    detail_response = await api_client.get("/api/v1/chat/sessions/unknown")
    assert list_response.status_code == 401
    assert detail_response.status_code == 401
