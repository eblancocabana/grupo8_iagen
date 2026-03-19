from __future__ import annotations

from dataclasses import dataclass

import requests

from app.config import Settings


class OllamaUnavailableError(RuntimeError):
    """Raised when Ollama cannot satisfy a generation request."""


@dataclass(slots=True)
class OllamaResponse:
    model_used: str
    response_text: str


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def available(self) -> bool:
        if not self.settings.use_ollama:
            return False
        try:
            response = requests.get(
                f"{self.settings.ollama_base_url}/api/tags",
                timeout=min(self.settings.request_timeout_sec, 10),
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

