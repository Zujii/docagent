from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

ROOT = Path(__file__).resolve().parents[2]


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "on", "yes")


@dataclass
class Config:
    provider: str = field(default_factory=lambda: os.getenv("DOCAGENT_PROVIDER", "ollama"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct"))
    ollama_embed_model: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))
    # Same embedder must be used at index time (local) and query time (hosted). Default = fastembed.
    embed_backend: str = field(default_factory=lambda: os.getenv("EMBED_BACKEND", "fastembed"))
    embed_model: str = field(default_factory=lambda: os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5"))
    ollama_host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    api_base_url: str = field(default_factory=lambda: os.getenv("API_BASE_URL", ""))
    api_key: str = field(default_factory=lambda: os.getenv("API_KEY", ""))
    api_model: str = field(default_factory=lambda: os.getenv("API_MODEL", ""))
    guardrails: bool = field(default_factory=lambda: _flag("GUARDRAILS", "on"))
    use_critic: bool = field(default_factory=lambda: _flag("USE_CRITIC", "on"))
    top_k: int = 6
    verifier_min_pass_rate: float = 0.8   # below this -> human approval
    critic_min_confidence: float = 0.5    # below this -> human approval
    data_dir: Path = ROOT / "data"
