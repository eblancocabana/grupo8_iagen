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
