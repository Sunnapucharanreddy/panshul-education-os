"""Deterministic detection and topic extraction for explicit video requests."""

import re
from collections.abc import Sequence

VIDEO_REQUEST = re.compile(
    r"\b(?:"
    r"video\s+(?:explanation|explaining|tutorial|about|on)"
    r"|youtube\s+video"
    r"|(?:show|give|find|recommend|suggest|send)\s+me\s+(?:a\s+)?(?:youtube\s+)?video"
    r"|(?:learn|teach\s+me)\s+(?:this\s+topic\s+)?through\s+(?:a\s+)?(?:youtube\s+)?video"
    r")\b",
    re.IGNORECASE,
)

_PREFIXES = re.compile(
    r"^(?:(?:please\s+)?(?:can|could|would)\s+you\s+|"
    r"(?:please\s+)?(?:i\s+want|i\s+need|i'd\s+like)\s+|"
    r"(?:please\s+)?(?:show|give|find|recommend|suggest|send)\s+me\s+)+",
    re.IGNORECASE,
)
_VIDEO_PHRASE = re.compile(
    r"^(?:a\s+|the\s+)?(?:youtube\s+)?video\s+"
    r"(?:(?:explanation|tutorial)\s+(?:of|about|on|for)|"
    r"(?:explaining|about|on|for))\s+",
    re.IGNORECASE,
)
_LEADING_TOPIC_VERB = re.compile(r"^(?:explain|teach\s+me|show\s+me)\s+", re.IGNORECASE)
_REFERENTIAL_TOPIC = re.compile(r"^(?:this topic|that topic|it|this|that)$", re.IGNORECASE)


def _clean_topic(text: str) -> str:
    text = text.strip().rstrip("?.!, ")
    text = _PREFIXES.sub("", text).strip()
    text = _VIDEO_PHRASE.sub("", text).strip()
    text = re.sub(r"\s+(?:through|using)\s+(?:a\s+)?(?:youtube\s+)?video\s*$", "", text, flags=re.I)
    text = _LEADING_TOPIC_VERB.sub("", text).strip()
    return text.strip(" .?!,\t\n")


def requested_video_topic(message: str, history: Sequence[dict] = ()) -> str | None:
    """Return a topic only for explicit video requests; None means normal chat."""
    if not VIDEO_REQUEST.search(message):
        return None

    topic = _clean_topic(message)
    if _REFERENTIAL_TOPIC.fullmatch(topic):
        for turn in reversed(history):
            if turn.get("role") != "user":
                continue
            candidate = _clean_topic(str(turn.get("content", "")))
            if candidate and not _REFERENTIAL_TOPIC.fullmatch(candidate):
                return candidate
        return ""
    return topic
