"""Scan parsed content BEFORE it enters agent context. Rules now; add your classifier next
(features -> XGBoost) and combine scores."""
from __future__ import annotations
import re
from ..schemas import Chunk, RiskEvent

RULES: list[tuple[str, float, re.Pattern]] = [
    ("override_instructions", 0.9, re.compile(r"ignore (all |any )?(previous|prior|above) (instructions|prompts)", re.I)),
    ("role_hijack", 0.7, re.compile(r"\b(you are now|act as|new system prompt|system:)\b", re.I)),
    ("tool_directive", 0.7, re.compile(r"\b(call|invoke|use) the \w+ (tool|function)\b", re.I)),
    ("exfil", 0.8, re.compile(r"(send|post|upload|email) .{0,60}(to|at) (https?://|\S+@\S+)", re.I)),
    ("hidden_directive", 0.6, re.compile(r"(do not|don't) (tell|mention|reveal) (the )?user", re.I)),
]
APPROVE_AT, BLOCK_AT = 0.5, 0.8


def scan_chunk(chunk: Chunk) -> RiskEvent:
    hits = [(name, w) for name, w, rx in RULES if rx.search(chunk.text)]
    score = max((w for _, w in hits), default=0.0)
    # TODO: score = combine(score, classifier.predict_proba(features(chunk)))
    decision = "block" if score >= BLOCK_AT else "require_approval" if score >= APPROVE_AT else "allow"
    return RiskEvent(source="ingest", target=chunk.chunk_id, score=score,
                     decision=decision, reasons=[n for n, _ in hits])
