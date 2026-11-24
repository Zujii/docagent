# Architecture

```
PDFs --(local, once)--> Docling/PyPDF --> Document JSON --> chunks.jsonl + embeddings.npy  (committed)
                                                                  |
question --> router(code) --> retrieve(hybrid) --> [ingest scanner] --> write(LLM)
          --> verify(code) --> critic(LLM, optional) --> human gate (interrupt) --> finalize
```

Principles
- Provenance on every chunk: `doc_id`, `page`, `element_ids`. Writer must cite chunk ids + verbatim quote.
- Deterministic verifier before any LLM critic.
- Guardrails at two boundaries: ingestion (content) and tool calls (actions). Toggle via `GUARDRAILS`.
- Heavy work (parsing, embedding, evals) local. Hosted app only queries prebuilt artifacts.
- Providers: ollama (local, headline eval numbers) | api (free tier, demo) | replay (cached traces).
