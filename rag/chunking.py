from __future__ import annotations

import re
from typing import Iterable

from app.schemas import Chunk, DocumentMetadata


def clean_text(raw_text: str) -> str:
    text = raw_text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_sections(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines
        if current_lines:
            sections.append((current_title, current_lines.copy()))
            current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append("")
            continue
        if stripped.startswith("#") or stripped.endswith(":"):
            flush()
            current_title = stripped.lstrip("#").strip(": ").strip() or current_title
            continue
        current_lines.append(stripped)
    flush()
    return [(title, "\n".join(content).strip()) for title, content in sections if "\n".join(content).strip()]


def paragraph_chunks(
    document: DocumentMetadata,
    text: str,
    max_chunk_chars: int,
    overlap_chars: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_index = 0
    evidence_level = source_to_evidence_level(document.source_type)

    for section, section_text in split_into_sections(text):
        paragraphs = [paragraph.strip() for paragraph in section_text.split("\n\n") if paragraph.strip()]
        buffer = ""
        for paragraph in paragraphs:
            candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
            if len(candidate) <= max_chunk_chars:
                buffer = candidate
                continue
            if buffer:
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.doc_id}_chunk_{chunk_index:03d}",
                        doc_id=document.doc_id,
                        section=section,
                        page=None,
                        text=buffer,
                        topic=document.topic,
                        evidence_level=evidence_level,
                        title=document.title,
                        year=document.year,
                    )
                )
                chunk_index += 1
            if len(paragraph) <= max_chunk_chars:
                buffer = paragraph[-overlap_chars:] + "\n\n" + paragraph if buffer else paragraph
                buffer = buffer[-max_chunk_chars:]
                continue

            for segment in _split_long_paragraph(paragraph, max_chunk_chars, overlap_chars):
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.doc_id}_chunk_{chunk_index:03d}",
                        doc_id=document.doc_id,
                        section=section,
                        page=None,
                        text=segment,
                        topic=document.topic,
                        evidence_level=evidence_level,
                        title=document.title,
                        year=document.year,
                    )
                )
                chunk_index += 1
            buffer = ""

        if buffer:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}_chunk_{chunk_index:03d}",
                    doc_id=document.doc_id,
                    section=section,
                    page=None,
                    text=buffer,
                    topic=document.topic,
                    evidence_level=evidence_level,
                    title=document.title,
                    year=document.year,
                )
            )
            chunk_index += 1
    return chunks


def _split_long_paragraph(paragraph: str, max_chunk_chars: int, overlap_chars: int) -> Iterable[str]:
    words = paragraph.split()
    buffer: list[str] = []
    for word in words:
        candidate = " ".join(buffer + [word]).strip()
        if len(candidate) <= max_chunk_chars:
            buffer.append(word)
            continue
        chunk = " ".join(buffer).strip()
        if chunk:
            yield chunk
        overlap_seed = chunk[-overlap_chars:] if chunk else ""
        buffer = [overlap_seed, word] if overlap_seed else [word]
    tail = " ".join(buffer).strip()
    if tail:
        yield tail


def source_to_evidence_level(source_type: str) -> str:
    normalized = source_type.lower()
    if "guideline" in normalized or "consensus" in normalized:
        return "high"
    if "review" in normalized or "meta" in normalized:
        return "moderate_high"
    return "moderate"

