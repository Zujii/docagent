"""Index metadata: guards against building with one embedder and querying with another."""
from __future__ import annotations
import json
from pathlib import Path


class EmbedderMismatch(RuntimeError):
    pass


def write_meta(path: Path, embedder_name: str, n_chunks: int, dim: int) -> None:
    Path(path).write_text(json.dumps({"embedder": embedder_name, "n_chunks": n_chunks, "dim": dim}, indent=2))


def check_meta(path: Path, embedder_name: str) -> dict:
    meta = json.loads(Path(path).read_text())
    if meta["embedder"] != embedder_name:
        raise EmbedderMismatch(
            f"Index was built with '{meta['embedder']}' but queries use '{embedder_name}'. "
            "Rebuild the index (make index) or fix EMBED_BACKEND/EMBED_MODEL.")
    return meta
