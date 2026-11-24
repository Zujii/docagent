from __future__ import annotations
from ..config import Config
from .base import LLMProvider


def get_provider(cfg: Config) -> LLMProvider:
    if cfg.provider == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider(cfg.ollama_model, cfg.ollama_host)
    if cfg.provider == "api":
        from .api import APIProvider
        return APIProvider(cfg.api_base_url, cfg.api_key, cfg.api_model)
    if cfg.provider == "replay":
        from .replay import ReplayProvider
        return ReplayProvider(cfg.data_dir / "traces" / "replay_cache.jsonl")
    raise ValueError(f"unknown provider {cfg.provider}")
