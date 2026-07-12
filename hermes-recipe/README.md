# Deployment v0 — Hermes Agent (HTF_Social) Reference

**Status:** v0 — first real deployment captured as agent instructions
**Provenance:** Derived from a manual server-to-server migration package
(`hermes-agent5-pkg`, "agent5" / Discord identity **HTF_Social**), the process
previously done by hand. This folder turns that manual hand-off into a
**repeatable, agent-executable instruction package**.
**Audience:** Internal (see [`../README.md`](../README.md) ground rules).

---

## What this is

The first concrete deployment **recipe** in the catalog (per
[`../roadmap.md`](../roadmap.md) Epic D1). Where
[`../recipes/reference-coding-agent.md`](../recipes/reference-coding-agent.md) is an
idealized seed, this is a **real, working deployment** reverse-engineered from a
package we actually moved between servers — so it captures the gotchas that only
show up in practice (the s6 init-hook chown trap, UID remap, mount nesting, a shared
Discord token).

- [`preflight-questionnaire.md`](preflight-questionnaire.md) — **the intake.** The
  answers (Discord, OpenRouter, Google Drive, host) to gather *before* deploying.
- [`deploy-hermes-agent.md`](deploy-hermes-agent.md) — **the instruction package.**
  An agent executes this, step by step, to stand up the bot on a new host.
- [`config-templates/`](config-templates/) — `.env.example` (consolidated intake),
  `config.yaml`, and two compose files: `docker-compose.yml` (the **minimal,
  known-good Hermes-only** v0 deployment) and `docker-compose.yaml.example` (a
  forward-looking **multi-service** template — agent + RAG + Drive mount +
  brain refresh, gated by compose `--profile`s; services we haven't built yet are
  marked `[BUILD: TBD]`). Placeholders only.

## Sanitization (read this)

The source package included live secrets and private state. **None of that is
reproduced here.** This folder contains only structure, config *shape*, and
instructions. Concretely, the following from the original are **deliberately
excluded** and must never be committed:

- `.env` real values (Discord bot token, OpenRouter key, channel IDs)
- `state.db` / `state.db-wal` / `kanban.db` (agent history — ~23 MB; the "more data
  than necessary")
- `memories/` (`MEMORY.md`, `USER.md`) and `sessions/` (private agent/user data)

At deploy time these come from the runtime secrets store and the agent's own fresh
state — not from this repo.

## What "v0" means here

Captured-as-is from one real deployment. It is intentionally specific to the Hermes
runtime. Generalizing across runtimes (NanoBot, OpenClaw) and lifting the shared
config into the recipe-manifest format is **v1** work, not v0. The goal of v0 is:
*an agent can reproduce this deployment from these instructions alone.*
