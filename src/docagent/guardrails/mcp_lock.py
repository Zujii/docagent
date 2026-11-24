"""Lockfile-style pinning for MCP tool definitions; detect description/schema drift (rug-pulls)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def tool_hash(tool: dict) -> str:
    canon = json.dumps({k: tool.get(k) for k in ("name", "description", "inputSchema")},
                       sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()


def write_lock(tools: list[dict], path: Path) -> None:
    Path(path).write_text(json.dumps({t["name"]: tool_hash(t) for t in tools}, indent=2, sort_keys=True))


def check_drift(tools: list[dict], path: Path) -> list[str]:
    """Return human-readable drift findings; empty list == clean."""
    locked = json.loads(Path(path).read_text())
    seen = {t["name"]: tool_hash(t) for t in tools}
    out = [f"changed: {n}" for n in seen if n in locked and seen[n] != locked[n]]
    out += [f"new (unpinned): {n}" for n in seen if n not in locked]
    out += [f"missing: {n}" for n in locked if n not in seen]
    return out
