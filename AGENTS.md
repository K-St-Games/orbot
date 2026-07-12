# Hi-Orbit Deployment — Agent Entry Point

**You are a deployment/build agent.** Your job is to stand up the Hi-Orbit
operator tech-support agent on a fresh host: a Discord-facing **Hermes** agent,
grounded by **Cortex** retrieval over a Google Drive corpus, with **local Ollama**
embeddings. This is operations work — standing up containers, wiring config,
collecting secrets — **not** research or design.

> **Mode for this phase: "get it running."** Deploy Cortex as-is from
> [`cortex/`](cortex/). The pilot-hardening items (especially the `min_relevance`
> safety threshold) are tracked in [`cortex-hardening.md`](cortex-hardening.md) and
> applied in a **later** pass — do not block first light on them. Flag them, don't
> fix them yet, unless the human says otherwise.

---

## Start here (reading order)

1. [`architecture.md`](architecture.md) — **the** composed picture: locked decisions,
   the container collection, the three read/write zones, the ingest pipeline. Read it
   first and in full.
2. [`deployment-plan.md`](deployment-plan.md) — the ordered build (host → Hermes →
   corpus → brain → Ollama → Cortex → wire). This is your checklist.
3. [`BUILD-KIT.md`](BUILD-KIT.md) — what's in this folder, what's vendored, and the
   **human-gated decisions you must collect before you can finish**.
4. [`SOUL.md`](SOUL.md) — the agent's persona + the hard safety rules it must obey.

## What each piece is

| Path | Role in the build |
|---|---|
| [`architecture.md`](architecture.md) | Source of truth for the design. |
| [`deployment-plan.md`](deployment-plan.md) | Step-by-step build order with verify gates. |
| [`agent-access-recipe.md`](agent-access-recipe.md) | How Discord + workspace + rclone Drive access wire up (distilled from a live host). Includes an openclaw↔Hermes mapping — **use the Hermes side.** |
| [`single-compose/`](single-compose/) | A runnable rclone+agent compose example to adapt. Note: it's openclaw-shaped; for Hermes follow §9 of the access recipe. |
| [`hermes-recipe/`](hermes-recipe/) | The Hermes deployment recipe + preflight + config templates (vendored from the parent platform's v0). |
| [`playbooks/`](playbooks/) | Components: `google-drive.md` (rclone), `rag-setup.md` (retrieval), `gdrive-markdown-brain.md` (the ingest "brain"). |
| [`cortex/`](cortex/) | The retrieval engine **code** — postgres + indexer + rag-server compose. This is what you deploy for retrieval. |
| [`cortex-hardening.md`](cortex-hardening.md) | Known Cortex gaps + fixes. **Later pass**, except where noted. |
| [`corpus-plan.md`](corpus-plan.md) / [`preflight.md`](preflight.md) | Ingestion plan; per-host intake (fill the `TBD`s with the human). |

## Ground rules

- **Secrets never go in this repo.** Discord tokens, the rclone OAuth token, model/API
  keys — all live in `.env` / a secrets store on the host, referenced by location only.
  If you find a real key committed anywhere, stop and flag it (see `cortex-hardening.md`
  #8).
- **Read-only corpus by construction.** The Drive mount is `drive.readonly` + a
  read-only bind. Don't give the agent write access to the design docs.
- **Don't publish management surfaces** (rclone WebGUI, Hermes dashboard, gateway) on a
  venue network. localhost / Tailscale only.
- **Verify each step** against the `*Verify:*` gate in `deployment-plan.md` before moving
  on. A `*Human gate: yes*` step needs the human to supply something (a secret, an
  approval) — ask, don't guess.
- **When a decision is ambiguous, ask.** The open decisions are listed in `BUILD-KIT.md`
  §"Decisions to collect" — surface them early rather than inventing answers.

## Out of scope (don't go here)

This deployment was extracted from a larger platform repo. Anything about **cartridges,
memory reflection, the runtime experiment, or engine forks** is *not* part of standing
up Hi-Orbit. If a vendored doc references those, ignore them. Your world is this folder.
