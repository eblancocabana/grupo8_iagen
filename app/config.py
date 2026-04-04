from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    raw_docs_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)
    chunks_dir: Path = field(init=False)
    profiles_dir: Path = field(init=False)
    outputs_dir: Path = field(init=False)
    plans_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    tables_dir: Path = field(init=False)

    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
    ollama_fallback_model: str = field(default_factory=lambda: os.getenv("OLLAMA_FALLBACK_MODEL", "llama3.2:3b"))
    generation_temperature: float = field(default_factory=lambda: float(os.getenv("GENERATION_TEMPERATURE", "0.2")))
    request_timeout_sec: int = field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT_SEC", "180")))
    use_ollama: bool = field(default_factory=lambda: _env_bool("USE_OLLAMA", False))
    repair_with_llm: bool = field(default_factory=lambda: _env_bool("REPAIR_WITH_LLM", False))
    max_repair_attempts: int = field(default_factory=lambda: int(os.getenv("MAX_REPAIR_ATTEMPTS", "1")))

    vector_backend: str = field(default_factory=lambda: os.getenv("VECTOR_BACKEND", "simple"))
    embedding_backend: str = field(default_factory=lambda: os.getenv("EMBEDDING_BACKEND", "hash"))
    chroma_collection_name: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION_NAME", "training_evidence"))
    retrieval_top_k: int = field(default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "5")))
    max_chunk_chars: int = field(default_factory=lambda: int(os.getenv("MAX_CHUNK_CHARS", "900")))
    chunk_overlap_chars: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP_CHARS", "120")))

    seed_corpus_metadata_path: Path = field(init=False)
    seed_profiles_path: Path = field(init=False)
    experiment_results_path: Path = field(init=False)

    def __post_init__(self) -> None:
        data_dir = self.project_root / "data"
        self.raw_docs_dir = data_dir / "raw_pdfs"
        self.processed_dir = data_dir / "processed"
        self.chunks_dir = data_dir / "chunks"
        self.profiles_dir = data_dir / "profiles"
        self.outputs_dir = self.project_root / "outputs"
        self.plans_dir = self.outputs_dir / "plans"
        self.logs_dir = self.outputs_dir / "logs"
        self.tables_dir = self.outputs_dir / "tables"
        self.seed_corpus_metadata_path = self.raw_docs_dir / "metadata.json"
        self.seed_profiles_path = self.profiles_dir / "test_profiles.json"
        self.experiment_results_path = self.tables_dir / "experiment_results.csv"

    def ensure_directories(self) -> None:
        for path in (
            self.raw_docs_dir,
            self.processed_dir,
            self.chunks_dir,
            self.profiles_dir,
            self.plans_dir,
            self.logs_dir,
            self.tables_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()

