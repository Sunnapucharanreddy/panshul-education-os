from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = None
    # Optional focused-workspace routing. Omit to keep automatic classification.
    agent: Literal["teacher", "quiz", "career", "interview", "startup"] | None = None


class VideoResult(BaseModel):
    video_id: str
    title: str
    channel_title: str | None = None
    thumbnail_url: str | None = None
    url: str


class ChatResponse(BaseModel):
    session_id: str
    agent: str
    response: str
    videos: list[VideoResult] = Field(default_factory=list)
    video_search_status: str | None = None
