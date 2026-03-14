from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass


TOKEN_RE = re.compile(r"[a-z0-9_]+")


class BaseEmbedder:
    dimension: int

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


@dataclass(slots=True)
class HashingEmbedder(BaseEmbedder):
    dimension: int = 256

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in TOKEN_RE.findall(text.lower()):
            hashed = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            index = hashed % self.dimension
            sign = -1.0 if (hashed >> 8) % 2 else 1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    return sum(a * b for a, b in zip(vec_a, vec_b, strict=False))

