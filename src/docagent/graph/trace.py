"""Save finished runs as JSON. Saved examples power Replay mode and the audit-trail tab."""
from __future__ import annotations
import json
import re
import time
from pathlib import Path
from pydantic import BaseModel


def slug(question: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:60] or "q"


def serialize(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items() if k != "__interrupt__"}
    if isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]
    return obj


def save_run(state: dict, runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    path = runs_dir / f"{int(time.time())}-{slug(state.get('question', ''))}.json"
    path.write_text(json.dumps(serialize(state), indent=1, default=str))
    return path


def save_example(state: dict, examples_dir: Path) -> Path:
    """Curated runs committed to the repo; Replay mode serves these by question."""
    examples_dir.mkdir(parents=True, exist_ok=True)
    path = examples_dir / f"{slug(state['question'])}.json"
    path.write_text(json.dumps(serialize(state), indent=1, default=str))
    return path


def list_examples(examples_dir: Path) -> list[str]:
    return [json.loads(p.read_text())["question"] for p in sorted(Path(examples_dir).glob("*.json"))]


def load_example(question: str, examples_dir: Path) -> dict | None:
    p = Path(examples_dir) / f"{slug(question)}.json"
    return json.loads(p.read_text()) if p.exists() else None
