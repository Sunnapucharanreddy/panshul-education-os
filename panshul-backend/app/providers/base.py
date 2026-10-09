"""Abstract provider interfaces — the seam that makes every AI model swappable.

Rules:
- Agents and services depend ONLY on these interfaces, never on a concrete model.
- Adding a new model = one adapter file + one registry entry + an .env change.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass
class ChatMessage:
    role: str            # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.7,
                   max_tokens: int = 1024, json_mode: bool = False) -> LLMResponse: ...

    @abstractmethod
    def stream(self, messages: list[ChatMessage], *, temperature: float = 0.7,
               max_tokens: int = 1024) -> AsyncIterator[str]: ...


@dataclass
class Transcript:
    text: str
    language: str
    duration_seconds: float


class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, *, language: str | None = None) -> Transcript: ...


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, *, language: str = "en",
                         voice: str | None = None) -> bytes:
        """Returns audio bytes (wav)."""


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class MemoryHit:
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, collection: str, texts: list[str],
                     vectors: list[list[float]], metadatas: list[dict]) -> None: ...

    @abstractmethod
    async def search(self, collection: str, vector: list[float], *,
                     limit: int = 5, filters: dict | None = None) -> list[MemoryHit]: ...
