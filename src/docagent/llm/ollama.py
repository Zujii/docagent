from __future__ import annotations
import time
import httpx
from .base import LLMProvider, LLMResult


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, model: str, host: str = "http://localhost:11434", temperature: float = 0.0):
        self.model, self.host, self.temperature = model, host.rstrip("/"), temperature

    def generate(self, prompt, system="", json_schema=None) -> LLMResult:
        body = {
            "model": self.model,
            "messages": ([{"role": "system", "content": system}] if system else [])
            + [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if json_schema:
            body["format"] = json_schema   # Ollama structured outputs
        t0 = time.time()
        r = httpx.post(f"{self.host}/api/chat", json=body, timeout=300)
        r.raise_for_status()
        d = r.json()
        return LLMResult(
            text=d["message"]["content"],
            prompt_tokens=d.get("prompt_eval_count", 0),
            completion_tokens=d.get("eval_count", 0),
            latency_s=time.time() - t0,
        )
