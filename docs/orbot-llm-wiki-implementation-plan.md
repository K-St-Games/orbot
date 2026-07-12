# Orbot LLM Wiki — Implementation Plan (Scaffolding + Cortex Fix)

> **Historical plan:** do not execute this document verbatim. `hi-orbit-wiki/` now exists
> as a submodule, the product vision has been approved and refined, and the forthcoming
> `MVP_ROADMAP.md` will re-sequence this work with explicit contracts and gates. See
> [`../CURRENT_TASK.md`](../CURRENT_TASK.md).

## Context

`docs/orbot-llm-wiki-product-proposal.md` proposes evolving Orbot from a plain RAG
chatbot into an agent-maintained Markdown wiki (canonical `docs/` + `evidence/` layers,
published via MkDocs, indexed by Cortex, maintained by Hermes).

Grounding the proposal against actual repo state surfaced two things that reshape scope:

1. **The Google Drive corpus mount is empty** — zero files. `preflight.md` always marked
   Drive access `TBD`, and nothing on disk (including `hi-orbit.old`) has real escape-room
   design content. Confirmed with user: build scaffolding only, no synthetic content, no
   ingestion run this pass.
2. **`cortex/` is a vendored copy of an unrelated personal project** — it indexes someone's
   private Obsidian vault, embeds via a remote homelab LiteLLM proxy
   (`100.67.191.114:4000`) with `qwen3-embedding-8b` (4096-dim), and has a hardcoded bind
   mount to `/home/damien/code/shared/gdrive_kst/Lonnie/Empirical Neoshamanism`. This
   contradicts `architecture.md`'s locked decision (local Ollama, `nomic-embed-text`,
   768-dim) and isn't wired into Hermes at all (`config.yaml` has no `mcp_servers:` key).
   Confirmed with user: fix this now, as part of this pass.

At the time this plan was written, the environment had no authenticated `gh` session, so
the proposed `hi-orbit-wiki` repository was to be built and committed locally for the user
to push. The repository and submodule now exist.

**Outcome of this pass:** a scaffolded, empty wiki repo ready to receive real content the
moment it lands in Drive, and a Cortex stack that's correctly pointed, correctly embedded,
safety-hardened, and reachable from Hermes — verified against zero/synthetic rows, not
real operational data.

---

## Track A — `hi-orbit-wiki` standalone repo (now linked as a submodule)

This track described building an independent `hi-orbit-wiki` repository. It now exists
and is linked at the parent repository's `hi-orbit-wiki/` path.

Structure (trimmed from proposal §7 — no content files, just navigable scaffolding):

```
hi-orbit-wiki/
├── README.md                       # what this repo is, how it relates to orbot/
├── AGENTS.md                       # wiki constitution — proposal §12, verbatim rules
├── mkdocs.yml                      # nav skeleton, material theme
├── docs/
│   ├── index.md                    # landing page explaining the structure
│   └── {rooms,puzzles,systems,components,procedures,troubleshooting,reference}/
│       └── .gitkeep
├── evidence/.gitkeep
├── _meta/
│   ├── source-manifest.yaml        # header + schema comment, empty list
│   ├── ingestion-log.md            # header only
│   ├── unresolved-questions.md     # header only
│   ├── contradictions.md           # header only
│   └── documentation-health.md     # header only
├── _drafts/.gitkeep
├── templates/
│   ├── puzzle-article.md           # proposal §9, as a copyable template
│   └── evidence-note.md            # proposal §10, as a copyable template
└── tools/
    ├── requirements.txt            # python-frontmatter, pyyaml
    ├── check_frontmatter.py        # validates required keys per doc type
    └── check_links.py              # flags broken relative links/images
```

Notes:
- `check_frontmatter.py` / `check_links.py` are real, working scripts (deterministic,
  Stage-A-style per `playbooks/gdrive-markdown-brain.md` §6) — testable now by running
  them against `templates/` and the empty `docs/` tree (expect clean exit).
- Explicitly **not** building `build-source-manifest.py` or any evidence-extraction
  (Stage B / LLM) tooling this pass — no Drive content to run it against. Note this as a
  deferred next-phase item in the wiki `README.md`.
- `AGENTS.md` carries proposal §12's rules directly (canonical-vs-evidence, never
  silently resolve contradictions, operator-first structure, safety-gated review).

---

## Track B — Fix `orbot/cortex/`

### B1. `cortex/init.sql`
- `embedding vector(4096)` → `vector(768)` (matches `nomic-embed-text`).
- Add `documents.status`, `documents.sensitivity`, `documents.exclude_from_rag` columns
  (defaults: `current`, `operator`, `false`) — these are the frontmatter gating fields
  already locked in `architecture.md` §4, not new scope from the wiki proposal.
- Add an HNSW index now that 768-dim is indexable (the old comment explaining why it was
  omitted no longer applies).

### B2. `cortex/indexer/indexer.py`
- Parse YAML frontmatter (`python-frontmatter`, new dependency) for `status`,
  `sensitivity`, `exclude_from_rag`; persist on the `documents` row.
- Replace the LiteLLM-proxy embedding call with local Ollama (`POST /api/embeddings`,
  new `ollama_url` setting replacing `litellm_url` as primary path).
  `embedding_model` default → `nomic-embed-text`.
- Implement `chunk_overlap_tokens` in `chunk_markdown()` — currently defined, unused
  (cortex-hardening.md #2): seed each new chunk with the trailing N tokens of the
  previous one.
- Rename `obsidian_path`/`OBSIDIAN_PATH` → two roots, `docs_path`/`DOCS_PATH` and
  `evidence_path`/`EVIDENCE_PATH`; tag each indexed chunk's `knowledge_tier`
  (`canonical` vs `evidence`) by which root it came from (cheap groundwork for proposal
  §14, not the full retrieval-hierarchy logic — that needs real content to validate).

### B3. `cortex/rag-server/server.py`
- Same embedding-provider switch (Ollama, not LiteLLM proxy).
- Add `min_relevance` filtering to `search_similar_chunks`/`search_notes`
  (cortex-hardening.md #6 — the safety-critical gap): filter `1 - distance >= min_relevance`
  (default ~0.3), return an explicit "no results above relevance threshold" message
  instead of weak matches.
- Add `status`/`exclude_from_rag` gating to the same query (only `current`,
  non-excluded rows) — the mechanism behind SOUL.md's "never guess, escalate" rule.
- Persistent `httpx.AsyncClient` created in `lifespan`, reused across `get_embedding()`
  calls, instead of one per request (#3).
- `list_all_notes()` gets `limit`/`offset` params with a default cap (#7).

### B4. `cortex/docker-compose.yaml`
- Add `ollama` service (`ollama/ollama` image, persisted models volume) + a one-shot
  `ollama-warmup` service that runs `ollama pull nomic-embed-text`, mirroring the
  existing `rclone-warmup` pattern in `single-compose/docker-compose.yml`.
- Remove the hardcoded `/home/damien/code/shared/gdrive_kst/Lonnie/Empirical
  Neoshamanism` bind mount. Replace with `${DOCS_MOUNT_PATH:-../hi-orbit-wiki/docs}` and
  `${EVIDENCE_MOUNT_PATH:-../hi-orbit-wiki/evidence}` — points at the submodule from
  `cortex/`.
- Drop `LITELLM_URL`/`LITELLM_API_KEY` as the primary embedding path (keep as an
  optional documented fallback var, no committed key — there's no live `cortex/.env` on
  disk today, so nothing to rotate, just don't reintroduce the pattern).
- Bind `postgres` and `rag-server` ports to `127.0.0.1` instead of all interfaces,
  matching `AGENTS.md`'s "don't publish management surfaces on a venue network" rule.
- Add `cortex/.env.example` documenting the renamed/new vars (none of this currently
  exists — no `.env.example` is present today).

### B5. Remove homelab-specific dead files
`cortex/https-proxy.py`, `cortex/https-wrapper.sh`, `cortex/mcp-config.json` — all
reference the old MetaMCP/AnythingLLM/self-signed-TLS setup that `architecture.md`
explicitly supersedes (Hermes talks to Cortex directly over plain internal HTTP; no
off-host TLS needed for this pilot). Keeping them risks a future reader trying to wire
up infrastructure that isn't part of this design.

---

## Track C — Wire Hermes → Cortex

`single-compose/bot_memory/orbot/.hermes/config.yaml` currently has no `mcp_servers:`
key at all. Per `hermes-agent`'s own docs
(`single-compose/hermes-agent/website/docs/guides/use-mcp-with-hermes.md`, "Pattern 4:
documentation / knowledge servers"), add:

```yaml
mcp_servers:
  cortex:
    url: "http://127.0.0.1:8100/sse"
    tools:
      include: [search_notes, get_note, list_notes, get_stats]
      prompts: false
      resources: false
```

Hermes runs `network_mode: host` (deliberately, per the docker-compose comment — "avoids
deviating from the supported path"). Rather than reconciling that with Cortex's bridge
network (flagged as an open problem in `BUILD-KIT.md` §5), the fix is simpler: Cortex's
`rag-server` already publishes its port to the host, so Hermes reaches it via
`127.0.0.1:8100` directly — no shared Docker network needed. This resolves the
previously-flagged networking tension without touching Hermes's validated host-network
setup.

No SOUL.md changes — its retrieve-then-cite/escalate behavior already describes this
exact flow; it just hasn't had a retrieval backend to call.

---

## Verification

- `hi-orbit-wiki/tools/check_frontmatter.py` and `check_links.py` run clean (exit 0) against
  `templates/` and the empty `docs/` tree.
- `cd hi-orbit-wiki && mkdocs build` succeeds and produces a navigable site from `docs/index.md`.
- `cd orbot/cortex && docker compose --profile full up -d` — postgres, ollama (+ warmup
  pulling `nomic-embed-text`), indexer, rag-server all healthy; indexer logs "0 files to
  index" cleanly against the empty mounted dirs (no crash on empty corpus).
- `curl http://127.0.0.1:8100/health` returns `{"status": "healthy", "documents": 0,
  "chunks": 0}`.
- Manually insert one throwaway test row (title + fake 768-dim embedding) into `chunks`/
  `documents`, confirm `search_notes` returns it above threshold and a nonsense query
  returns "no results above relevance threshold" — proves the min-relevance gate works
  without needing real content. Delete the test row after.
- Restart the Hermes stack (`docker compose up -d` in `single-compose/`), confirm
  `/reload-mcp` (or a fresh session) shows the `cortex` MCP server connected and
  `search_notes`/`get_note`/`list_notes`/`get_stats` tools available.
- `docker ps` — confirm nothing on `orbot-rclone`, `orbot-hermes`, or the GDrive FUSE
  mount was disturbed by this work (this track only touches `cortex/` and one Hermes
  config file, plus one bind-mount path recheck).
