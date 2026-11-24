from docagent.ingest.chunk import chunk_document


def test_footer_dropped_and_table_whole(doc):
    chunks = chunk_document(doc)
    assert all("Page 1 of 9" not in c.text for c in chunks)
    t = [c for c in chunks if c.is_table]
    assert len(t) == 1 and "Backups | 365" in t[0].text and t[0].page == 2


def test_provenance_and_section(doc):
    c = chunk_document(doc)[0]
    assert c.page == 1 and c.element_ids == ["d:1:2"] and c.section_path[-1] == "Data Retention"
