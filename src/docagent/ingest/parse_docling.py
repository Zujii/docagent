"""Docling -> our Pydantic models.

NOTE: Docling's API evolves. Verify attribute names against the installed version
(run it on your 5 ugliest PDFs in Phase 0 and print doc.iterate_items()).
"""
from __future__ import annotations
from pathlib import Path
from ..schemas import Document, Element, Table
from .parse_pypdf import file_hash

LABEL_MAP = {
    "title": "title", "section_header": "heading", "text": "paragraph", "paragraph": "paragraph",
    "list_item": "list_item", "footnote": "footnote", "page_header": "header",
    "page_footer": "footer", "picture": "figure", "caption": "paragraph", "table": "table",
}


def parse_docling(path: Path, do_ocr: bool = True) -> Document:
    from docling.document_converter import DocumentConverter  # heavy import, local only
    path = Path(path)
    doc_id = file_hash(path)
    result = DocumentConverter().convert(str(path))   # TODO: pass pipeline options (do_ocr) if RAM-limited
    dl = result.document
    elements: list[Element] = []
    tables: list[Table] = []
    counters: dict[int, int] = {}
    for item, _level in dl.iterate_items():
        label = getattr(item.label, "value", str(item.label))
        etype = LABEL_MAP.get(label, "other")
        prov = item.prov[0] if getattr(item, "prov", None) else None
        page = prov.page_no if prov else 0
        idx = counters.get(page, 0)
        counters[page] = idx + 1
        eid = f"{doc_id}:{page}:{idx}"
        bbox = None
        if prov and getattr(prov, "bbox", None):
            b = prov.bbox
            bbox = (b.l, b.t, b.r, b.b)
        if etype == "table":
            rows = [[str(c) for c in row] for row in item.export_to_dataframe().values.tolist()]
            tables.append(Table(id=eid, page=page, rows=rows))
            elements.append(Element(id=eid, type="table", text=tables[-1].to_text(), page=page, bbox=bbox))
        else:
            text = getattr(item, "text", "") or ""
            if text.strip():
                elements.append(Element(id=eid, type=etype, text=text, page=page, bbox=bbox))
    n_pages = len(dl.pages) if hasattr(dl, "pages") else max((e.page for e in elements), default=0)
    return Document(doc_id=doc_id, source_path=str(path), parser="docling",
                    n_pages=n_pages, elements=elements, tables=tables)
