"""Qdrant vector store adapter."""
import uuid

from qdrant_client import AsyncQdrantClient, models

from app.core.config import get_settings
from app.providers.base import MemoryHit, VectorStore


class QdrantStore(VectorStore):
    def __init__(self) -> None:
        self._client = AsyncQdrantClient(url=get_settings().qdrant_url)

    async def ensure_collection(self, collection: str, dim: int = 1024) -> None:
        if not await self._client.collection_exists(collection):
            await self._client.create_collection(
                collection_name=collection,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )

    async def upsert(self, collection: str, texts: list[str],
                     vectors: list[list[float]], metadatas: list[dict]) -> None:
        await self.ensure_collection(collection, dim=len(vectors[0]))
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload={"text": text, **meta},
            )
            for text, vec, meta in zip(texts, vectors, metadatas)
        ]
        await self._client.upsert(collection_name=collection, points=points)

    async def search(self, collection: str, vector: list[float], *,
                     limit: int = 5, filters: dict | None = None) -> list[MemoryHit]:
        qfilter = None
        if filters:
            qfilter = models.Filter(must=[
                models.FieldCondition(key=k, match=models.MatchValue(value=v))
                for k, v in filters.items()
            ])
        res = await self._client.search(
            collection_name=collection, query_vector=vector,
            limit=limit, query_filter=qfilter,
        )
        return [
            MemoryHit(text=p.payload.get("text", ""), score=p.score,
                      metadata={k: v for k, v in (p.payload or {}).items() if k != "text"})
            for p in res
        ]
