"""Replay + recording. Replay keeps the public demo alive when API quotas run out."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .base import LLMProvider, LLMResult


def prompt_key(prompt: str, system: str) -> str:
    return hashlib.sha256((system + "\x00" + prompt).encode()).hexdigest()


class ReplayProvider(LLMProvider):
    name = "replay"

    def __init__(self, cache_path: Path):
        self.cache: dict[str, dict] = {}
        if Path(cache_path).exists():
            for line in Path(cache_path).read_text().splitlines():
                rec = json.loads(line)
                self.cache[rec["key"]] = rec

    def generate(self, prompt, system="", json_schema=None) -> LLMResult:
        rec = self.cache.get(prompt_key(prompt, system))
        if rec is None:
            raise KeyError("No cached response for this prompt (replay mode only serves pre-run examples)")
        return LLMResult(rec["text"], rec.get("prompt_tokens", 0), rec.get("completion_tokens", 0), 0.0)


class RecordingProvider(LLMProvider):
    """Wrap a real provider and append every call to a JSONL cache."""

    def __init__(self, inner: LLMProvider, cache_path: Path):
        self.inner, self.path, self.name = inner, Path(cache_path), f"rec({inner.name})"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, prompt, system="", json_schema=None) -> LLMResult:
        res = self.inner.generate(prompt, system, json_schema)
        with self.path.open("a") as f:
            f.write(json.dumps({"key": prompt_key(prompt, system), "text": res.text,
                                "prompt_tokens": res.prompt_tokens,
                                "completion_tokens": res.completion_tokens}) + "\n")
        return res
