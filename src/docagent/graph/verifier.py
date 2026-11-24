"""Deterministic citation verifier: runs BEFORE any LLM critic. Cheap and quantifiable."""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from ..schemas import Chunk, ClaimVerdict, Draft, VerifyResult

_num = re.compile(r"\d[\d,]*\.?\d*")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def quote_in_text(quote: str, text: str, threshold: float = 0.9) -> bool:
    q, t = _norm(quote), _norm(text)
    if not q:
        return False
    if q in t:
        return True
    m = SequenceMatcher(None, q, t, autojunk=False).find_longest_match(0, len(q), 0, len(t))
    return m.size / len(q) >= threshold


def numbers(s: str) -> set[str]:
    return {n.replace(",", "").rstrip(".") for n in _num.findall(s)}


def verify_draft(draft: Draft, chunks_by_id: dict[str, Chunk]) -> VerifyResult:
    verdicts = []
    for i, claim in enumerate(draft.claims):
        reasons = []
        cited = [chunks_by_id[c] for c in claim.chunk_ids if c in chunks_by_id]
        if not claim.chunk_ids:
            reasons.append("no citation")
        elif len(cited) != len(claim.chunk_ids):
            reasons.append("cites chunk id that was not retrieved")
        if cited:
            joined = " ".join(c.text for c in cited)
            if not any(quote_in_text(claim.quote, c.text) for c in cited):
                reasons.append("quote not found in cited chunk")
            missing = numbers(claim.text) - numbers(joined)
            if missing:
                reasons.append(f"numbers not in cited text: {sorted(missing)}")
        verdicts.append(ClaimVerdict(claim_index=i, ok=not reasons, reasons=reasons))
    return VerifyResult(verdicts=verdicts)
