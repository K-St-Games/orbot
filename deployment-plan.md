# Hi-Orbit — Deployment Plan

**Status:** v0.1 draft
**Composes:** the v0 Hermes recipe + rclone Drive mount + RAG over the design docs +
the Hi-Orbit persona. This is the ordered build; it references the shared docs rather
than duplicating them.

---

## Target shape

> Full composed view, decisions, and the three read/write zones:
> [`architecture.md`](architecture.md). This section is the build-order summary.

```
new dedicated host (on-site)
├── DURABLE SHARED INFRA (engine-agnostic, own compose, shared net)
│     ├── rclone mount  ← Google Drive design docs (read-only) at /opt/gdrive_kst
│     ├── brain-builder ← convert+caption corpus → markdown "brain" (writable, git-tracked)
│     ├── ollama        ← local embeddings (nomic-embed-text, 768-dim)
│     └── Cortex        ← postgres (pgvector+BM25) + indexer + rag-server (MCP/SSE)
└── AGENT (swappable, own compose)
      └── Hermes (docker, per hermes-recipe/deploy-hermes-agent.md)
            ├── Discord gateway ← operators (restricted users), require_mention
            ├── identity        ← SOUL.md (Hi-Orbit support persona)
            ├── retrieval       ← Cortex MCP (cited answers)
            └── output          → writable "orbot output" zone (escalation/session notes)
```

## Build order

1. **Prep the dedicated host.** OS, Docker 24+, the deploy user (note UID/GID),
   code-root layout. → fills preflight §A/§F.
   - *Verify:* `docker compose version` works; layout matches v0 Step 3.

2. **Stand up Hermes (Discord).** Follow [`hermes-recipe/deploy-hermes-agent.md`](hermes-recipe/deploy-hermes-agent.md)
   with the Hi-Orbit `.env` values: a **dedicated Discord bot/token**, operators
   restricted (`DISCORD_ALLOW_ALL_USERS=false` + `DISCORD_ALLOWED_USERS`), the
   operator channel(s) in `allowed_channels`.
   - *Verify:* bot connects; responds to an operator @mention; ignores other users.
   - *Human gate:* yes (Discord token, access policy).

3. **Mount the design-doc corpus.** Configure an rclone Google Drive remote
   (read-only, least-privilege; SA preferred) and mount at `shared/gdrive_kst` →
   `/opt/gdrive_kst`. See [`playbooks/google-drive.md`](playbooks/google-drive.md).
   - *Verify:* `ls` of the mount shows the design docs.
   - *Human gate:* yes (grants Drive access).

4. **Build the markdown brain (Zone 2).** Convert the read-only corpus to markdown +
   YAML frontmatter, captioning diagrams at ingest; carry `source_path`/section,
   `status`, `sensitivity`, `exclude_from_rag`, `caption_reviewed`. See
   [`corpus-plan.md`](corpus-plan.md) + [`playbooks/gdrive-markdown-brain.md`](playbooks/gdrive-markdown-brain.md).
   - *Verify:* a sample PDF/Word/diagram each produces a reviewable markdown file with
     correct frontmatter; the engineer spot-checks diagram captions (`caption_reviewed`).
   - *Human gate:* yes (engineer reviews captions before operators rely on them).

5. **Stand up local embeddings (Ollama).** Run `ollama` on the shared network with
   `nomic-embed-text`; persist the models volume. See [`architecture.md`](architecture.md) §6.
   - *Verify:* `curl ollama:11434` healthy; an embed call returns a 768-dim vector.
   - *Human gate:* no (but confirm host can carry Ollama + Hermes + Postgres — §6).

6. **Stand up Cortex + index the brain.** Bring up `cortex-postgres`, `cortex-indexer`,
   `cortex-rag-server` (gate on Postgres healthy); point the indexer at the **brain**
   (Zone 2), embeddings at Ollama. Apply the hardening checklist in
   [`architecture.md`](architecture.md) §8 — **the `min_relevance` threshold is non-negotiable.**
   - *Verify:* `search_notes` returns a **cited** chunk for a known fault; a below-threshold
     query returns **nothing** (→ agent will escalate); a diagram query surfaces the
     captioned image + asset link.
   - *Human gate:* no (internal HTTP on the shared net; no off-host TLS needed — §7).

7. **Install the persona + wire retrieval.** Load `SOUL.md` as the agent identity; add the
   Cortex MCP endpoint (`http://cortex-rag-server:8100/sse`) to `config.yaml`; instruct
   retrieve-then-answer-with-citation and the safety/escalation rules from `SOUL.md`.
   Point the agent's output at the writable **Zone 3** folder.
   - *Verify:* end-to-end test below.

## End-to-end acceptance

- An operator describes a common fault for a documented puzzle → the agent asks for
  symptoms if needed, returns a correct, **cited** step-by-step, and confirms the fix.
- An **uncovered** issue → the agent says the docs don't cover it and **escalates**.
- A **safety-relevant** symptom (trapped guest, failed release) → the agent
  prioritizes guest safety and points to the engineer/on-site lead, not a DIY fix.
- A user who is **not** an operator → no response.

## Still to resolve before this runs (see architecture.md §9 + preflight)
- **Brain-builder build vs buy** — is conversion+captioning a small custom job or a
  wrapped existing tool? (Main net-new code.)
- **Host sizing** — confirm the box carries Ollama + Hermes + Postgres concurrently.
- Corpus structure → chunking; **re-index trigger** (nightly vs on-Drive-change).
- **Escalation mechanism** (channel ping / ticket) → lands in the writable Zone 3 output.
- Concrete secrets/IDs (Discord, rclone/Drive, host) — collected into the runtime
  secrets store, never the repo.

*(Resolved since v0.1: engine = Hermes; retrieval = Cortex MCP; diagrams = caption-at-ingest
into the reviewed brain; embeddings = local Ollama. See [`architecture.md`](architecture.md).)*
