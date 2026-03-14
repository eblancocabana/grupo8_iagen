from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

class BaseEmbedder:
    dimension: int

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    return sum(a * b for a, b in zip(vec_a, vec_b, strict=False))

