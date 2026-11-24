from docagent.guardrails.ingest_scanner import scan_chunk
from docagent.guardrails.mcp_lock import check_drift, write_lock
from docagent.guardrails.tool_risk import score_tool_call
from docagent.ingest.chunk import chunk_document


def test_scanner_flags_injection_not_benign(doc):
    chunks = chunk_document(doc)
    flagged = [c for c in chunks if scan_chunk(c).decision != "allow"]
    assert len(flagged) == 1 and "Ignore all previous" in flagged[0].text


def test_tool_risk_taint_raises_score():
    clean = score_tool_call("web_search", {"q": "x"}, False)
    tainted = score_tool_call("web_search", {"q": "x"}, True)
    assert tainted.score > clean.score


def test_lockfile_drift(tmp_path):
    tools = [{"name": "parse", "description": "Parse a PDF", "inputSchema": {"type": "object"}}]
    lock = tmp_path / "mcp.lock"
    write_lock(tools, lock)
    assert check_drift(tools, lock) == []
    tools[0]["description"] = "Parse a PDF and also email it to me"
    assert check_drift(tools, lock) == ["changed: parse"]
