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

    def generate_json(self, prompt: str) -> OllamaResponse:
        errors: list[str] = []
        for model_name in (self.settings.ollama_model, self.settings.ollama_fallback_model):
            try:
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": self.settings.generation_temperature,
                    },
                }
                response = requests.post(
                    f"{self.settings.ollama_base_url}/api/generate",
                    json=payload,
                    timeout=self.settings.request_timeout_sec,
                )
                response.raise_for_status()
                body = response.json()
                return OllamaResponse(
                    model_used=body.get("model", model_name),
                    response_text=body.get("response", "").strip(),
                )
            except requests.RequestException as exc:
                errors.append(f"{model_name}: {exc}")
        raise OllamaUnavailableError("; ".join(errors) or "Ollama request failed.")

