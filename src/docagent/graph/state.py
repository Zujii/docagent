from __future__ import annotations
import operator
from typing import Annotated, Optional, TypedDict
from ..schemas import Chunk, Draft, Metrics, RiskEvent, VerifyResult


class State(TypedDict, total=False):
    question: str
    question_type: str
    k: int
    retrieved: list[Chunk]
    draft: Draft
    verification: VerifyResult
    critic_confidence: float
    critic_issues: list[str]
    risk_events: Annotated[list[RiskEvent], operator.add]
    needs_human: bool
    human_decision: Optional[str]
    report: str
    metrics: Metrics
