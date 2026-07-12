# Recipe (v0): Deploy Hermes Agent (HTF_Social) to a New Host

**Type:** deployment-recipe / agent-executable instruction package
**Status:** v0 (captured from a real manual migration)
**Owner:** —
**Last reviewed:** 2026-06-04
**Deploys:** A `hermes-agent` (NousResearch) Discord bot, dockerized, routing LLM
calls directly to OpenRouter (OpenAI-compatible).

> ⚠️ Verify upstream specifics against current `hermes-agent` docs (last checked via
> snapshot 2026-06-04: hermes-agent 0.15.1, commit `fa4ebaa8b`). Upstream changes
> the init hook, Dockerfile UID, and config surface on its own schedule.

---

## Manifest

```yaml
id: hermes-agent-htf-social
description: Dockerized hermes-agent Discord bot (identity HTF_Social) on OpenRouter.
runtime: hermes-agent (NousResearch)        # upstream: github.com/nousresearch/hermes-agent
target_tier: 1-2                            # markdown SOUL.md + MEMORY.md memory (not yet a cartridge)
components:
  - docker + compose
  - discord bot application (token)
  - openrouter account (direct, OpenAI-compatible model API)
  - (optional) rclone google drive mount    # cf. ../playbooks/google-drive.md
  - (optional) projects corpus bind-mount
default_config:
  model_default: "<OPENROUTER_MODEL_ID>"
  discord_require_mention: true
  discord_auto_thread: true
  hermes_uid_gid: 1000                       # match the host user that owns the data
secrets:                                     # placeholders; live in runtime .env / secrets store, NOT this repo
  - <DISCORD_BOT_TOKEN>
  - <OPENROUTER_API_KEY>                       # OPENAI_API_KEY for the custom provider
  - <DISCORD_HOME_CHANNEL_ID>
```

---

## Instruction Package (agent-executable)

**Role:** You are deploying `hermes-agent-htf-social` to a fresh host. Execute the
steps in order. **Stop and request human approval before any step that handles real
credentials or is irreversible** (marked *Human gate: yes*). Each step ends in a
verification — do not proceed until it passes. Use placeholders for all secrets;
read real values from the runtime secrets store the operator provides, never from
this repo.

### Step 1 — Prerequisites
- **Complete [`preflight-questionnaire.md`](preflight-questionnaire.md) first** —
  all ✅ Required answers must be in hand before proceeding.
- Docker Engine 24+ with the Compose plugin (`docker compose version`).
- Git; ~5 GB free disk (image ~3.5 GB + state).
- Note the host user's UID/GID: `id -u; id -g`. The config assumes **1000**.
- *Verify:* `docker compose version` succeeds and you have recorded UID/GID.
- *Human gate:* no

### Step 2 — Clone the runtime
```bash
cd <CODE_ROOT>
git clone https://github.com/nousresearch/hermes-agent hermes-agent
cd hermes-agent && git checkout fa4ebaa8b   # known-good pin; or omit for latest
```
- *Verify:* `hermes-agent/` exists with the upstream `docker-compose.yml`.
- *Human gate:* no

### Step 3 — Establish the directory layout
The compose file uses **relative** bind-mount paths; preserve this exact layout:
```
<CODE_ROOT>/
├── hermes-agent/                  ← cloned upstream (this is where you run compose)
├── bot_memory/agent5/
│   ├── stage2-hook.sh             ← patched init hook (Step 5 — CRITICAL)
│   └── .hermes/                   ← HERMES_HOME (config.yaml, .env, workspace, state)
├── projects/                      ← bind-mounted at /opt/projects
└── shared/gdrive_kst/             ← optional rclone mount at /opt/gdrive_kst
```
```bash
cd <CODE_ROOT>
mkdir -p bot_memory/agent5/.hermes projects shared/gdrive_kst
```
- *Verify:* the tree above exists.
- *Human gate:* no

### Step 4 — Install the patched compose file
Copy [`config-templates/docker-compose.yml`](config-templates/docker-compose.yml)
over the upstream one, then set the UID/GID if not 1000.
```bash
cp <THIS_DIR>/config-templates/docker-compose.yml hermes-agent/docker-compose.yml
```
This compose differs from upstream in five ways (all intentional):
- Both `gateway` **and** `dashboard` bind-mount the patched `stage2-hook.sh`.
- Data volume → `../bot_memory/agent5/.hermes` (not `~/.hermes`).
- `../projects` mounted at `/opt/projects` (top-level, not nested under data).
- `../shared/gdrive_kst` mounted at `/opt/gdrive_kst` with `rslave` propagation.
- `HERMES_UID`/`HERMES_GID` default to **1000** (upstream uses 10000).
- *Verify:* the two `stage2-hook.sh:/opt/hermes/docker/stage2-hook.sh:ro` lines are
  present in both services.
- *Human gate:* no

### Step 5 — Apply the CRITICAL init-hook patch
**This is the single most important step. Skipping it causes multi-hour boots and
700+ MB of layer bloat per restart.** Upstream's `docker/stage2-hook.sh` re-runs a
recursive `chown -R` over `.venv` / `ui-tui` / `node_modules` on **every** boot when
`HERMES_UID != 10000`; on overlayfs that copies up tens of thousands of files.

Create `bot_memory/agent5/stage2-hook.sh` as a copy of the upstream
`hermes-agent/docker/stage2-hook.sh`, then **wrap the install-tree chown block in a
heredoc comment** so it is skipped:
```sh
echo "[stage2] (agent5 patch) skipping install-tree chown of .venv/ui-tui/node_modules"
: <<'AGENT5_SKIP'
    chown -R hermes:hermes \
        "$INSTALL_DIR/.venv" \
        "$INSTALL_DIR/ui-tui" \
        "$INSTALL_DIR/node_modules"
AGENT5_SKIP
```
Leave the rest of the hook intact (UID remap, `/opt/data` chown, config seeding,
skills sync). It is safe to skip because the Dockerfile already runs
`chmod -R a+rX /opt/hermes` at build time and `discord.py` is pre-installed.
```bash
chmod +x bot_memory/agent5/stage2-hook.sh
```
- *Verify:* `grep AGENT5_SKIP bot_memory/agent5/stage2-hook.sh` matches, and the
  file is executable.
- *Human gate:* no
- *Note:* on `git pull` + rebuild of upstream, re-check `docker/stage2-hook.sh` for
  changes and re-apply this wrap if the block moved. (A cleaner permanent fix: bake
  `useradd -u 1000` into the Dockerfile and drop the remap entirely.)

### Step 6 — Seed config (placeholders, then real secrets)
Collect answers using [`preflight-questionnaire.md`](preflight-questionnaire.md) and
fill [`config-templates/.env.example`](config-templates/.env.example) into a real,
**uncommitted** `.env`. Values are tagged by scope — distribute them:
- `[runtime]` → `bot_memory/agent5/.hermes/.env`
- `[compose]` → `hermes-agent/.env` (docker compose substitution)
- `[config]` → copy into `config.yaml` (model base_url/default, allowed_channels)
- `[rclone]` → rclone config / env (Step 7)

```bash
cp <THIS_DIR>/config-templates/config.yaml      bot_memory/agent5/.hermes/config.yaml
cp <FILLED_ENV>                                  bot_memory/agent5/.hermes/.env   # [runtime] keys
```
Confirm the `bot_memory/agent5/.hermes/.env` `[runtime]` values:
- `DISCORD_BOT_TOKEN` = `<DISCORD_BOT_TOKEN>` for **this** bot. ⚠️ Do not reuse a
  token already held by another running bot — a Discord token allows only one active
  gateway session. Create a fresh application at developer.discord.com if needed.
- `OPENAI_API_KEY` = `<OPENROUTER_API_KEY>` (your OpenRouter key).
- `DISCORD_HOME_CHANNEL` / `DISCORD_HOME_CHANNEL_THREAD_ID` = `<DISCORD_HOME_CHANNEL_ID>`.
- Review `DISCORD_ALLOW_ALL_USERS` — `true` lets **anyone** in the allowed channels
  (or via DM) drive the agent. Prefer `DISCORD_ALLOWED_USERS=<id1,id2>` to restrict.

And in `config.yaml` set `model.base_url` to `https://openrouter.ai/api/v1`,
`model.default` to an OpenRouter model id, and confirm `discord.allowed_channels`
are channels this bot can access.
- *Verify:* `.env` has no placeholder `<...>` left; OpenRouter is reachable from the
  host with the key (`curl -s https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`).
- *Human gate:* **yes** — handling the Discord token and OpenRouter key, and setting
  the user-access policy.

### Step 7 — (Optional) External mounts
- **projects corpus:** rsync from source or start empty (`mkdir -p projects`).
- **Google Drive:** configure an rclone remote and mount at
  `shared/gdrive_kst` (`rclone mount <remote>: shared/gdrive_kst --vfs-cache-mode=writes --daemon`).
  See [`../playbooks/google-drive.md`](../playbooks/google-drive.md). If unused, the
  symlink dangles harmlessly inside the container.
- *Verify:* if mounted, `ls shared/gdrive_kst` lists Drive contents.
- *Human gate:* yes (grants Drive access)

### Step 8 — Fix ownership, build, start
```bash
chown -R $(id -u):$(id -g) bot_memory/agent5/
cd <CODE_ROOT>/hermes-agent
docker compose build           # first build is slow (~25-45 min); cached after
docker compose up -d
docker compose logs -f gateway
```
- *Verify:* logs show `[stage2] (agent5 patch) skipping install-tree chown ...`,
  `[Discord] Connected as HTF_Social#...`, and `Gateway running with 1 platform(s)`.
  The dashboard is at `http://127.0.0.1:9119` (localhost-only; SSH-tunnel for remote).
- *Human gate:* no

---

## End-to-end verification
In an allowed Discord channel, @mention the bot with a simple request. It reacts
(👀/✅), opens a thread, and responds via OpenRouter. Confirm it does **not**
respond when not mentioned (require_mention) and does **not** respond outside
`allowed_channels`.

## Teardown
```bash
cd <CODE_ROOT>/hermes-agent && docker compose down
```
- Revoke/rotate the Discord token and OpenRouter key if the deployment is ending.
- Unmount rclone; remove `shared/gdrive_kst`.
- Handle `bot_memory/agent5/.hermes/` deliberately — it holds the agent's memory and
  state; archive or delete per data policy, don't silently drop.

## Troubleshooting (the ones that actually bite)
| Symptom | Cause | Fix |
|---|---|---|
| Init hangs for hours / gateway never connects | stage2-hook patch not active | Confirm Step 5; check both compose bind-mounts; `down && up -d` |
| Bot online but no `discord connected` | bad token, OpenRouter unreachable/bad key, or channel access | Check `.hermes/logs/gateway.log`; verify token, `base_url`, OpenRouter key, channel IDs |
| Files owned by 1000 but host user differs | UID mismatch | Set `HERMES_UID/GID` in compose to `id -u`/`id -g`; `down && up -d` |
| Two bots fight over one token | shared Discord token | Give each bot its own application/token |

## Deployment record
After a successful deploy, record (in the agent's own memory or a deployment log):
recipe `id`, upstream commit/pin, host, UID/GID, and which optional mounts were
enabled — **without secrets** — so the deployment is traceable and reproducible.
