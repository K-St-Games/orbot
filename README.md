# Pilot: Hi-Orbit — Operator Tech-Support Agent

**Status:** v0.1 — scoping
**Owner:** —
**Last updated:** 2026-06-04
**Type:** Deployment pilot (composes a deployment recipe + RAG + a scoped persona)

---

## What this is

An internal technical-support chatbot for **Hi-Orbit Games**, an escape-room
installation. The agent is an interface for **game operator employees** to talk
through **technical troubleshooting** during operations — "the X puzzle isn't
resetting," "the maglock on Y won't release" — grounded in the **design documents**
for the installation's puzzles.

It stands in for asking the design engineer directly: operators get fast,
document-grounded troubleshooting guidance, and the engineer is escalated to only
when the docs don't cover it.

## Who it's for

Game operators — **not** engineers. They know the room and the symptoms, not the
wiring. The agent must speak operator-language, ask for observable symptoms, and give
step-by-step diagnostics, while **never** guessing at fixes that touch mains power,
rigging, or anything physically unsafe (those escalate — see `SOUL.md`).

## The bet (what this pilot tests)

Does a domain-scoped agent, grounded by RAG over a real document corpus, give
operators *useful, trustworthy, cited* troubleshooting help — enough to deflect
routine "ask the engineer" interruptions? This is also the first real exercise of:
deployment recipe → retrieval playbook → scoped persona/cartridge, end to end.

## Architecture (how it composes the platform)

```
operators ──(Discord)──► Hi-Orbit agent (Hermes, on a dedicated host)
                           ├── persona/identity   → SOUL.md (this folder)
                           ├── retrieval (cited)  → Cortex MCP (hybrid pgvector+BM25)
                           │     ingest: Drive corpus → markdown "brain" → Cortex
                           │     embeddings: local Ollama (nomic-embed-text)
                           │     corpus: puzzle design docs in Google Drive (rclone, read-only)
                           └── deployment recipe   → hermes-recipe/ (Hermes)
```

**See [`architecture.md`](architecture.md) for the full composed view** — the locked
decisions, container collection, the three read/write zones, the brain ingest pipeline,
and the retrieval-layer safety gating. The sketch above is the summary.

**Resolved scope (2026-06-04):**
- **Interface:** Discord, reusing the v0/Hermes stack.
- **Corpus:** puzzle design docs in **Google Drive**, read via an **rclone FUSE
  mount** (read-only) — the agent reads them as plain files.
- **Formats:** mixed — **PDF, Word, Markdown, and images/diagrams** (the last needs
  special handling; see `corpus-plan.md`).
- **Hosting:** a **new dedicated host** (likely on-site at the installation).
- **Persona:** scoped support identity (`SOUL.md`) — Tier 1/2 cartridge to start.
- **Citations:** every answer cites the source design doc/section.

## Corpus (the puzzle design documents)

The agent's knowledge is the design docs for each puzzle. They live in Google Drive
and are ingested for retrieval per [`corpus-plan.md`](corpus-plan.md). The notable
challenge is the **diagrams/schematics** — image content that text-RAG can't search
without a captioning/vision step. Still to confirm: per-puzzle vs master-doc
structure (→ chunking) and update cadence (→ re-index trigger).

## Scope

**In:** document-grounded troubleshooting Q&A for operators; citing sources;
escalation guidance.
**Out (v0.1):** controlling/actuating any hardware; modifying design docs; anything
safety-critical without a human; multi-installation/tenant.

## Success criteria (draft)

- Operators get a correct, cited answer for common puzzle faults without paging the
  engineer.
- The agent **declines or escalates** rather than guessing on uncovered or unsafe
  issues.
- Standing it up is reproducible from this folder + the shared recipes.

## Open questions (remaining)

1. **Diagram/image handling** — how to make schematics searchable (vision captioning
   at ingest vs. surface-as-asset). Main technical risk; see `corpus-plan.md`.
2. **Corpus structure** — one doc per puzzle vs. a master doc (→ chunking) and
   update cadence (→ re-index trigger).
3. **Escalation path** — how the agent hands off to the design engineer (channel
   ping? ticket?).
4. **Operator identities** — the Discord user/role IDs to restrict access to.

## Files

- [`architecture.md`](architecture.md) — the composed architecture: locked decisions,
  container collection, three read/write zones, brain ingest, retrieval safety gating.
- [`preflight.md`](preflight.md) — pilot-specific intake (resolved where decided).
- [`SOUL.md`](SOUL.md) — the support agent's persona/identity seed.
- [`corpus-plan.md`](corpus-plan.md) — design-doc ingestion plan (incl. diagrams).
- [`deployment-plan.md`](deployment-plan.md) — how this pilot is built, end to end.
- [`agent-access-recipe.md`](agent-access-recipe.md) — how to wire the agent's
  Discord, local repo/file workspace, and Google Drive (rclone) access, with a
  single-compose example (`single-compose/`) and openclaw vs. Hermes notes.
