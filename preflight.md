# Hi-Orbit Pilot — Preflight Intake

**Status:** v0.1 — partially filled (scoping in progress)
**Based on:** [`hermes-recipe/preflight-questionnaire.md`](hermes-recipe/preflight-questionnaire.md)

Pre-filled where known; `TBD` where scoping is needed. Secrets go in the runtime
`.env` / secrets store, **never** here.

## A. Host & deployment basics
- A1 Host / Docker: **TBD**
- A2 Code root: **TBD**
- A3 UID/GID: **TBD** (default 1000)
- A4 Version pin: default — pin known-good upstream

## B. Model backend (OpenRouter, direct)
- B1 Base URL: **`https://openrouter.ai/api/v1`** (direct; no proxy). ✅
- B2 OpenRouter API key: **TBD** (secret)
- B3 Default model: **TBD** — a capable OpenRouter model (troubleshooting needs good
  reasoning + faithful citation)
- B4 Embeddings provider (RAG): **TBD** — OpenRouter is chat-focused; may need a
  separate embeddings endpoint (confirm w/ rag-mcp)

## C. Interface (operators)
- **Channel: Discord** (reuse the v0/Hermes stack). ✅
- Audience: **game operators** (internal, non-engineers)
- User access: **restricted to operators** (not open) — `DISCORD_ALLOW_ALL_USERS=false`,
  collect operator user/role IDs → `DISCORD_ALLOWED_USERS` (**TBD** values)
- Bot token / server ID / channel IDs / home channel: **TBD** (collect per v0 intake)
- Mention behavior: default `require_mention: true`, `auto_thread: true`

## D. Document corpus (RAG) — the puzzle design docs
- Need retrieval: **yes** (core of the pilot)
- Location: **Google Drive**, read via **rclone FUSE mount (read-only)**. ✅
- Format: **mixed — PDF, Word (.docx), Markdown/text, and images/diagrams.** ✅
- Diagram handling: **decision needed** — captioning/vision at ingest vs.
  surface-as-asset. See [`corpus-plan.md`](corpus-plan.md).
- Structure: **TBD** — one doc per puzzle vs master doc → chunking
- Update cadence: **TBD** — re-index trigger when docs change
- Citation requirement: **yes** — answers cite the source doc/section
- rclone remote + mount path / Drive folder ID / auth (SA vs OAuth): **TBD**

## E. Escalation
- Path to the design engineer: **TBD** — channel ping / ticket.

## F. Hosting / runtime
- **New dedicated host** (likely on-site at the installation). ✅
- Host OS / Docker / UID-GID / code root: **TBD** (set during host setup)

---

## Decisions still needed before build
1. Diagram/image handling strategy (D) — see corpus-plan.md
2. Corpus structure + update cadence (D)
3. Escalation mechanism (E)
4. Concrete values: Discord token/IDs, host specifics, rclone/Drive config (secrets store)
