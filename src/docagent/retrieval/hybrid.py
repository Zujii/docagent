"""BM25 + dense (numpy cosine) with reciprocal rank fusion. Embeddings can be precomputed (.npy)."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional
import numpy as np
from rank_bm25 import BM25Okapi
from ..schemas import Chunk
from .embed import Embedder

_tok = lambda s: re.findall(r"\w+", s.lower())


class HybridIndex:
    def __init__(self, chunks: list[Chunk], embeddings: Optional[np.ndarray] = None,
                 embedder: Optional[Embedder] = None):
        self.chunks = chunks
        self.bm25 = BM25Okapi([_tok(c.text) for c in chunks]) if chunks else None
        self.embeddings, self.embedder = embeddings, embedder
        if embeddings is not None:
            n = np.linalg.norm(embeddings, axis=1, keepdims=True)
            self.embeddings = embeddings / np.clip(n, 1e-9, None)

    def build_embeddings(self) -> np.ndarray:
        assert self.embedder is not None
        self.embeddings = self.embedder([c.text for c in self.chunks])
        n = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / np.clip(n, 1e-9, None)
        return self.embeddings

    def save_embeddings(self, path: Path) -> None:
        np.save(path, self.embeddings)

    def search(self, query: str, k: int = 6, mode: str = "hybrid", rrf_k: int = 60) -> list[tuple[Chunk, float]]:
        ranks: dict[int, float] = {}
        if mode in ("hybrid", "bm25") and self.bm25:
            scores = self.bm25.get_scores(_tok(query))
            for r, i in enumerate(np.argsort(-scores)[: k * 4]):
                ranks[int(i)] = ranks.get(int(i), 0) + 1 / (rrf_k + r + 1)
        if mode in ("hybrid", "dense") and self.embeddings is not None and self.embedder:
            q = self.embedder([query])[0]
            q = q / max(np.linalg.norm(q), 1e-9)
            sims = self.embeddings @ q
            for r, i in enumerate(np.argsort(-sims)[: k * 4]):
                ranks[int(i)] = ranks.get(int(i), 0) + 1 / (rrf_k + r + 1)
        top = sorted(ranks.items(), key=lambda kv: -kv[1])[:k]
        return [(self.chunks[i], s) for i, s in top]
