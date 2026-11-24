"""Cache parsed docs + chunks as JSON so nothing is ever reparsed (and the hosted demo can read them)."""
from __future__ import annotations
import json
from pathlib import Path
from ..schemas import Chunk, Document


def save_doc(doc: Document, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{doc.doc_id}.{doc.parser}.json"
    p.write_text(doc.model_dump_json(indent=1))
    return p


def load_docs(parsed_dir: Path, parser: str = "docling") -> list[Document]:
    return [Document.model_validate_json(p.read_text()) for p in sorted(parsed_dir.glob(f"*.{parser}.json"))]


def save_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(c.model_dump_json() for c in chunks))


def load_chunks(path: Path) -> list[Chunk]:
    return [Chunk.model_validate_json(l) for l in path.read_text().splitlines() if l.strip()]
