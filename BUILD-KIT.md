# Hi-Orbit Build Kit — Manifest & Standalone Notes

**What this is:** this folder is a **self-contained** deployment kit. It carries
everything needed to stand up the Hi-Orbit agent, so it can be copied into a fresh
environment (or split into its own git repo) and built without the parent platform repo.

**Entry point:** [`AGENTS.md`](AGENTS.md). **Design:** [`architecture.md`](architecture.md).
**Build order:** [`deployment-plan.md`](deployment-plan.md).

---

## 1. Contents

### Authored for this pilot
| Path | Purpose |
|---|---|
| `AGENTS.md` | Build-agent entry point + ground rules. |
| `architecture.md` | The composed architecture (source of truth). |
| `deployment-plan.md` | Ordered build with verify gates. |
| `corpus-plan.md` | Corpus ingestion plan (formats, diagrams, citations). |
| `preflight.md` | Per-host intake (fill the `TBD`s). |
| `SOUL.md` | Agent persona + safety rules. |
| `agent-access-recipe.md` | Discord + workspace + rclone wiring (Hermes & openclaw). |
| `single-compose/` | Runnable rclone+agent compose example. |
| `BUILD-KIT.md` | This file. |

### Vendored from the parent platform repo (snapshots — see §3)
| Path | Vendored from | Purpose |
|---|---|---|
| `hermes-recipe/` | `deployment/v0/` | Hermes deploy recipe, preflight, config templates. |
| `playbooks/` | `deployment/playbooks/` | rclone Drive, RAG setup, the markdown-brain ingest. |
| `cortex/` | `reference/cortex/` | **The retrieval engine code** (postgres + indexer + rag-server). |
| `cortex-hardening.md` | `mcp_enhancement_suggestions.md` | Known Cortex gaps + fixes (later pass). |

## 2. The container collection (what you'll run)

Two compose projects on one shared docker network (`hi-orbit-net`):

**Durable shared infra** (engine-agnostic):
- `rclone-gdrive` — privileged FUSE mount of the read-only Drive corpus.
- `ollama` — local embeddings (`nomic-embed-text`, 768-dim). **Added for this pilot;**
  not in the vendored Cortex compose — wire it in and point Cortex's `OLLAMA_URL` at it.
- `cortex-postgres` / `cortex-indexer` / `cortex-rag-server` — from [`cortex/`](cortex/).
- `brain-builder` — the convert+caption ingest job (the main net-new code; see §"Decisions").

**Swappable agent** (Hermes-specific):
- `hermes-agent` (+ `hermes-dashboard`) — from [`hermes-recipe/`](hermes-recipe/).

See [`architecture.md`](architecture.md) §2 for the topology and §6 for the Ollama wiring.

## 3. Standalone caveats (read before relying on vendored docs)

- **Vendored = point-in-time snapshots.** `hermes-recipe/`, `playbooks/`, `cortex/`, and
  `cortex-hardening.md` were copied from the parent repo on **2026-06-25**. Once this kit
  becomes its own repo, **this kit is the source of truth** — changes here do not flow
  back to the parent automatically, and vice-versa.
- **A few internal links in the vendored docs** still reference the parent repo's layout
  (e.g. `hermes-recipe/README.md` mentions a `../roadmap.md` / `../recipes/` that aren't
  in this kit). The primary build-path docs (`AGENTS`, `architecture`, `deployment-plan`,
  `corpus-plan`, `preflight`, the playbooks) have been repointed to local paths. If a
  vendored link 404s, it's pointing at the old platform — ignore it.
- **`cortex/` ≠ a finished service for this corpus.** As shipped it indexes markdown +
  YAML frontmatter (Obsidian-style) and embeds via Ollama/LM Studio/LiteLLM. For Hi-Orbit
  you still need the `brain-builder` (multi-format → markdown) in front of it. "Get it
  running" means: stand up Cortex against the **brain**, not the raw mixed corpus.
- **`agent-access-recipe.md` references live host paths** (`/home/damien/...`). Those are
  documentation of the source deployment, not files to copy — ignore for a fresh host.

## 4. Decisions to collect from the human (before the build can finish)

These are the `*Human gate: yes*` / open items from `architecture.md` §9 and `preflight.md`.
Status as of 2026-06-25:

1. **Host sizing** — *still open.* Design spec stands as written (single
   dedicated host runs Ollama + Hermes + Postgres). May land on an existing
   on-prem server instead of a new box — if so, avoid a "spiderweb of
   microservices" where one container breaking takes the bot down with it
   (keep the durable-infra/swappable-agent split from `architecture.md` §2
   strict for this reason).
2. **Discord operator access** — *resolved (changed from the original plan).*
   No `DISCORD_ALLOWED_USERS` allowlist. Instead `DISCORD_ALLOW_ALL_USERS=true`
   — rely on Discord's own bot-install/invite flow as the access boundary.
   Reflected in `single-compose/bot_memory/hi-orbit/.hermes/.env.example`.
3. **Escalation mechanism** — *resolved.* Channel ping with an `@`-mention,
   not a ticket system. Still needs: which channel/role gets pinged, and
   whether the agent posts the handoff summary itself or just alerts.
4. **Google Drive** — *still open.* rclone OAuth token, Shared Drive ID,
   `drive.readonly` scope all TBD — collect per `playbooks/google-drive.md`.
5. **Model routing** — *in progress.* Direct OpenRouter (no LiteLLM proxy) per
   `single-compose/bot_memory/hi-orbit/.hermes/config.yaml`'s `provider:
   openrouter`. Model id + API key still need filling in.
6. **Brain-builder: build vs buy** — *deferred.* Don't decide yet; revisit once
   primary connectivity (Discord + Hermes online) is working and the actual
   corpus files have been seen — the real documents may change the approach
   (e.g. converting legacy docs into Obsidian-style markdown and pointing
   operators at that directly, rather than a captioning pipeline).
7. **Corpus structure / re-index trigger** — *deferred for the same reason as
   #6* — needs the actual files in hand first.
8. **Discord tool surface — accepted risk (2026-06-25).** `platform_toolsets.
   discord` in `config.yaml` includes both `file` and `terminal`. Note: any
   comments explaining this written directly into `config.yaml` get stripped
   — Hermes rewrites that file wholesale to its normalized schema on boot
   (`_config_version` migration), so the rationale lives here instead:
   - `file` (read_file/write_file/patch/search_files): needed so the agent
     can read `/opt/gdrive_hiorbit` directly. write_file/patch are bundled in
     (no read-only-only toolset exists upstream) but are neutralized for the
     corpus specifically — `/opt/gdrive_hiorbit`'s bind mount in
     `docker-compose.yml` is `read_only: true`, enforced at the OS level
     (verified: write attempts fail with "Read-only file system" regardless
     of what the toolset permits).
   - `terminal` (full shell as the `hermes` OS user): granted as a **known,
     accepted risk**, not a default. Upstream's own docs say the terminal
     tool bypasses `read_file`'s credential denylist entirely — concretely,
     `cat /opt/data/.env` or `env` exposes `DISCORD_BOT_TOKEN`,
     `OPENROUTER_API_KEY`, and `API_SERVER_KEY`. Combined with
     `DISCORD_ALLOW_ALL_USERS=true` (decision #2 above), **any Discord user
     who can message this bot can attempt that exfiltration today.** If this
     risk profile ever needs to tighten, the lever is `DISCORD_ALLOW_ALL_USERS`
     /`DISCORD_ALLOWED_USERS` in the Hermes runtime `.env`, not the toolset.

## 5. Single-compose scaffold — what's actually built vs. still manual

`single-compose/` (see `agent-access-recipe.md` §8) is no longer an
illustrative openclaw template — it's a real, Hermes-native scaffold:
`hermes-agent/` is upstream `nousresearch/hermes-agent` cloned and pinned at
`fa4ebaa8b`; `docker-compose.yml` runs `rclone-gdrive` + Hermes `gateway` +
`dashboard` as one project; the critical stage2-hook chown patch is applied;
`bot_memory/hi-orbit/.hermes/` holds `config.yaml` + `SOUL.md` + an
`.env.example` for runtime secrets (kept separate from the compose-scope
`.env`). The Hermes image build was verified in this dev sandbox.

**Not yet done / can't be done here:**
- This dev sandbox has **no `/dev/fuse`** — `rclone-gdrive` cannot run here.
  The Drive-mount half of the stack can only be verified on the real target
  host (preflight.md A1).
- No real secrets filled in (Discord token, OpenRouter key, rclone OAuth,
  Drive folder/Shared-Drive ID, operator channel IDs) — `.env`/`config.yaml`
  placeholders are ready for them.
- Cortex/Ollama (RAG retrieval) are explicitly **not** wired into this compose
  yet — `AGENTS.md` scopes "get it running" to Hermes + rclone first; Cortex
  is a later pass once the bot is online (and note: Cortex's compose uses a
  bridge network + service-name DNS, while Hermes uses `network_mode: host` —
  reconciling that is part of the later pass, not solved here).

---

## 6. Promoting this folder to its own repo

You want git history as you evolve the deployment. Two ways:

### Option A — clean start (simplest; no history)

```bash
# from a copy of this folder, outside the parent repo
cp -r deployment/pilots/hi-orbit ~/hi-orbit-deploy
cd ~/hi-orbit-deploy
rm -rf cortex/.git 2>/dev/null    # ensure no nested git dirs came along
git init -b main
git add .
git commit -m "Initial Hi-Orbit deployment kit (vendored 2026-06-25)"
# then create the remote and push:
#   gh repo create <org>/hi-orbit-deploy --private --source=. --push
```

Use this if you don't care about preserving the parent repo's commit history for these
files. It's the cleanest result — a fresh repo whose first commit is the whole kit.

### Option B — preserve history with `git subtree split`

```bash
# from the parent htf_coder repo
git subtree split --prefix=deployment/pilots/hi-orbit -b hi-orbit-export
# create the new repo from that branch:
mkdir ~/hi-orbit-deploy && cd ~/hi-orbit-deploy
git init -b main
git pull /path/to/htf_coder hi-orbit-export
#   gh repo create <org>/hi-orbit-deploy --private --source=. --push
```

This keeps the commits that touched these paths. Caveat: the vendored files
(`cortex/`, `playbooks/`, `hermes-recipe/`) only carry history from when they were
**copied in** (this commit), not their original history under `reference/`/`v0/` — that
history stays in the parent repo. Good enough for tracking the deployment going forward.

### After the split — first things to do in the new repo

- Add a `.gitignore` for runtime artifacts and secrets: `**/.env`, `**/rclone.conf`,
  `**/*.key`, `shared/`, `*/data/`, `*/logs/`, model volumes. (`cortex/.gitignore` is a
  starting point.)
- Replace `AGENTS.md`'s "extracted from a larger platform" note if you want — it's
  already scoped to just the deployment.
- Decide whether `cortex/`, `playbooks/`, `hermes-recipe/` should later become **git
  submodules** pointing back at upstream sources instead of vendored copies. For now,
  vendored is simpler and matches "self-contained"; revisit if you find yourself syncing
  fixes by hand in two places.

### Sub-repo alternative

If you'd rather keep it *inside* `htf_coder` but independently versioned, make it a
**submodule**: create the standalone repo (Option A/B), then in the parent
`git rm -r deployment/pilots/hi-orbit && git submodule add <url> deployment/pilots/hi-orbit`.
The parent then pins a commit of the deployment repo. More moving parts; only worth it if
you want the parent to keep referencing a specific deployment version.
