import json
import pytest
from docagent.graph.trace import list_examples, load_example, save_example, slug
from docagent.llm.base import extract_json
from docagent.retrieval.meta import EmbedderMismatch, check_meta, write_meta
from docagent.schemas import Draft


def test_extract_json_handles_fences_and_chatter():
    assert json.loads(extract_json('Sure!\n```json\n{"a": 1}\n```\nDone')) == {"a": 1}
    assert json.loads(extract_json('prefix {"claims": [], "abstained": true} suffix'))["abstained"] is True
    assert Draft.model_validate_json(extract_json('```{"claims": [], "abstained": true}```')).abstained


def test_meta_guards_embedder_mismatch(tmp_path):
    p = tmp_path / "meta.json"
    write_meta(p, "fastembed:bge-small", 10, 384)
    assert check_meta(p, "fastembed:bge-small")["dim"] == 384
    with pytest.raises(EmbedderMismatch):
        check_meta(p, "ollama:nomic-embed-text")


def test_examples_roundtrip(tmp_path):
    state = {"question": "How long is data kept?", "report": "- 90 days", "draft": Draft(abstained=True)}
    save_example(state, tmp_path)
    assert list_examples(tmp_path) == ["How long is data kept?"]
    assert load_example("How long is data kept?", tmp_path)["report"] == "- 90 days"
    assert load_example("unknown", tmp_path) is None
    assert slug("A  B!") == "a-b"
