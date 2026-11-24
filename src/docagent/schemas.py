"""Core Pydantic models. Provenance (doc_id/page/element ids) flows through everything."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

ElementType = Literal[
    "title", "heading", "paragraph", "list_item", "table",
    "footnote", "header", "footer", "figure", "other",
]


class Element(BaseModel):
    id: str                      # stable: f"{doc_id}:{page}:{index}"
    type: ElementType
    text: str
    page: int
    bbox: Optional[tuple[float, float, float, float]] = None


class Table(BaseModel):
    id: str
    page: int
    caption: Optional[str] = None
    rows: list[list[str]]

    def to_text(self) -> str:
        lines = [" | ".join(r) for r in self.rows]
        return (f"{self.caption}\n" if self.caption else "") + "\n".join(lines)


class Document(BaseModel):
    doc_id: str
    source_path: str
    parser: str                  # "docling" | "pypdf"
    n_pages: int
    elements: list[Element]
    tables: list[Table] = Field(default_factory=list)


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    page: int
    element_ids: list[str]
    section_path: list[str] = Field(default_factory=list)
    is_table: bool = False
    quarantined: bool = False


class Claim(BaseModel):
    text: str
    chunk_ids: list[str]
    quote: str = ""              # verbatim span from a cited chunk


class Draft(BaseModel):
    claims: list[Claim] = Field(default_factory=list)
    abstained: bool = False      # writer says evidence is insufficient


class ClaimVerdict(BaseModel):
    claim_index: int
    ok: bool
    reasons: list[str] = Field(default_factory=list)


class VerifyResult(BaseModel):
    verdicts: list[ClaimVerdict] = Field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if not self.verdicts:
            return 1.0
        return sum(v.ok for v in self.verdicts) / len(self.verdicts)


class RiskEvent(BaseModel):
    source: Literal["ingest", "tool_call", "output"]
    target: str                  # chunk_id or tool name
    score: float
    decision: Literal["allow", "require_approval", "block"]
    reasons: list[str] = Field(default_factory=list)


class Metrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_s: float = 0.0
    llm_calls: int = 0
    cost_usd: float = 0.0
