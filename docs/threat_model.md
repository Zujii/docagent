# Threat model (fill in as you build)

**Assets:** user documents, tool permissions, report integrity.
**Attackers:** authors of uploaded documents or fetched web pages (indirect prompt injection); a tampered MCP server (tool-description drift / rug-pull).

| Threat | Where it enters | Control | Measured by |
|---|---|---|---|
| Instructions hidden in document text/tables/footers | ingestion | ingest scanner (rules + classifier), quarantine | detection rate, FPR |
| Injected text triggers a risky tool call | agent runtime | tool-call risk scorer, approval gate | attack success rate (on vs off) |
| Exfiltration via final report (URLs/emails) | output | output scan | tests |
| MCP tool description/schema changes after approval | MCP boundary | Lockfile hashes + drift check | CI drift test |
| Fabricated or misattributed citations | writer | deterministic verifier | unsupported-claim rate |

**Out of scope / known limits:** write these honestly (e.g. hidden-text visibility depends on what the parser exposes).
