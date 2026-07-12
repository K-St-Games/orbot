# Recipe: agent access setup (Discord + local repo/file editing + Google Drive)

**What this is:** a reference recipe distilled from the running **openclaw** bot
(`agent2` on this host), covering the three capabilities Hi-Orbit needs to
replicate: a **Discord** interface, a **local file-editing / git-repo**
workspace, and a **read-mostly Google Drive corpus via an rclone FUSE mount**.

It documents *how each piece is wired* and *every credential / config value*
required to stand it up. Live secret values are **not** reproduced here — each is
named with the file it lives in on the host. Never commit real tokens.

> Source of truth on the host:
> - openclaw repo + compose: [`/home/damien/code/openclaw/`](/home/damien/code/openclaw/)
> - openclaw runtime config/state: `/home/damien/code/bot_memory/agent2/.openclaw/`
> - rclone mount service: [`/home/damien/code/rclone/`](/home/damien/code/rclone/)

---

## 1. Topology at a glance

```
                          ┌─────────────────────────────────────────┐
 Discord  ──(outbound)──► │  openclaw-gateway (container)            │
 operators               │   node dist/index.js gateway --bind lan  │
                          │   ports 18789 (gateway) 18790 (bridge)   │
                          │                                          │
                          │   workspace = /home/node/.openclaw/      │
                          │              workspace                   │
                          │     ├── projects   ◄── bind ../projects  │  ← git repos, file editing
                          │     ├── bot_memory ◄── bind ../bot_memory│
                          │     └── gdrive_kst ─► symlink to          │
                          │                       /home/node/gdrive_kst│
                          └───────────────┬──────────────────────────┘
                                          │ bind (rslave)
                                          ▼
                          /home/damien/code/shared/gdrive_kst   ← FUSE mount point
                                          ▲
                          ┌───────────────┴──────────────────────────┐
                          │  rclone-gdrive-kst (separate container)   │
                          │   rclone mount "gdrive_kst:" ...          │
                          │   reads OAuth token from rclone.conf      │
                          └────────────────────► Google Drive (Shared Drive)
```

Two **independent** containers:

1. **`rclone-gdrive-kst`** owns the FUSE mount and the Google OAuth token. It
   writes the cloud files onto a host path (`shared/gdrive_kst`).
2. **`openclaw-gateway`** bind-mounts that host path in (plus the local repos)
   and runs the agent + Discord channel.

Decoupling them matters: the rclone container is privileged (needs `/dev/fuse`);
openclaw is not. The mount survives openclaw restarts, and vice-versa.

---

## 2. Discord access

openclaw talks to Discord as an **outbound bot connection** (gateway websocket) —
no inbound port is needed for Discord itself. Configuration lives in the agent's
`openclaw.json`, not in env vars.

### Wiring (`bot_memory/agent2/.openclaw/openclaw.json`)

```jsonc
"plugins": {
  "allow": ["discord", "canvas", "device-pair"],
  "entries": { "discord": { "enabled": true } }
},
"channels": {
  "discord": {
    "enabled": true,
    "token": "<DISCORD_BOT_TOKEN>",      // the bot's secret token
    "groupPolicy": "open",               // responds in allowed guild channels
    "streaming": { "mode": "off" },
    "guilds": {
      "<GUILD_ID>": {                    // per-server allowlist
        "channels": {
          "<CHANNEL_ID>": { "enabled": true }   // or "*": {"enabled": true}
        }
      }
    }
  }
}
```

### Sender allowlist

`bot_memory/agent2/.openclaw/credentials/discord-allowFrom.json` restricts *who*
the bot will act on (Discord user IDs and/or role/guild IDs):

```json
{ "version": 1, "allowFrom": ["<USER_OR_ROLE_ID>", "..."] }
```

This is exactly the lever Hi-Orbit needs for **open question #4 (operator
identities)** — drop the operators' Discord user IDs (or an operator role ID)
in here.

### Credentials & IDs required for Discord

| Item | Where it lives | How to get it |
|------|----------------|---------------|
| **Bot token** | `openclaw.json → channels.discord.token` | Discord Developer Portal → your App → **Bot** → Reset/Copy Token |
| **Guild (server) ID** | `openclaw.json → channels.discord.guilds` | Discord client with Developer Mode on → right-click server → Copy ID |
| **Channel ID(s)** | `...guilds.<id>.channels` | right-click channel → Copy ID (or use `"*"` for all channels in the guild) |
| **Allowed sender IDs** | `credentials/discord-allowFrom.json` | right-click user/role → Copy ID |

### Discord Developer Portal setup (one-time, per bot)

1. Create an Application → add a **Bot**.
2. Enable the **Message Content Intent** (required to read message text), plus
   Server Members / Presence intents only if needed.
3. Invite the bot to the server via OAuth2 URL with `bot` scope and at least
   *Read Messages*, *Send Messages*, *Read Message History* permissions.
4. Copy the bot token into `openclaw.json`.

State openclaw persists for Discord (auto-created, no manual setup):
`.openclaw/discord/` (`thread-bindings.json`, `command-deploy-cache.json`) and
`credentials/discord-pairing.json`.

---

## 3. Local file-editing / git-repo environment

The agent's working tree is `/home/node/.openclaw/workspace` **inside** the
container. Host directories are bind-mounted into it so the agent edits *real*
files and can run `git` against *real* repos. Edits the agent makes appear on the
host immediately, and vice-versa.

### Wiring (`openclaw/docker-compose.yml`, gateway service)

```yaml
volumes:
  # config + state (the whole .openclaw dir)
  - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
  - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
  # the editable repos / corpora:
  - ../projects:/home/node/.openclaw/workspace/projects
  - ../bot_memory/:/home/node/.openclaw/workspace/bot_memory
  - ../nanobot:/home/node/.openclaw/workspace/nanobot
environment:
  HOME: /home/node
  OPENCLAW_HOME: /home/node
  # Container-side paths are PINNED so host paths from .env can't leak in:
  OPENCLAW_STATE_DIR:      /home/node/.openclaw
  OPENCLAW_CONFIG_PATH:    /home/node/.openclaw/openclaw.json
  OPENCLAW_CONFIG_DIR:     /home/node/.openclaw
  OPENCLAW_WORKSPACE_DIR:  /home/node/.openclaw/workspace
```

The **host** side of those binds is set in `openclaw/.env`:

```ini
OPENCLAW_CONFIG_DIR=/home/damien/code/bot_memory/agent2/.openclaw
OPENCLAW_WORKSPACE_DIR=/home/damien/code/bot_memory/agent2/.openclaw/workspace
```

### Critical details that make file editing actually work

- **UID alignment.** The container runs as `node` = **uid/gid 1000**, matching
  the host user. This is *the* thing that keeps `git push`, cross-agent edits,
  and host edits from fighting over file ownership. Every bot in this fleet is
  standardized on uid 1000 for the shared `../projects` mount — replicate that.
- **`docker.sock` mount** (`/var/run/docker.sock`) + `group_add: ${DOCKER_GID}`
  lets the agent shell out to sibling containers via `docker exec`. Optional —
  include only if the Hi-Orbit agent needs to drive other containers.
  `DOCKER_GID` must equal `stat -c '%g' /var/run/docker.sock` on the host.
- **Hardening:** `cap_drop: [NET_RAW, NET_ADMIN]`, `no-new-privileges:true`.
- **git identity / auth:** the agent runs `git` as the `node` user inside the
  container. For pushes it needs credentials in the workspace — a `.gitconfig`
  and a token/SSH key reachable from `$HOME` (`/home/node`). Provide these via
  the mounted `.openclaw` (which *is* `$HOME`) if the agent must push.

### Config required for the workspace

| Item | Where | Notes |
|------|-------|-------|
| Host repo path(s) | `docker-compose.yml` volumes + `.env` | bind each repo/corpus you want editable |
| `OPENCLAW_CONFIG_DIR` / `OPENCLAW_WORKSPACE_DIR` | `openclaw/.env` | host source of the state + workspace binds |
| Run as uid/gid **1000** | image default (`node` user) | keep file ownership uniform with host |
| `DOCKER_GID` | `openclaw/.env` (only if mounting docker.sock) | host docker group gid |
| git credentials | inside `$HOME` = mounted `.openclaw` | only if agent pushes |

---

## 4. Google Drive via rclone FUSE mount

The corpus is exposed to the agent as **plain files on disk**. A dedicated rclone
container mounts a Google **Shared Drive** to a host path; openclaw bind-mounts
that path in. This is exactly the Hi-Orbit corpus model (read design docs as
files; PDFs/Word/MD/images).

### 4a. The rclone mount service (`/home/damien/code/rclone/`)

`docker-compose.yml` (key parts):

```yaml
services:
  rclone-gdrive-kst:
    image: rclone/rclone:latest
    restart: unless-stopped
    privileged: true                 # FUSE needs this
    devices: [/dev/fuse]
    cap_add: [SYS_ADMIN]
    security_opt: [apparmor:unconfined]
    environment: [PUID=1000, PGID=1000, TZ=America/Los_Angeles]
    ports: ["${RCLONE_KST_GUI_PORT:-5575}:5572"]   # WebGUI on host :5575
    volumes:
      - ./data/rclone_config:/config/rclone        # holds rclone.conf (the OAuth token!)
      - ./logs:/logs
      - ../shared/gdrive_kst:/shared/gdrive_kst:shared   # the mount point, shared propagation
    command: >
      mount "gdrive_kst:" /shared/gdrive_kst
      --config /config/rclone/rclone.conf
      --uid 1000 --gid 1000 --umask 002 --allow-other --allow-non-empty
      --vfs-cache-mode full --vfs-cache-max-size 10G --vfs-cache-max-age 24h
      --dir-cache-time 1000h --poll-interval 15s
      --rc --rc-web-gui --rc-addr :5572
      --rc-user ${RCLONE_USER:-admin} --rc-pass ${RCLONE_PASSWORD:-admin}
      --log-file /logs/rclone-gdrive-kst.log --log-level INFO
    healthcheck:
      test: ["CMD", "mountpoint", "-q", "/shared/gdrive_kst"]
```

Key choices to copy:
- **`--uid 1000 --gid 1000 --umask 002 --allow-other`** so the openclaw
  container (uid 1000) can read the files.
- **`vfs-cache-mode full`** + a cache size cap — gives sane performance and
  lets large PDFs/images stream.
- **`:shared` mount propagation** on the host path so the FUSE mount is visible
  to the other container that binds it.
- For a **read-only** corpus, set the remote's `scope = drive.readonly` (see
  `gdrive2`/`gdrive_shared` remotes for the read-only pattern). `gdrive_kst`
  currently uses full `scope = drive` (read-write).

### 4b. The rclone remote definition (`rclone/data/rclone_config/rclone.conf`)

```ini
[gdrive_kst]
type = drive
scope = drive                 # use drive.readonly for a read-only corpus
team_drive = 0AO...           # the Shared Drive ID
root_folder_id =              # optional: pin to a subfolder
token = {"access_token":...}  # OAuth token — SECRET, do not commit
```

### 4c. Credentials & config required for Google Drive

| Item | Where it lives | How to get it |
|------|----------------|---------------|
| **Google OAuth token** | `rclone.conf → [remote].token` | `rclone config` OAuth flow (or the WebGUI). Easiest: run `rclone authorize "drive"` on a machine with a browser, paste the token back. |
| **(optional) OAuth client_id/secret** | `rclone.conf` | Google Cloud Console → OAuth credentials. Recommended for prod to avoid rclone's shared, rate-limited default client. |
| **Shared Drive ID** (`team_drive`) | `rclone.conf → team_drive` | `rclone backend drives gdrive_kst:` or Drive URL |
| **Scope** | `rclone.conf → scope` | `drive.readonly` for read-only corpus; `drive` for read-write |
| **WebGUI user/pass** | `rclone/.env` (`RCLONE_USER`/`RCLONE_PASSWORD`) | defaults `admin/admin` — **change for any non-Tailscale host** |
| **GUI port** | `rclone/.env` (`RCLONE_KST_GUI_PORT`, default **5575**) | host port for `:5572` WebGUI |
| **PUID/PGID/TZ** | `rclone/.env` | set to `1000/1000` and the site timezone |

> The `.env` shipped here defines `RCLONE_GUI_PORT` but the compose actually reads
> `RCLONE_KST_GUI_PORT` (default 5575) — set the latter if you want a custom port.

### 4d. Connecting the mount into openclaw

In `openclaw/docker-compose.yml` the host mount is bound to a **non-nested
top-level path** inside the container, then symlinked into the workspace:

```yaml
- type: bind
  source: ../shared/gdrive_kst
  target: /home/node/gdrive_kst        # NOT under the workspace bind
  bind: { propagation: rslave }
```
```
# inside the workspace:
.openclaw/workspace/gdrive_kst -> /home/node/gdrive_kst   (symlink)
```

**Why not bind directly into the workspace?** Docker silently fails when a FUSE
bind is nested inside another bind-mounted dir (rprivate propagation). The fix is
the top-level target + `rslave`/`rshared` propagation + a workspace symlink so the
agent's paths still read naturally. **Copy this pattern exactly** — it's the #1
gotcha.

### 4e. Operational gotcha — recreating the mount

Never plain `docker compose up -d` the rclone service after a config change. A
removed rclone container leaves a **stale FUSE endpoint** (`transport endpoint is
not connected`) that breaks openclaw's bind on next start. Use the provided
[`rclone/recreate.sh`](/home/damien/code/rclone/recreate.sh): it `compose down`s,
clears a stale endpoint via a throwaway privileged container (no host sudo), then
`compose up`s. Replicate this script.

**Startup order:** bring up rclone (mount healthy) **before** openclaw.

---

## 5. Models / LLM routing (context, since the agent needs a brain)

Not strictly "access," but required to run. openclaw routes models via a LiteLLM
proxy; provider keys live in `.env` and `openclaw.json`:

- `openclaw.json → models.providers.litellm.baseUrl` = `http://<litellm-host>:4000`
- Default model: `openclaw.json → agents.defaults.model.primary`
- Direct provider keys (fallback): `openclaw/.env` (`OPENROUTER_API_KEY`,
  `OPENROUTER_MODEL`) and `credentials/openrouter.key`.

For Hi-Orbit you'll likely point this at the same LiteLLM proxy or a direct
OpenRouter/Anthropic key.

---

## 6. Complete credentials & config checklist

Everything you must supply to stand up an openclaw-style agent with all three
capabilities:

**Discord**
- [ ] Discord **bot token** (Developer Portal) → `openclaw.json`
- [ ] **Message Content Intent** enabled on the bot
- [ ] Bot **invited** to the server with read/send/history perms
- [ ] **Guild ID** + **channel ID(s)** → `openclaw.json`
- [ ] Operator **user/role IDs** → `credentials/discord-allowFrom.json`

**Local repo / file editing**
- [ ] Host repo/corpus paths bind-mounted in `docker-compose.yml`
- [ ] `OPENCLAW_CONFIG_DIR` + `OPENCLAW_WORKSPACE_DIR` in `.env`
- [ ] Container runs as **uid/gid 1000** (host-aligned)
- [ ] (optional) `docker.sock` mount + correct `DOCKER_GID`
- [ ] (optional) git identity/credentials in `$HOME` if the agent pushes

**Google Drive (rclone)**
- [ ] **Google OAuth token** (`rclone authorize "drive"`) → `rclone.conf`
- [ ] (recommended) own **OAuth client_id/secret** (Google Cloud Console)
- [ ] **Shared Drive ID** (`team_drive`) + scope (`drive.readonly` for corpus)
- [ ] rclone **WebGUI user/pass** changed from `admin/admin`
- [ ] FUSE flags: `--uid/--gid 1000 --umask 002 --allow-other`, `vfs-cache-mode full`
- [ ] Mount bound to a **top-level** container path + workspace **symlink**
- [ ] `recreate.sh` used for restarts; rclone started **before** openclaw

**Models**
- [ ] LiteLLM base URL or direct provider key (`OPENROUTER_API_KEY` / Anthropic)
- [ ] Default model set in `openclaw.json`

**Host prerequisites**
- [ ] Docker + Docker Compose
- [ ] `/dev/fuse` available (for the rclone container)
- [ ] User uid/gid 1000 owning the bind-mount source dirs
- [ ] (recommended) Tailscale or equivalent for safe access to WebGUIs/gateway

---

## 7. Bring-up order (summary)

1. Put OAuth token in `rclone/data/rclone_config/rclone.conf`; set `rclone/.env`.
2. `cd rclone && ./recreate.sh` → confirm `shared/gdrive_kst` is a healthy mount.
3. Set `openclaw/.env` (config dir, workspace dir, ports, gateway token, model key).
4. Put Discord token + guild/channel IDs in `openclaw.json`; operator IDs in
   `credentials/discord-allowFrom.json`.
5. `cd openclaw && docker compose up -d --build`.
6. Verify: gateway `/healthz` green, bot online in Discord, agent can `ls
   workspace/gdrive_kst` and edit files under `workspace/projects`.

---

## 8. Rolling it all into a single docker compose

The live `agent2`/openclaw deployment runs rclone and the agent as **two
separate compose projects** (in `rclone/` and `openclaw/`). That's deliberate —
they have different privilege needs and lifecycles. For a self-contained pilot
like Hi-Orbit, both services run in **one compose project** instead, letting
Compose order them by health.

[`single-compose/`](single-compose/) is **the real, Hermes-native scaffold** for
Hi-Orbit (built 2026-06-25, not an illustrative template):

| Path | Purpose |
|------|---------|
| [`docker-compose.yml`](single-compose/docker-compose.yml) | `rclone-gdrive` + Hermes `gateway` + `dashboard`, one project |
| [`.env.example`](single-compose/.env.example) | compose-scope tunables only (paths, ports, uid/gid, rclone) — copy to `.env` |
| [`hermes-agent/`](single-compose/hermes-agent/) | upstream `nousresearch/hermes-agent`, cloned + pinned at `fa4ebaa8b`; `gateway` builds from here |
| [`bot_memory/hi-orbit/.hermes/`](single-compose/bot_memory/hi-orbit/.hermes/) | `HERMES_HOME` — `config.yaml`, `SOUL.md`, and `.env.example` (runtime secrets scope, separate from the compose `.env`) |
| [`bot_memory/hi-orbit/stage2-hook.sh`](single-compose/bot_memory/hi-orbit/stage2-hook.sh) | the patched init hook (the chown-skip patch below) |
| [`recreate.sh`](single-compose/recreate.sh) | safe full restart (clears stale FUSE endpoint) |

### How the single compose works

- **One project, three services:** `rclone-gdrive` (privileged, owns the FUSE
  mount), `gateway` (Hermes, unprivileged), `dashboard` (same Hermes image,
  `dashboard` command). Only rclone is privileged.
- **Ordering via health, not just start:** `gateway` declares
  ```yaml
  depends_on:
    rclone-gdrive:
      condition: service_healthy
  ```
  and rclone's healthcheck is `mountpoint -q /shared/gdrive_kst`. Hermes does
  not start until the Drive mount is *actually present*, not merely until the
  container launched.
- **The mount still goes through a host path.** rclone mounts to a host dir
  (`GDRIVE_MOUNT_DIR`, default `./shared/gdrive_kst`) with `:shared`
  propagation; Hermes binds that same host path with `rslave` to a
  **top-level** `/opt/gdrive_kst` (NOT nested under `/opt/data` — nested FUSE
  binds silently fail). Same host-path + propagation pattern as §4d.
- **Two secrets scopes, deliberately not merged:** the compose `.env`
  (`single-compose/.env`) only carries values Compose substitutes into the
  YAML (uid/gid, paths, rclone). Hermes itself loads `DISCORD_BOT_TOKEN`,
  `OPENROUTER_API_KEY`, etc. via its own `load_dotenv` from
  `bot_memory/hi-orbit/.hermes/.env` — Docker's `env_file:` is intentionally
  **not** used for the Hermes services, so there's exactly one place each
  secret lives.

### The Hermes-specific gotcha — the stage2-hook patch (must-read)

s6-overlay's stage2 init hook recursively `chown -R`s `.venv`/`ui-tui`/
`node_modules` on **every boot** whenever `HERMES_UID != 10000`. On overlayfs
that forces copy-up of tens of thousands of files — a multi-hour hang, gigabytes
of layer bloat, gateway never starts. `bot_memory/hi-orbit/stage2-hook.sh` is a
copy of the upstream hook with that one block wrapped in a `: <<'HI_ORBIT_SKIP'`
heredoc so it's skipped; it's bind-mounted over
`/opt/hermes/docker/stage2-hook.sh:ro` in **both** `gateway` and `dashboard`.
Re-verify this patch still applies (`grep HI_ORBIT_SKIP`) after any
`hermes-agent` upstream pull — the chown block can move.

### What still has to be done by hand (not expressible in compose)

1. **`rclone.conf` with the OAuth token** → `single-compose/rclone/config/rclone.conf`.
   Generate with `rclone authorize "drive"` (see §4b/§4c). Compose can't mint this.
2. **`bot_memory/hi-orbit/.hermes/.env`** (copy from the `.env.example` next to
   it) with `DISCORD_BOT_TOKEN`, `OPENROUTER_API_KEY`, `DISCORD_ALLOWED_USERS`/
   `DISCORD_ALLOW_ALL_USERS`, home channel.
3. **`bot_memory/hi-orbit/.hermes/config.yaml`** placeholders — model id,
   `discord.allowed_channels`.
4. **Target-host check:** `/dev/fuse` must exist on whatever host actually
   runs this — confirmed **absent** in this dev sandbox, so `rclone-gdrive`
   cannot be brought up here. The Hermes image build/config don't need FUSE
   and were verified in this sandbox; the FUSE mount + full end-to-end run
   needs the real on-site host (preflight.md A1).

### Bring-up (single compose)

```bash
cd single-compose
cp .env.example .env                              # compose-scope vars
cp bot_memory/hi-orbit/.hermes/.env.example bot_memory/hi-orbit/.hermes/.env  # runtime secrets
# fill both .env files, then:
rclone authorize "drive"        # paste result into rclone/config/rclone.conf
# fill bot_memory/hi-orbit/.hermes/config.yaml placeholders
docker compose up -d --build
docker compose ps               # rclone healthy, then gateway/dashboard healthy
```

### Restart semantics (important)

- **Hermes-only change** (config, image): `docker compose up -d gateway
  dashboard` — safe, the mount is untouched.
- **Full restart / rclone change:** use [`single-compose/recreate.sh`](single-compose/recreate.sh),
  not a bare `down`/`up`. A plain `docker compose down` removes the rclone
  container and can leave a **stale FUSE endpoint** (`transport endpoint is not
  connected`) that breaks Hermes's bind next start. `recreate.sh` clears it via
  a throwaway privileged container (no host sudo). Same gotcha as §4e — it
  doesn't go away just because both services share a compose file.

### Trade-offs vs. the two-project layout

| | Single compose | Two projects (current host) |
|---|---|---|
| Lifecycle | one `up`/`down`, ordered by health | independent; mount survives Hermes rebuilds |
| Blast radius | `down` takes the mount with it | restart Hermes without touching Drive |
| Portability | self-contained pilot folder | shared mount feeds *multiple* bots (fleet) |
| Best for | a single dedicated-host pilot (Hi-Orbit) | a multi-bot host |

For Hi-Orbit's "new dedicated host" plan, the single compose is the better fit:
one folder, one command, reproducible from this repo.

---

## 9. If you build on Hermes instead of openclaw

The Hi-Orbit README names **Hermes** (NousResearch) as the engine, and there's a
live Hermes bot on this host (`agent5`). The good news: **the entire rclone /
Google Drive half of this recipe is engine-agnostic and unchanged.** Only the
*agent* container differs. Source of truth on the host:

> - Hermes repo + compose: [`/home/damien/code/hermes-agent/`](/home/damien/code/hermes-agent/)
> - Hermes runtime home (`HERMES_HOME`): `/home/damien/code/bot_memory/agent5/.hermes/`
>   (`config.yaml`, `.env`, `SOUL.md`, `workspace/`, SQLite `state.db`)

### What stays exactly the same

- **The rclone container** (§4) — same image, same `rclone.conf`, same OAuth
  token, same flags.
- **The top-level mount + `rslave` + workspace-symlink pattern** (§4d). Hermes
  binds the FUSE mount to `/opt/gdrive_kst` (top-level, NOT under the workspace
  bind) with `propagation: rslave`, and symlinks it in from the workspace —
  identical reasoning to openclaw, plus a second reason: it keeps Hermes' per-boot
  `chown -R .../workspace` from walking the Drive tree.
- **uid/gid 1000 alignment** for the shared `../projects` mount.
- **LiteLLM model routing** at `http://100.67.191.114:4000` and the host-path
  decoupling of the two containers.

### What changes (openclaw → Hermes mapping)

| Concern | openclaw | Hermes |
|---|---|---|
| Primary config | `openclaw.json` (one JSON) | `config.yaml` (large YAML) **+** `.env` (secrets) **+** `SOUL.md` (persona) |
| `$HOME` / state dir | `/home/node/.openclaw` | `/opt/data` = `HERMES_HOME` |
| Discord token | in `openclaw.json` | in `.env` → `DISCORD_BOT_TOKEN` |
| Discord allowlist | `credentials/discord-allowFrom.json` | `.env` `DISCORD_ALLOWED_USERS` / `DISCORD_ALLOW_ALL_USERS`, **and** `config.yaml → discord` |
| Model routing | `openclaw.json → models.providers.litellm` | `config.yaml → model:` (`provider: custom`, `base_url`, `api_key`) |
| uid remap | image runs as `node` (uid 1000) directly | `HERMES_UID`/`HERMES_GID` env → s6-overlay remaps the internal `hermes` user |
| Networking | published ports `18789/18790` | `network_mode: host`; dashboard on `127.0.0.1:9119`, no published gateway port |
| Process model | `node dist/index.js gateway` | s6-overlay `/init` PID 1 → `gateway run`; a **second** `dashboard` service shares the image |
| Image | build from openclaw repo | build from `hermes-agent/` → image `hermes-agent` |
| Corpus mount path | `/home/node/gdrive` (+ symlink) | `/opt/gdrive_kst` (+ symlink) |

### Discord on Hermes

Two layers, both needed:
- **`.env`**: `DISCORD_BOT_TOKEN` (one live gateway connection per token — don't
  share it with another running bot), and either `DISCORD_ALLOW_ALL_USERS=true`
  (insecure, anyone in-channel/DM can drive tools) or
  `DISCORD_ALLOWED_USERS=<id,id,…>` to lock down. **For Hi-Orbit operators, use
  `DISCORD_ALLOWED_USERS`** (this is open question #4).
- **`config.yaml → discord`**: `require_mention`, `allowed_channels` (list of
  channel IDs, `'*'` for all), `auto_thread`, `history_backfill`, `reactions`,
  `allow_mentions`. This is where you scope which channels the bot answers in.

### Models / vision — a Hermes advantage for this pilot

`config.yaml → model:` sets the primary (`provider: custom` + `base_url` +
`api_key`; for a non-OpenRouter base_url Hermes reads `OPENAI_API_KEY` from
`.env`). More relevant to Hi-Orbit's **diagram/schematic** problem (corpus open
question #1): Hermes has a built-in **`auxiliary.vision`** model slot (provider /
model / base_url / api_key). That gives you a native captioning/vision hook for
the design-doc images without bolting on a separate ingest step — worth
evaluating against the RAG plan in [`corpus-plan.md`](corpus-plan.md).

### Persona maps cleanly

Hermes reads **`SOUL.md`** from `HERMES_HOME` as the agent's identity — the same
`SOUL.md` this pilot already defines. No translation needed: drop the pilot's
`SOUL.md` into the Hermes home.

### The Hermes-specific gotcha (must-read before you deploy)

The s6-overlay **stage2 init-hook recursively chowns the install tree on every
boot** whenever `HERMES_UID != 10000`. On overlayfs (this host) that forces
copy-up of tens of thousands of files → a **multi-hour hang** and GBs of bloat;
the gateway never starts. The live fix is a patched `stage2-hook.sh` (the
install-tree chown neutralized) bind-mounted over
`/opt/hermes/docker/stage2-hook.sh:ro` in **both** services. If you stand up a
fresh Hermes host, either apply that patch **or** rebuild the image with the
Hermes UID baked to 1000 so the per-boot chown is a no-op. Re-check this on every
Hermes update.

### Single-compose implications — implemented

The §8 single-compose now ships Hermes-native (`single-compose/`, built
2026-06-25, verified against upstream `fa4ebaa8b`):
- `gateway` builds from the cloned `hermes-agent/` context; `image:
  hi-orbit-hermes:local`.
- `network_mode: host` on both `gateway` and `dashboard` (no `ports:` block;
  the dashboard is `127.0.0.1:9119`, tunnel via SSH for remote access).
- `dashboard` is a second service, same image, `command: ["dashboard",
  "--host", "127.0.0.1", "--no-open"]`.
- `bot_memory/hi-orbit/.hermes` → `/opt/data`; corpus → `/opt/gdrive_kst`;
  `projects/` → `/opt/projects`.
- `depends_on: rclone-gdrive: condition: service_healthy` gate is in place.
- The patched `stage2-hook.sh` is bind-mounted into both services.

One correction vs. the snapshot this section was written from: current
upstream (`fa4ebaa8b`) prefers `model: { default, provider: openrouter }` —
no `provider: custom` / inline `base_url`/`api_key` needed; the key comes
from `OPENROUTER_API_KEY` in `.env` and is auto-detected. The template at
`single-compose/bot_memory/hi-orbit/.hermes/config.yaml` uses the current form.

### Hermes credentials checklist (delta vs. §6) — what's still TBD

- [ ] `DISCORD_BOT_TOKEN` in `bot_memory/hi-orbit/.hermes/.env` (dedicated
  token, not shared with a running bot)
- [x] User-access policy resolved 2026-06-04: `DISCORD_ALLOW_ALL_USERS=true`
  — rely on Discord's own bot-install/invite flow, not a user-ID allowlist
- [ ] `config.yaml → discord.allowed_channels` scoped to the ops channel(s)
- [ ] `OPENROUTER_API_KEY` in `.env` + `config.yaml → model.default` (model id)
- [ ] (optional) `config.yaml → auxiliary.vision` for diagram captioning
- [x] `SOUL.md` placed in `HERMES_HOME` — done, copied from the pilot root
- [x] `HERMES_UID=1000` / `HERMES_GID=1000` + the stage2-hook patch — applied
- [ ] rclone half: unchanged from §4, still needs the OAuth token + Shared
  Drive ID; **also needs a target host with `/dev/fuse`** — absent in the dev
  sandbox this was built in

---

*Derived from the live `agent2`/openclaw and `agent5`/Hermes deployments on this
host (2026-06-25). Secret values are referenced by location only — never commit
real tokens to this repo.*
