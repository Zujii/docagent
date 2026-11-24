from __future__ import annotations
from typing import Callable
import numpy as np
import httpx

Embedder = Callable[[list[str]], np.ndarray]


def ollama_embedder(model: str, host: str = "http://localhost:11434") -> Embedder:
    def embed(texts: list[str]) -> np.ndarray:
        out = []
        for t in texts:
            r = httpx.post(f"{host}/api/embeddings", json={"model": model, "prompt": t}, timeout=120)
            r.raise_for_status()
            out.append(r.json()["embedding"])
        return np.array(out, dtype="float32")
    return embed


def fastembed_embedder(model: str = "BAAI/bge-small-en-v1.5") -> Embedder:
    """Light ONNX embedder for the hosted app (no torch)."""
    from fastembed import TextEmbedding
    m = TextEmbedding(model_name=model)
    return lambda texts: np.array(list(m.embed(texts)), dtype="float32")


def get_embedder(cfg) -> tuple[Embedder, str]:
    """Returns (embedder, name). The name is stored in index/meta.json and checked at load time."""
    if cfg.embed_backend == "ollama":
        return ollama_embedder(cfg.ollama_embed_model, cfg.ollama_host), f"ollama:{cfg.ollama_embed_model}"
    return fastembed_embedder(cfg.embed_model), f"fastembed:{cfg.embed_model}"
