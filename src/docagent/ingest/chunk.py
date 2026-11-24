"""Structure-aware chunking: headings set section_path, tables stay whole, headers/footers dropped."""
from __future__ import annotations
from ..schemas import Chunk, Document

SKIP = {"header", "footer"}


def chunk_document(doc: Document, max_chars: int = 1200) -> list[Chunk]:
    chunks: list[Chunk] = []
    section: list[str] = []
    buf_text: list[str] = []
    buf_ids: list[str] = []
    buf_page = 0

    def flush():
        nonlocal buf_text, buf_ids
        if buf_text:
            chunks.append(Chunk(
                chunk_id=f"{doc.doc_id}:c{len(chunks)}", doc_id=doc.doc_id,
                text="\n".join(buf_text), page=buf_page,
                element_ids=list(buf_ids), section_path=list(section)))
        buf_text, buf_ids = [], []

    for el in doc.elements:
        if el.type in SKIP:
            continue
        if el.type in ("title", "heading"):
            flush()
            section = (section + [el.text]) if el.type == "heading" and section else [el.text]
            section = section[-3:]
            continue
        if el.type == "table":
            flush()
            chunks.append(Chunk(
                chunk_id=f"{doc.doc_id}:c{len(chunks)}", doc_id=doc.doc_id, text=el.text,
                page=el.page, element_ids=[el.id], section_path=list(section), is_table=True))
            continue
        if buf_text and sum(map(len, buf_text)) + len(el.text) > max_chars:
            flush()
        if not buf_text:
            buf_page = el.page
        buf_text.append(el.text)
        buf_ids.append(el.id)
    flush()
    return chunks
