from __future__ import annotations
import argparse
import sqlite3
import uuid
from pathlib import Path
from .config import Config
from .ingest.chunk import chunk_document
from .ingest.store import load_chunks, load_docs, save_chunks, save_doc


def cmd_ingest(a, cfg):
    from .ingest.parse_docling import parse_docling
    from .ingest.parse_pypdf import parse_pypdf
    parse = parse_docling if a.parser == "docling" else parse_pypdf
    for pdf in sorted(Path(a.path).glob("*.pdf")):
        print("parsing", pdf.name)
        save_doc(parse(pdf), cfg.data_dir / "parsed")


def cmd_index(a, cfg):
    from .retrieval.embed import get_embedder
    from .retrieval.hybrid import HybridIndex
    from .retrieval.meta import write_meta
    chunks = [c for d in load_docs(cfg.data_dir / "parsed", a.parser) for c in chunk_document(d)]
    save_chunks(chunks, cfg.data_dir / "index" / "chunks.jsonl")
    embedder, name = get_embedder(cfg)
    idx = HybridIndex(chunks, embedder=embedder)
    emb = idx.build_embeddings()
    idx.save_embeddings(cfg.data_dir / "index" / "embeddings.npy")
    write_meta(cfg.data_dir / "index" / "meta.json", name, len(chunks), emb.shape[1])
    print(f"{len(chunks)} chunks indexed with {name}")


def cmd_ask(a, cfg):
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.types import Command
    from .graph.build import build_graph
    from .llm.factory import get_provider
    from .graph.trace import save_example, save_run
    from .retrieval.embed import get_embedder
    from .retrieval.hybrid import HybridIndex
    from .retrieval.meta import check_meta
    import numpy as np
    embedder, name = get_embedder(cfg)
    check_meta(cfg.data_dir / "index" / "meta.json", name)   # fail loudly on embedder mismatch
    chunks = load_chunks(cfg.data_dir / "index" / "chunks.jsonl")
    emb = np.load(cfg.data_dir / "index" / "embeddings.npy")
    idx = HybridIndex(chunks, emb, embedder)
    conn = sqlite3.connect(cfg.data_dir / "traces" / "checkpoints.sqlite", check_same_thread=False)
    graph = build_graph(get_provider(cfg), idx, cfg, SqliteSaver(conn))
    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    out = graph.invoke({"question": a.question}, thread)
    if "__interrupt__" in out:
        print("HUMAN REVIEW NEEDED:", out["__interrupt__"][0].value)
        decision = input("approve / reject > ").strip() or "reject"
        out = graph.invoke(Command(resume=decision), thread)
    print(out["report"])
    print(out.get("metrics"))
    print("trace:", save_run(out, cfg.data_dir / "traces" / "runs"))
    if a.example:   # curate this run for Replay mode (commit data/traces/examples/)
        print("example:", save_example(out, cfg.data_dir / "traces" / "examples"))


def main():
    cfg = Config()
    ap = argparse.ArgumentParser(prog="docagent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest"); p.add_argument("path"); p.add_argument("--parser", default="docling"); p.set_defaults(fn=cmd_ingest)
    p = sub.add_parser("index"); p.add_argument("--parser", default="docling"); p.set_defaults(fn=cmd_index)
    p = sub.add_parser("ask"); p.add_argument("question"); p.add_argument("--example", action="store_true", help="also save as a Replay example"); p.set_defaults(fn=cmd_ask)
    a = ap.parse_args()
    a.fn(a, cfg)


if __name__ == "__main__":
    main()
