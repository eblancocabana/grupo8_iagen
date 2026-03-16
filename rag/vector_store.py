from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import Settings
from app.schemas import Chunk, RetrievedContext
from rag.embeddings import BaseEmbedder, cosine_similarity


class BaseVectorStore:
    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        raise NotImplementedError

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedContext]:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError


@dataclass(slots=True)
class SimpleJsonVectorStore(BaseVectorStore):
    index_path: Path

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        payload = [
            {
                "chunk": chunk.model_dump(mode="json"),
                "embedding": embedding,
            }
            for chunk, embedding in zip(chunks, embeddings, strict=False)
        ]
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedContext]:
        if not self.index_path.exists():
            return []
        payload = json.loads(self.index_path.read_text(encoding="utf-8"))
        scored = sorted(
            (
                (
                    cosine_similarity(query_embedding, item["embedding"]),
                    item["chunk"],
                )
                for item in payload
            ),
            key=lambda pair: pair[0],
            reverse=True,
        )
        results: list[RetrievedContext] = []
        for score, chunk in scored[:top_k]:
            results.append(
                RetrievedContext(
                    chunk_id=chunk["chunk_id"],
                    doc_id=chunk["doc_id"],
                    title=chunk["title"],
                    year=chunk["year"],
                    section=chunk["section"],
                    topic=chunk["topic"],
                    text=chunk["text"],
                    score=round(float(score), 4),
                )
            )
        return results

    def reset(self) -> None:
        if self.index_path.exists():
            self.index_path.unlink()

