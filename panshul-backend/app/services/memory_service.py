"""Student long-term memory: store salient facts as vectors in Qdrant,
retrieve top-k relevant memories for each conversation turn (RAG)."""
from app.core.config import get_settings
from app.providers.base import EmbeddingProvider, VectorStore


class MemoryService:
    def __init__(self, embedder: EmbeddingProvider, store: VectorStore) -> None:
        self.embedder = embedder
        self.store = store
        self.collection = get_settings().qdrant_collection_memory

    async def remember(self, user_id: str, facts: list[str]) -> None:
        if not facts:
            return
        vectors = await self.embedder.embed(facts)
        await self.store.upsert(
            self.collection, facts, vectors,
            metadatas=[{"user_id": user_id} for _ in facts],
        )

    async def recall(self, user_id: str, query: str, limit: int = 5) -> str:
        vector = (await self.embedder.embed([query]))[0]
        hits = await self.store.search(self.collection, vector, limit=limit,
                                       filters={"user_id": user_id})
        return "\n".join(f"- {h.text}" for h in hits) if hits else "None yet"
