from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.config import Settings
from app.schemas import Chunk, DocumentMetadata
from rag.chunking import clean_text, paragraph_chunks
from rag.embeddings import BaseEmbedder
from rag.vector_store import BaseVectorStore


@dataclass(slots=True)
class IngestionSummary:
    documents_ingested: int
    chunks_created: int
    index_backend: str


class CorpusIngestor:
    def __init__(self, settings: Settings, embedder: BaseEmbedder, vector_store: BaseVectorStore) -> None:
        self.settings = settings
        self.embedder = embedder
        self.vector_store = vector_store

    def load_metadata(self) -> list[DocumentMetadata]:
        if not self.settings.seed_corpus_metadata_path.exists():
            return []
        raw = json.loads(self.settings.seed_corpus_metadata_path.read_text(encoding="utf-8"))
        return [DocumentMetadata.model_validate(item) for item in raw]

    def run(self) -> IngestionSummary:
        documents = self.load_metadata()
        all_chunks: list[Chunk] = []
        for document in documents:
            source_path = Path(document.filepath)
            if not source_path.is_absolute():
                source_path = self.settings.project_root / source_path
            text = self.extract_text(source_path)
            cleaned = clean_text(text)
            processed_path = self.settings.processed_dir / f"{document.doc_id}.txt"
            processed_path.write_text(cleaned, encoding="utf-8")

            chunks = paragraph_chunks(
                document=document,
                text=cleaned,
                max_chunk_chars=self.settings.max_chunk_chars,
                overlap_chars=self.settings.chunk_overlap_chars,
            )
            chunk_path = self.settings.chunks_dir / f"{document.doc_id}.json"
            chunk_path.write_text(
                json.dumps([chunk.model_dump(mode="json") for chunk in chunks], indent=2),
                encoding="utf-8",
            )
            all_chunks.extend(chunks)

        embeddings = self.embedder.embed_texts([chunk.text for chunk in all_chunks]) if all_chunks else []
        self.vector_store.add_chunks(all_chunks, embeddings)
        return IngestionSummary(
            documents_ingested=len(documents),
            chunks_created=len(all_chunks),
            index_backend=self.vector_store.__class__.__name__,
        )

    def extract_text(self, filepath: Path) -> str:
        if not filepath.exists():
            raise FileNotFoundError(f"Corpus document not found: {filepath}")
        if filepath.suffix.lower() in {".txt", ".md"}:
            return filepath.read_text(encoding="utf-8")
        if filepath.suffix.lower() == ".pdf":
            try:
                import fitz
            except ImportError as exc:
                raise RuntimeError("PyMuPDF is required to ingest PDFs.") from exc
            document = fitz.open(filepath)
            pages = [page.get_text("text") for page in document]
            document.close()
            return "\n".join(pages)
        raise ValueError(f"Unsupported corpus file type: {filepath.suffix}")
