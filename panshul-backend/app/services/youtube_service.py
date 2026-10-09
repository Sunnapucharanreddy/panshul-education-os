"""Backend-only client for YouTube Data API v3 video search."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeSearchUnavailable(Exception):
    """Raised when YouTube search cannot be completed safely."""


class YouTubeService:
    """Search YouTube for real videos without exposing the API key to clients."""

    def __init__(self, api_key: str = "", transport: httpx.AsyncBaseTransport | None = None):
        self.api_key = api_key.strip()
        self.transport = transport

    async def search(self, topic: str, max_results: int = 3) -> list[dict[str, str | None]]:
        topic = topic.strip()
        if not topic:
            return []
        if not self.api_key:
            raise YouTubeSearchUnavailable("YouTube video search is temporarily unavailable.")

        params = {
            "part": "snippet",
            "q": f"{topic} explanation",
            "type": "video",
            "maxResults": min(max_results, 3),
            "safeSearch": "moderate",
            "key": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, transport=self.transport) as client:
                response = await client.get(YOUTUBE_SEARCH_URL, params=params)
            response.raise_for_status()
            data: Any = response.json()
        except (httpx.HTTPError, ValueError):
            # Avoid logging exception text: request URLs can contain the API key.
            logger.warning("YouTube Data API search request failed")
            raise YouTubeSearchUnavailable(
                "YouTube video search is temporarily unavailable."
            ) from None

        if not isinstance(data, dict):
            raise YouTubeSearchUnavailable("YouTube returned an invalid response.")

        videos: list[dict[str, str | None]] = []
        items = data.get("items", [])
        if not isinstance(items, list):
            return videos
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            snippet = item.get("snippet")
            if not isinstance(item_id, dict) or not isinstance(snippet, dict):
                continue
            video_id = item_id.get("videoId")
            if not video_id or not snippet.get("title"):
                continue
            thumbnails = snippet.get("thumbnails", {})
            if not isinstance(thumbnails, dict):
                thumbnails = {}
            thumbnail = next(
                (candidate.get("url") for size in ("high", "medium", "default")
                 if isinstance((candidate := thumbnails.get(size)), dict) and candidate.get("url")),
                None,
            )
            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "channel_title": snippet.get("channelTitle"),
                "thumbnail_url": thumbnail,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })
            if len(videos) >= max_results:
                break
        return videos
