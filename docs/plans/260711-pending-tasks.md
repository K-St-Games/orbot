# Orbot — Pending Tasks (Wiki authoring + retrieval wiring)

**Captured:** 2026-07-12
**Sources:** [`../vision/VISION.md`](../vision/VISION.md) · [`../vision/VISION_FEEDBACK.md`](../vision/VISION_FEEDBACK.md) · [`../orbot-llm-wiki-implementation-plan.md`](../orbot-llm-wiki-implementation-plan.md)

## Where things stand (done)

- **GDrive FUSE mount fixed** — `root_folder_id` re-pointed to the recreated
  `Production/` folder; live through to Hermes at `/opt/gdrive_hiorbit` (read-only).
- **Wiki checkouts in place (two-copy model):**
  - Submodule `orbot/hi-orbit-wiki` (pinned, reviewed `main`) → **Cortex/RAG source**.
    `.git` is a pointer file, so this copy is read-only by nature.
  - Clone `single-compose/projects/hi-orbit-wiki` (real `.git`) → **Hermes authoring
    workspace**, mounted read-write at `/opt/projects/hi-orbit-wiki`. Already
    gitignored via `single-compose/projects/*`.

## Access model (decided)

| Store | Role | Hermes access | RAG-indexed? |
|---|---|---|---|
| GDrive (`/opt/gdrive_hiorbit`) | raw source material | read-only, read directly for authoring | **No** (canonical-first; don't build a source-shaped brain) |
| Wiki `docs/` | canonical output | read-write (authoring) | **Yes** (Cortex indexes reviewed canonical) |

Promotion gate: Hermes authors in the `projects/` clone → pushes branch → engineer
merges PR → `git submodule update --remote hi-orbit-wiki` + commit gitlink → Cortex reindexes.

---

## Task 1 — Fix Cortex (impl-plan Track B)

`cortex/docker-compose.yaml` still hardcodes the dead personal-vault path
`/home/damien/code/shared/.../Empirical Neoshamanism:/data/obsidian:ro` and the old
LiteLLM/4096-dim embedding setup. Bring it to the locked architecture:

- **B1 `init.sql`:** `vector(4096)` → `vector(768)` (nomic-embed-text); add
  `status`/`sensitivity`/`exclude_from_rag` columns; add HNSW index.
- **B2 `indexer/indexer.py`:** parse frontmatter gating fields; swap LiteLLM proxy →
  local Ollama (`/api/embeddings`, `nomic-embed-text`); implement `chunk_overlap_tokens`;
  rename `obsidian_path` → `docs_path` + `evidence_path`, tag `knowledge_tier`.
- **B3 `rag-server/server.py`:** Ollama embedding switch; `min_relevance` filter
  (safety-critical — return "no results above threshold" instead of weak matches);
  `status`/`exclude_from_rag` gating; persistent `httpx.AsyncClient`; `limit`/`offset`.
- **B4 `docker-compose.yaml`:** add `ollama` + `ollama-warmup` (pull `nomic-embed-text`);
  replace the dead bind with `${DOCS_MOUNT_PATH:-../hi-orbit-wiki/docs}` +
  `${EVIDENCE_MOUNT_PATH:-../hi-orbit-wiki/evidence}` (note: submodule is named
  `hi-orbit-wiki`, not the plan's placeholder `wiki`); bind postgres/rag-server to
  `127.0.0.1`; add `cortex/.env.example`.
- **B5:** delete dead homelab files `https-proxy.py`, `https-wrapper.sh`, `mcp-config.json`.

**Verify:** `docker compose --profile full up -d` healthy; indexer logs "0 files" cleanly
against empty dirs; `curl 127.0.0.1:8100/health` → `{"status":"healthy","documents":0}`;
insert one throwaway 768-dim row, confirm `search_notes` returns it and a nonsense query
hits the relevance floor; delete the test row.

## Task 2 — Wire Hermes → Cortex (impl-plan Track C)

`bot_memory/orbot/.hermes/config.yaml` has no `mcp_servers:` key. Add:

```yaml
mcp_servers:
  cortex:
    url: "http://127.0.0.1:8100/sse"
    tools:
      include: [search_notes, get_note, list_notes, get_stats]
      prompts: false
      resources: false
```

Hermes runs `network_mode: host`, so it reaches Cortex's host-published port directly at
`127.0.0.1:8100` — no shared Docker network needed. **Verify:** restart the Hermes stack,
confirm `/reload-mcp` (or fresh session) shows the `cortex` server connected with its tools.

## Task 3 — GitHub credentials for the authoring/PR loop  (mostly done)

The vision requires Hermes to author via **drafts/branches/PRs with human review**, so the
`projects/` clone needs push + PR access. No `gh` CLI in the image → Hermes uses its
`github-*` skills' **`git` + `curl` + `$GITHUB_TOKEN`** path (fully supported).

- [x] **Fine-grained PAT** for `K-St-Games/hi-orbit-wiki` only — Contents: R/W, Pull
      requests: R/W, short expiry. (Best practice: on a dedicated bot account, not personal.)
- [x] **Token in Hermes runtime `.env`** (`bot_memory/orbot/.hermes/.env`, `600`, gitignored)
      as `GITHUB_TOKEN=…` — NOT the compose `.env` (compose is substitution-only; Hermes
      `load_dotenv`s its own home `.env`).
- [x] **Git wired in the clone** (`single-compose/projects/hi-orbit-wiki`): tokenless
      credential helper that echoes `$GITHUB_TOKEN` at push time (no token in `.git/config`),
      plus commit identity `Orbot (Hermes)`.
- [ ] **Verify (Task-4 restart):** `docker restart orbot-hermes`, then
      `docker exec orbot-hermes sh -c 'printenv GITHUB_TOKEN >/dev/null && echo yes'` and
      `docker exec -w /opt/projects/hi-orbit-wiki orbot-hermes git ls-remote origin -h`.

**Load-bearing caveat:** everything rides on `$GITHUB_TOKEN` reaching the agent's shell env.
The skill's file fallback greps `~/.hermes/.env`, but this image has `HOME=/root` and no
`/root/.hermes`, so that fallback won't find `/opt/data/.env`. If the verify `printenv`
shows nothing, add `GITHUB_TOKEN` to the Hermes service `environment:` in compose (same
documented exception already used for `API_SERVER_KEY`).

**Scope guard:** push + PR-open only — nothing that enables auto-merge. The human review
gate is the point.

---

## Sequencing

1. **Task 1 (Cortex)** and **Task 3 (token)** are independent — can proceed in parallel.
2. **Task 2 (MCP wiring)** depends on Task 1 (Cortex must be healthy and reachable first).
3. Full authoring loop is unblocked once all three land; first vertical slice is
   Payphone → Laser Maze (per VISION_FEEDBACK).
