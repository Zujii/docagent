"""One class for any OpenAI-compatible endpoint (Gemini, Groq, OpenRouter...)."""
from __future__ import annotations
import json
import time
import httpx
from .base import LLMProvider, LLMResult


class RateLimited(Exception):
    pass


class APIProvider(LLMProvider):
    name = "api"

    def __init__(self, base_url: str, api_key: str, model: str, temperature: float = 0.0,
                 min_interval_s: float = 4.0):
        self.base_url, self.api_key, self.model = base_url.rstrip("/"), api_key, model
        self.temperature, self.min_interval_s = temperature, min_interval_s
        self._last = 0.0

    def generate(self, prompt, system="", json_schema=None) -> LLMResult:
        wait = self.min_interval_s - (time.time() - self._last)   # crude client-side rate limit
        if wait > 0:
            time.sleep(wait)
        if json_schema:  # generic JSON mode has no schema enforcement, so put the schema in the prompt
            system = (system + "\n\nRespond with ONLY a JSON object matching this JSON schema:\n"
                      + json.dumps(json_schema))
        body = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": ([{"role": "system", "content": system}] if system else [])
            + [{"role": "user", "content": prompt}],
        }
        if json_schema:
            body["response_format"] = {"type": "json_object"}
        t0 = time.time()
        r = httpx.post(f"{self.base_url}/chat/completions", json=body, timeout=120,
                       headers={"Authorization": f"Bearer {self.api_key}"})
        self._last = time.time()
        if r.status_code == 429:
            raise RateLimited("free-tier quota hit; fall back to replay mode")
        r.raise_for_status()
        d = r.json()
        u = d.get("usage", {})
        return LLMResult(d["choices"][0]["message"]["content"],
                         u.get("prompt_tokens", 0), u.get("completion_tokens", 0), time.time() - t0)
