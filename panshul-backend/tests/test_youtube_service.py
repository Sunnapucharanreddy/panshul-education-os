import httpx
import pytest

from app.services.youtube_service import YouTubeSearchUnavailable, YouTubeService


@pytest.mark.asyncio
async def test_search_returns_video_metadata_and_uses_requested_topic():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["q"] == "Dijkstra's algorithm explanation"
        assert request.url.params["type"] == "video"
        assert request.url.params["maxResults"] == "3"
        return httpx.Response(200, json={"items": [{
            "id": {"videoId": "video-123"},
            "snippet": {
                "title": "Dijkstra's Algorithm Explained",
                "channelTitle": "Algorithms Class",
                "thumbnails": {"high": {"url": "https://img.youtube.test/thumb.jpg"}},
            },
        }]})

    service = YouTubeService("test-key", transport=httpx.MockTransport(handler))
    results = await service.search("Dijkstra's algorithm")

    assert results == [{
        "video_id": "video-123",
        "title": "Dijkstra's Algorithm Explained",
        "channel_title": "Algorithms Class",
        "thumbnail_url": "https://img.youtube.test/thumb.jpg",
        "url": "https://www.youtube.com/watch?v=video-123",
    }]


@pytest.mark.asyncio
async def test_search_handles_empty_results():
    service = YouTubeService(
        "test-key",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"items": []})),
    )

    assert await service.search("topic") == []


@pytest.mark.asyncio
async def test_search_handles_youtube_api_failure_without_leaking_details():
    service = YouTubeService(
        "test-key",
        transport=httpx.MockTransport(lambda _: httpx.Response(403, json={"error": "quota"})),
    )

    with pytest.raises(YouTubeSearchUnavailable, match="temporarily unavailable"):
        await service.search("topic")


@pytest.mark.asyncio
async def test_search_reports_missing_api_key_without_requesting_youtube():
    def unexpected_request(_: httpx.Request) -> httpx.Response:
        pytest.fail("A request must not be made without an API key")

    service = YouTubeService(transport=httpx.MockTransport(unexpected_request))

    with pytest.raises(YouTubeSearchUnavailable, match="temporarily unavailable"):
        await service.search("topic")
