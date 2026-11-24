import numpy as np
from docagent.ingest.chunk import chunk_document
from docagent.retrieval.hybrid import HybridIndex


def test_bm25_finds_retention_chunk(doc):
    idx = HybridIndex(chunk_document(doc))
    top, _ = idx.search("how long is personal data retained", k=1, mode="bm25")[0]
    assert top.page == 1


def test_hybrid_with_fake_embedder(doc):
    chunks = chunk_document(doc)
    fake = lambda texts: np.array([[len(t) % 7 + 1, 1.0] for t in texts], dtype="float32")
    idx = HybridIndex(chunks, embedder=fake)
    idx.build_embeddings()
    assert idx.search("retention", k=2)
