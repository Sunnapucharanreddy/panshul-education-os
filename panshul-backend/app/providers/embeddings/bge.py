"""BGE-M3 embedding adapter (multilingual — works for Telugu/Hindi/English)."""
import asyncio

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import EmbeddingProvider


class BGEM3Provider(EmbeddingProvider):
    def __init__(self) -> None:
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from FlagEmbedding import BGEM3FlagModel
            except ImportError as exc:
                raise ProviderError("FlagEmbedding not installed on this worker") from exc
            self._model = BGEM3FlagModel(get_settings().embedding_model, use_fp16=True)
        return self._model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        def _run() -> list[list[float]]:
            out = self._load().encode(texts, return_dense=True)
            return [v.tolist() for v in out["dense_vecs"]]

        return await asyncio.to_thread(_run)
