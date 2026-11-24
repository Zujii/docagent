# Gold set format (one JSON object per line in gold.jsonl)

| field | meaning |
|---|---|
| id | unique id |
| split | `dev` (tune on this) or `test` (frozen; never tune on it) |
| type | lookup, multi_hop, table, comparison, unanswerable |
| question | the question |
| answer | expected answer (null if unanswerable) |
| support | list of `{doc, page}` that justify the answer (doc = doc_id from data/parsed) |
| answerable | false => system should abstain |

Aim for 40-60 questions, ~10-15% unanswerable. See gold.example.jsonl.
