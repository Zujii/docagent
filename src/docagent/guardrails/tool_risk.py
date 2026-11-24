"""Tool-call risk scoring (port your Blast-Radius logic here)."""
from __future__ import annotations
from ..schemas import RiskEvent

TOOL_BASE_RISK = {"retrieve": 0.05, "web_search": 0.35, "read_file": 0.3, "write_file": 0.8, "http_post": 0.9}


def score_tool_call(tool: str, args: dict, context_tainted: bool) -> RiskEvent:
    score = TOOL_BASE_RISK.get(tool, 0.5)
    reasons = []
    if context_tainted:
        score += 0.3
        reasons.append("call made while untrusted/quarantined content in context")
    if any(isinstance(v, str) and ("http://" in v or "https://" in v) for v in args.values()):
        score += 0.1
        reasons.append("url in arguments")
    score = min(score, 1.0)
    decision = "block" if score >= 0.85 else "require_approval" if score >= 0.5 else "allow"
    return RiskEvent(source="tool_call", target=tool, score=score, decision=decision, reasons=reasons)
