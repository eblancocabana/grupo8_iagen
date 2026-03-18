from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.schemas import RetrievedContext, UserProfile
from rag.embeddings import BaseEmbedder
from rag.vector_store import BaseVectorStore


@dataclass(slots=True)
class RetrievalTrace:
    query: str
    top_k: int
    results_count: int


class RAGRetriever:
    def __init__(self, settings: Settings, embedder: BaseEmbedder, vector_store: BaseVectorStore) -> None:
        self.settings = settings
        self.embedder = embedder
        self.vector_store = vector_store

    def build_query(self, profile: UserProfile) -> str:
        restriction_text = (
            ", ".join(item.value.replace("_", " ") for item in profile.movement_restrictions)
            if profile.movement_restrictions
            else "no special movement restrictions"
        )
        return (
            f"Evidence-based recommendations for {profile.experience_level.value} "
            f"{profile.goal.value.replace('_', ' ')} training, {profile.days_per_week} days per week, "
            f"{profile.session_duration_min} minute sessions, {profile.equipment.value} equipment, "
            f"with {restriction_text}."
        )

    def retrieve(self, profile: UserProfile, top_k: int | None = None) -> tuple[str, list[RetrievedContext], RetrievalTrace]:
        effective_top_k = top_k or self.settings.retrieval_top_k
        query = self.build_query(profile)
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_store.search(query_embedding, effective_top_k)
        trace = RetrievalTrace(query=query, top_k=effective_top_k, results_count=len(results))
        return query, results, trace

