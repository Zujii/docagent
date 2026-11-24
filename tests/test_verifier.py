from docagent.graph.verifier import verify_draft
from docagent.ingest.chunk import chunk_document
from docagent.schemas import Claim, Draft


def test_verifier(doc):
    chunks = chunk_document(doc)
    by_id = {c.chunk_id: c for c in chunks}
    cid = chunks[0].chunk_id
    good = Claim(text="Data is kept 90 days.", chunk_ids=[cid], quote="retain personal data for 90 days")
    bad_quote = Claim(text="Data is kept 90 days.", chunk_ids=[cid], quote="we sell data to partners")
    bad_num = Claim(text="Data is kept 120 days.", chunk_ids=[cid], quote="retain personal data for 90 days")
    no_cite = Claim(text="Something.", chunk_ids=[], quote="")
    vr = verify_draft(Draft(claims=[good, bad_quote, bad_num, no_cite]), by_id)
    assert [v.ok for v in vr.verdicts] == [True, False, False, False]
    assert vr.pass_rate == 0.25
