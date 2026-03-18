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


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, settings: Settings) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is not installed.") from exc

        self.client = chromadb.PersistentClient(path=str(settings.chunks_dir / "chroma"))
        self.collection = self.client.get_or_create_collection(settings.chroma_collection_name)

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.reset()
        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "doc_id": chunk.doc_id,
                    "section": chunk.section,
                    "topic": chunk.topic,
                    "evidence_level": chunk.evidence_level,
                    "title": chunk.title,
                    "year": chunk.year,
                }
                for chunk in chunks
            ],
        )

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedContext]:
        response = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        ids = response.get("ids", [[]])[0]
        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]
        results: list[RetrievedContext] = []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            score = 1 / (1 + float(distance))
            results.append(
                RetrievedContext(
                    chunk_id=chunk_id,
                    doc_id=metadata["doc_id"],
                    title=metadata["title"],
                    year=int(metadata["year"]),
                    section=metadata["section"],
                    topic=metadata["topic"],
                    text=text,
                    score=round(score, 4),
                )
            )
        return results

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection.name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(self.collection.name)


def build_vector_store(settings: Settings) -> BaseVectorStore:
    if settings.vector_backend == "chroma":
        try:
            return ChromaVectorStore(settings)
        except RuntimeError:
            pass
    return SimpleJsonVectorStore(index_path=settings.chunks_dir / "simple_vector_index.json")

