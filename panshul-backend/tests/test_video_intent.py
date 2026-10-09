from app.services.video_intent import requested_video_topic


def test_video_requests_extract_the_requested_topic():
    assert requested_video_topic(
        "Can you give me a video explaining TCP congestion control?"
    ) == "TCP congestion control"
    assert requested_video_topic("Show me a video about deadlocks.") == "deadlocks"
    assert requested_video_topic("I want a video explanation of normalization.") == "normalization"


def test_regular_academic_questions_remain_teacher_requests():
    assert requested_video_topic("Explain Dijkstra's algorithm.") is None


def test_referential_video_request_uses_recent_user_topic():
    history = [{"role": "user", "content": "Explain Dijkstra's algorithm."}]
    assert requested_video_topic("Teach me this topic through a YouTube video.", history) == "Dijkstra's algorithm"


def test_video_request_without_a_known_topic_asks_for_one():
    assert requested_video_topic("Can you teach me this topic through a YouTube video?") == ""
