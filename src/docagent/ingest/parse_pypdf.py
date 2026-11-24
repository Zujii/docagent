"""Naive baseline parser (ablation #1). Emits the same models as the Docling parser."""
from __future__ import annotations
import hashlib
from pathlib import Path
from ..schemas import Document, Element


def file_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def parse_pypdf(path: Path) -> Document:
    from pypdf import PdfReader
    path = Path(path)
    doc_id = file_hash(path)
    reader = PdfReader(str(path))
    elements: list[Element] = []
    for pno, page in enumerate(reader.pages, start=1):
        paras = [p.strip() for p in (page.extract_text() or "").split("\n\n") if p.strip()]
        for i, text in enumerate(paras):
            elements.append(Element(id=f"{doc_id}:{pno}:{i}", type="paragraph", text=text, page=pno))
    return Document(doc_id=doc_id, source_path=str(path), parser="pypdf",
                    n_pages=len(reader.pages), elements=elements)
