# Hi-Orbit — Composed Architecture

**Status:** v0.1 — decisions locked, ready to build against
**Date:** 2026-06-25
**Composes:** [`deployment-plan.md`](deployment-plan.md) (Hermes recipe) +
[`agent-access-recipe.md`](agent-access-recipe.md) (rclone/Discord/workspace) +
[`corpus-plan.md`](corpus-plan.md) (ingestion) +
[`playbooks/gdrive-markdown-brain.md`](playbooks/gdrive-markdown-brain.md) +
Cortex (retrieval engine, `cortex/`).

This is the single composed view of how the pilot's pieces fit. It supersedes the
scattered "RAG search tool" hand-waving in the older docs by naming the actual engine
(Cortex), the actual embedding host (local Ollama), and the read/write boundaries.

---

## 1. Decisions locked

| Decision | Choice | Why |
|---|---|---|
| **Runtime** | **Hermes** (NousResearch) | Pilot engine of record; reuses the v0 recipe; native `SOUL.md`, `auxiliary.vision` slot. |
| **Retrieval** | **Cortex** (hybrid pgvector + BM25, MCP) | Self-hosted, cited search; already exists; metadata gating fits the safety rules. |
| **Embeddings** | **Local — Ollama on the host** (`nomic-embed-text`, 768-dim) | Query-time dependency must survive a venue-network outage; hybrid degrades to BM25 if it stalls. |
| **Citation path** | Agent answers **from Cortex MCP results** (carry source+section) | File-on-disk access alone can't guarantee citations (SOUL requirement). |
| **Corpus access** | **rclone FUSE mount, read-only** | Source of truth; never mutated by the agent. |
| **Ingest** | **Markdown "second brain"** as the canonical indexed artifact | Bridges the format gap, gives a *reviewable* home for diagram captions, hosts the metadata gating. |
| **Write zones** | **Three** — read-only corpus / writable brain / writable output | Different governance per zone; a write bug can't reach the design docs. |
| **Topology** | Cortex + rclone + Ollama as **durable shared infra**; Hermes agent as the **swappable** service | Postgres index is precious; infra is engine-agnostic (runtime-adaptation seam). |

---

## 2. Topology

```
                       Google Shared Drive (design docs: PDF/Word/MD/images)
                                     │  rclone, scope=drive.readonly
                                     ▼
  ┌──────────────────────────── DURABLE SHARED INFRA (engine-agnostic) ───────────────────────────┐
  │                                                                                                │
  │   rclone-gdrive (privileged, /dev/fuse)                                                        │
  │     └─► host path  shared/gdrive_kst   ──(ro bind)──►  [ZONE 1: CORPUS, read-only]             │
  │                                                                                                │
  │   brain-builder (convert + caption)  reads CORPUS ──►  [ZONE 2: BRAIN, writable, git-tracked]  │
  │                                       (md + YAML frontmatter; diagram captions; gating tags)   │
  │                                                                                                │
  │   ollama (nomic-embed-text, 768-dim) ◄──embeds──┐                                              │
  │                                                 │                                              │
  │   cortex-indexer  reads BRAIN ──chunks──► embeds├─► cortex-postgres (pgvector HNSW + pg_bm25)  │
  │                                                 │            ▲                                 │
  │   cortex-rag-server (FastAPI + MCP/SSE) ────────┘────────────┘                                 │
  │        exposes search_notes / get_note / list_notes / get_stats                                │
  └───────────────────────────────────────────────┬────────────────────────────────────────────-─┘
                                                   │  MCP over SSE (internal HTTP on shared net)
                                                   ▼
  ┌──────────────────────────── SWAPPABLE AGENT (engine-specific) ─────────────────────────────────┐
  │   hermes-agent (gateway)  +  hermes-dashboard (127.0.0.1:9119)                                  │
  │     ├── identity        ← SOUL.md (HERMES_HOME)                                                 │
  │     ├── Discord         ← operators only (DISCORD_ALLOWED_USERS), require_mention               │
  │     ├── retrieval       ← Cortex MCP  (cited answers)                                           │
  │     ├── corpus (view)   ← CORPUS read-only mount (secondary: show the actual diagram)           │
  │     └── output          ─► [ZONE 3: OUTPUT, writable]  (escalation summaries, session notes)    │
  └───────────────────────────────────────────────────────────────────────────────────────────────┘
```

Two compose projects on one shared external docker network (`hi-orbit-net`):
- **infra**: `rclone-gdrive`, `ollama`, `cortex-postgres`, `cortex-indexer`,
  `cortex-rag-server` (+ the `brain-builder` job).
- **agent**: `hermes-agent`, `hermes-dashboard`.

Keeping them separate means an agent rebuild never risks the Postgres index or the FUSE
mount, and the whole infra half is reusable across engines/bots.

---

## 3. The three read/write zones

| Zone | Backing | Mount/scope | Who writes | Governance |
|---|---|---|---|---|
| **1. Corpus** | `gdrive_kst` design docs | rclone `drive.readonly` + read-only bind | nobody (the design engineer edits in Drive) | Source of truth; read-only **by construction**, not by agent behavior. |
| **2. Brain** | git-tracked markdown + frontmatter | local writable volume | `brain-builder` (machine) → **engineer review** | The reviewable derived layer. Diagram captions and gating tags live here and are spot-checked **before** operators rely on them. |
| **3. Output** | "orbot output" folder/remote | local writable volume (or a `drive` write remote) | the agent | Operational exhaust: escalation summaries, "what worked" notes, session logs. Isolated so a write bug can't touch Zone 1. |

This is the concrete form of "read-only main Drive + a writable output folder" — split into
three because the *derived brain* (reviewed) and *agent output* (logged) have different
review needs.

---

## 4. Ingest pipeline (the brain)

```
ZONE 1 corpus (PDF / Word / MD / images, read-only)
   │
   ├─ PDF (digital)  → text-layer extract (keep page #s for citation)
   ├─ PDF (scanned)  → OCR (flag low-confidence)
   ├─ Word (.docx)   → extract text + headings
   ├─ Markdown/text  → pass through (cleanest citations)
   └─ Images/diagrams→ vision caption + label extraction
        │
        ▼
ZONE 2 brain: one markdown file per source, YAML frontmatter:
   ---
   source_path: <drive path>          # for citation
   section / page: <…>
   status: current | superseded       # freshness gate
   sensitivity: operator | engineer   # access gate
   exclude_from_rag: false
   caption_reviewed: true|false       # diagram-caption review flag
   tags: [puzzle-3, maglock, …]
   ---
        │  cortex-indexer (chunk 600–900 tok on heading boundaries; embed via Ollama)
        ▼
cortex-postgres (pgvector HNSW + pg_bm25)  ──►  rag-server  ──MCP──►  Hermes
```

**Why caption-at-ingest, not query-time vision:** captions of safety-relevant hardware
must be human-checkable. The brain makes them reviewable (`caption_reviewed`) before an
operator can act on them. Hermes's `auxiliary.vision` is kept as an *enhancement* — to
**show the operator the actual diagram** — not as the retrieval path. (Phenomenology
guardrail, per `corpus-plan.md` + `cartridge-visual-architecture-readout.md`.)

---

## 5. Retrieval safety — mechanism, not just instructions

The SOUL says *"I never guess; I escalate when the docs don't cover it."* That behavior is
backed at the **retrieval layer** so the model can't drift from it:

1. **Similarity threshold (`min_relevance`).** Cortex must filter low-confidence matches
   (`WHERE embedding <=> query < threshold`) and return **nothing** rather than a weak
   guess. *No-result → the agent escalates.* This is the single most important Cortex
   change before the pilot (a known gap — `cortex-hardening.md` #6).
2. **Status gating.** Index only `status: current`; stale/superseded docs never surface.
   Answers the corpus-plan freshness/re-index open question at the retrieval layer.
3. **Sensitivity / `exclude_from_rag`.** Engineer-only notes are never served to operators.
4. **Hybrid as resilience.** If Ollama momentarily stalls, BM25 keyword still returns
   grounded, cited results instead of failing the operator mid-shift.

---

## 6. Local embeddings (the added container)

Vector search embeds the **query** on every answer, so the embedding endpoint is a
*runtime* dependency, not just an indexing one. Hence **Ollama runs locally on the host.**

- **Service:** `ollama` on `hi-orbit-net`, model `nomic-embed-text` (768-dim), models
  volume persisted. Cortex points `OLLAMA_URL=http://ollama:11434`, `LITELLM_URL` as
  fallback.
- **Why local:** a venue-network / Tailscale outage must not take the troubleshooting
  agent offline. Local keeps query embedding and re-indexing self-contained.
- **Throughput:** ~3–4 docs/min indexing (embedding-bound); query embedding is sub-second.
  Fine for a hundreds-of-docs corpus that changes occasionally.
- **Host requirement (confirm in preflight):** the box must run Ollama embeddings **and**
  the Hermes agent **and** Postgres concurrently. `nomic-embed-text` is small and CPU-viable;
  a GPU only speeds the initial bulk index, not steady-state queries.

---

## 7. Transport / exposure

- **Agent ↔ Cortex:** plain **HTTP over the internal docker network** (`http://cortex-rag-server:8100/sse`).
  TLS is only needed to expose Cortex *off-host* — so Cortex's open Caddy/HTTPS blocker
  (`cortex-hardening.md` #1) does **not** gate this pilot.
- **Hermes dashboard:** `127.0.0.1:9119`; reach it via SSH tunnel, don't publish.
- **rclone WebGUI / Hermes gateway:** do **not** publish on a venue network by default;
  bind to localhost/Tailscale. Change rclone's `admin/admin` if ever exposed.
- **Corpus mount:** `drive.readonly` + read-only bind.

---

## 8. Cortex hardening checklist (before operators touch it)

From `cortex-hardening.md`, the pilot-blocking subset:

- [ ] **`min_relevance` threshold** in search (#6) — *correctness/safety; non-negotiable.*
- [ ] **Multi-format ingest** (#5) — delivered via the brain-builder (PDF/docx/OCR/caption).
- [ ] **Chunk overlap** actually applied (#2) — retrieval quality.
- [ ] **Hardcoded corpus path → env var** (#4) — portability to the Hi-Orbit host.
- [ ] **Persistent httpx client** in rag-server (#3) — perf.
- [ ] **Rotate the committed `LITELLM_API_KEY`** in the reference `.env` (#8).
- [ ] HNSW index appropriate for 768-dim (#9) once on `nomic-embed-text`.

---

## 9. Open questions this resolves / leaves

**Resolved:**
- Engine of record → **Hermes**.
- Cited-retrieval architecture → **Cortex via MCP** (not direct file read).
- Diagram searchability (corpus-plan #1) → **caption-at-ingest into the reviewed brain**;
  `auxiliary.vision` for display.
- Re-index/freshness (corpus-plan #2/#3) → **`status` gating + scheduled `POST /reindex`**.
- Read/write safety → **three zones**, corpus read-only by construction.

**Still open:**
- **Escalation mechanism** (README #3) — channel ping vs ticket; the writable **output**
  zone is the natural home for the handoff artifact.
- **Operator identities** (README #4) — `DISCORD_ALLOWED_USERS` values to collect.
- **Host sizing** — confirm the box carries Ollama + Hermes + Postgres (see §6).
- **Brain-builder build vs buy** — is conversion+captioning a small custom job, or an
  existing tool wrapped? (Scoping needed; it's the main net-new code.)
- **Re-index trigger** — scheduled nightly vs on-Drive-change.

---

*Runtime-adaptation note: everything in the infra half (rclone, Ollama, Cortex) is
engine-agnostic and unchanged if the agent later moves off Hermes. Only the agent service
is engine-specific. That is the cartridge/runtime seam, applied to a real deployment.*
