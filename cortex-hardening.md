# MCP Enhancement Suggestions

Analysis of `cortex/` and `reference/mcp-obsidianRAG/` in context of the Hi-Orbit pilot and Claude Code integration blocker.

---

## Critical: Fixes that unblock or break things

### 1. HTTPS blocker — use Caddy in docker-compose instead of proxy scripts

Both `https-proxy.py` and `https-wrapper.sh` are raw TCP tunnels over self-signed certs. Claude Code rejects self-signed certs; that's why Claude Code integration is still blocked. The `socat` approach also breaks SSE (long-lived connections) unpredictably. The right fix is a Caddy service in `docker-compose.yaml` with `tls internal` — it issues a locally-trusted cert that Claude Code accepts. Drop both proxy scripts when it's in place.

### 2. `chunk_overlap_tokens` is defined but never used

In `indexer/indexer.py`, `chunk_overlap_tokens: int = 50` is a settings field, but `chunk_markdown()` never references it. Overlap is the main knob for improving retrieval quality — without it, a query spanning two adjacent chunks will miss one half. Fix: when flushing a chunk, seed the next one with the last N tokens of the current chunk.

### 3. `get_embedding()` in `server.py` creates a new `httpx.AsyncClient` per call

Every `search_notes` invocation opens and closes an HTTP connection. The indexer correctly takes a shared `client` as a parameter. The server should create a persistent client at startup (in `lifespan`) and pass it through.

### 4. Hardcoded absolute path in `docker-compose.yaml`

`docker-compose.yaml` line 62 has:
```yaml
- /home/damien/code/shared/gdrive_kst/Lonnie/Empirical Neoshamanism:/data/obsidian:ro
```
This breaks on any other host. Should be `${OBSIDIAN_MOUNT_PATH}:/data/obsidian:ro` — `OBSIDIAN_MOUNT_PATH` is already defined in `.env`.

---

## Important: Gaps for Hi-Orbit

### 5. Indexer only handles `.md` files

`indexer.py` uses `base.rglob("*.md")`. The Hi-Orbit corpus is mixed — PDF, Word, Markdown, and images/diagrams. PDF and `.docx` support is needed at minimum. PDFs need `pypdf` or `pymupdf`; Word needs `python-docx`. Images require a captioning step (vision model at ingest) — the main open technical risk already called out in `corpus-plan.md`.

### 6. No similarity threshold — dangerous for a support agent

`search_similar_chunks` always returns `limit` results regardless of actual relevance. For Hi-Orbit, returning low-confidence matches is worse than returning nothing — an operator might act on a wrong troubleshooting step. Add a `min_relevance` parameter (default e.g. `0.3`) and filter with `WHERE c.embedding <=> $1::vector < threshold` (distance, lower = more similar).

---

## Minor / Quality

### 7. `list_notes` is unbounded

`server.py` `list_all_notes()` returns every indexed document with no limit. At 289+ docs and growing this will bloat context. Add a `limit` + `offset` or at least a default cap.

### 8. API key committed to reference `.env`

`cortex/.env` contains a live `LITELLM_API_KEY`. Worth rotating and replacing with a placeholder, even if gitignored on the server.

### 9. No vector index = full table scan (known, fine now)

`init.sql` documents that ivfflat/hnsw can't index 4096-dim vectors. At ~600 chunks this is negligible. If the embedding model is ever swapped to a smaller-dim model (e.g. `nomic-embed-text` at 768-dim), add an HNSW index at that point for a significant query speedup at scale.

---

## Comparison: `mcp-obsidianRAG` vs `cortex`

The `mcp-obsidianRAG` bridge uses `subprocess.run` to shell out to a CLI tool — every query forks a process, slow and brittle. Cortex's direct `asyncpg` + pgvector approach is the right architecture. The obsidianRAG reference is useful only as evidence the bridge-service pattern exists; don't inherit its implementation.

---

## Priority order

| # | Fix | Impact |
|---|-----|--------|
| 1 | Caddy TLS in docker-compose | Unblocks Claude Code |
| 2 | Chunk overlap implementation | Retrieval quality |
| 3 | Multi-format indexer (PDF/docx) | Hi-Orbit feasibility |
| 4 | Similarity threshold in search | Hi-Orbit correctness/safety |
| 5 | Hardcoded path → env var | Portability for Hi-Orbit host |
| 6 | Persistent httpx client | Server performance |
| 7 | Rotate API key in reference .env | Security hygiene |
