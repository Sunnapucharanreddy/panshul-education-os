"""Provider registry — the single place where env config maps to implementations.
Swapping any model = change one env var. Adding a model = register one class."""
from functools import lru_cache

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import EmbeddingProvider, LLMProvider, STTProvider, TTSProvider, VectorStore

_LLM = {
    "qwen": "app.providers.llm.qwen.QwenProvider",
    "groq": "app.providers.llm.qwen.QwenProvider",   # same OpenAI-compatible adapter
    "openrouter": "app.providers.llm.qwen.QwenProvider",
}
_STT = {
    "faster_whisper": "app.providers.stt.faster_whisper.FasterWhisperProvider",
    "sarvam": "app.providers.stt.sarvam.SarvamSTTProvider",
}
_TTS = {
    "xtts_v2": "app.providers.tts.xtts.XTTSProvider",
    "sarvam": "app.providers.tts.sarvam.SarvamTTSProvider",
}
_EMB = {"bge_m3": "app.providers.embeddings.bge.BGEM3Provider"}


def _instantiate(path: str):
    module_path, cls_name = path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[cls_name])
    return getattr(module, cls_name)()


def _resolve(mapping: dict[str, str], key: str, kind: str):
    if key not in mapping:
        raise ProviderError(f"Unknown {kind} provider: {key}")
    return _instantiate(mapping[key])


@lru_cache
def get_llm() -> LLMProvider:
    return _resolve(_LLM, get_settings().llm_provider, "LLM")


@lru_cache
def get_stt() -> STTProvider:
    return _resolve(_STT, get_settings().stt_provider, "STT")


@lru_cache
def get_tts() -> TTSProvider:
    return _resolve(_TTS, get_settings().tts_provider, "TTS")


@lru_cache
def get_embedder() -> EmbeddingProvider:
    return _resolve(_EMB, get_settings().embedding_provider, "embedding")


@lru_cache
def get_vector_store() -> VectorStore:
    from app.providers.vector.qdrant_store import QdrantStore
    return QdrantStore()
