# Deployment Preflight Questionnaire (v0)

**Status:** v0 intake checklist
**Use:** Fill this in **before** starting a deployment (`deploy-hermes-agent.md`).
Every "Required" answer must be in hand before Step 1. Collect the values into
[`config-templates/.env.example`](config-templates/.env.example) (copy it to a real,
**uncommitted** `.env`).

> Secrets discipline: write real values only into the runtime `.env` / secrets store,
> never into this repo. This questionnaire records *what to ask*, not the answers.

---

## A. Host & deployment basics

| # | Question | Required | Notes / where it goes |
|---|---|---|---|
| A1 | What host will run this (OS, Docker 24+ present)? | ✅ | `docker compose version` must work |
| A2 | What is the code root path on that host? | ✅ | `<CODE_ROOT>` in the instructions |
| A3 | UID/GID of the user that will own the data? | ✅ | `id -u; id -g` → `HERMES_UID`/`HERMES_GID` (default 1000) |
| A4 | Pin to a known-good upstream commit, or track latest? | ⬜ | default: pin `fa4ebaa8b` |

## B. Model backend (OpenRouter, direct)

| # | Question | Required | Notes / where it goes |
|---|---|---|---|
| B1 | Model base URL | ✅ | → `config.yaml model.base_url` = `https://openrouter.ai/api/v1` (direct; no proxy) |
| B2 | OpenRouter API key? | ✅ | → `.hermes/.env` `OPENAI_API_KEY` (treat as secret) |
| B3 | Default OpenRouter model id? | ✅ | → `config.yaml model.default` (e.g. `anthropic/claude-sonnet-4.6`, `deepseek/deepseek-chat`) |
| B4 | (RAG only) Embeddings provider/endpoint? | ⬜ | OpenRouter is chat-focused; embeddings may need a separate endpoint — confirm w/ rag-mcp |

## C. Discord

| # | Question | Required | Notes / where it goes |
|---|---|---|---|
| C1 | **Bot token** for *this* bot? | ✅ | developer.discord.com → Bot → Token. → `.hermes/.env` `DISCORD_BOT_TOKEN`. One token = one live bot session; don't reuse across bots. |
| C2 | **Server (guild) ID** the bot joins? | ✅ | Needed to generate the invite link + scope slash commands. Right-click server → Copy Server ID (Developer Mode on). |
| C3 | Which **channels** should the bot respond in? All, or a limited set? | ✅ | If limited, collect channel IDs → `config.yaml discord.allowed_channels`. Empty = every visible channel (not recommended). |
| C4 | **Home channel** (for cron output / proactive messages)? | ✅ | channel ID → `.hermes/.env` `DISCORD_HOME_CHANNEL` (+ `_THREAD_ID`) |
| C5 | **User access**: anyone in the channels, or restricted users? | ✅ | Open = `DISCORD_ALLOW_ALL_USERS=true`. Restricted = `DISCORD_ALLOWED_USERS=<id1,id2>`. **Open means anyone in those channels (or via DM) can drive the agent.** |
| C6 | Require @mention in servers (vs respond to all)? | ⬜ | default: `require_mention: true`, `auto_thread: true` |
| C7 | Bot display name / persona? | ⬜ | identity in Discord app; persona text in `SOUL.md` |

> To get IDs: enable Discord **Developer Mode** (Settings → Advanced), then
> right-click a server/channel/user → "Copy ID".

## D. Google Drive (optional — rclone mount)

Only if the agent needs a Drive corpus. See also
[`../playbooks/google-drive.md`](../playbooks/google-drive.md).

| # | Question | Required | Notes / where it goes |
|---|---|---|---|
| D1 | Need Google Drive access at all? | ⬜ | If no, skip D — the mount is optional |
| D2 | Auth model: **service account** or **OAuth user**? | ✅* | SA recommended for unattended agents (share the folder with the SA email) |
| D3 | (SA) Service-account JSON key? | ✅* | file in secrets store → `RCLONE_CONFIG_<REMOTE>_SERVICE_ACCOUNT_FILE` |
| D4 | (OAuth) client ID / secret / refresh token? | ✅* | via `rclone config`; or `RCLONE_CONFIG_<REMOTE>_*` env vars |
| D5 | Target **folder / Shared Drive ID** (scope of access)? | ✅* | → `RCLONE_CONFIG_<REMOTE>_ROOT_FOLDER_ID` / `_TEAM_DRIVE` |
| D6 | Access scope — read-only or read-write? | ✅* | default & safest: `drive.readonly` |
| D7 | rclone remote name + mount path on host? | ✅* | e.g. remote `kst`, mount `shared/gdrive_kst` → `/opt/gdrive_kst` |

`✅*` = required only if D1 = yes.

## E. Projects corpus (optional bind-mount)

| # | Question | Required | Notes / where it goes |
|---|---|---|---|
| E1 | Expose a host `projects/` dir to the agent? | ⬜ | bind-mounted at `/opt/projects` |
| E2 | Seed it (rsync from a source) or start empty? | ⬜ | rsync `user@src:/code-root/projects/` or `mkdir -p projects` |

## F. Optional gateways / surfaces

| # | Question | Required | Notes / where it goes |
|---|---|---|---|
| F1 | Expose the OpenAI-compatible API server? | ⬜ | off by default; needs `API_SERVER_HOST` + `API_SERVER_KEY` (auth mandatory) |
| F2 | Microsoft Teams gateway? | ⬜ | `TEAMS_CLIENT_ID/SECRET/TENANT_ID/ALLOWED_USERS` (dev.botframework.com) |
| F3 | Google Chat gateway? | ⬜ | `GOOGLE_CHAT_PROJECT_ID/SUBSCRIPTION_NAME/SERVICE_ACCOUNT_JSON/ALLOWED_USERS` |
| F4 | Remote dashboard access? | ⬜ | dashboard is localhost-only by design; use `ssh -L 9119:localhost:9119` |

---

## Sign-off

- [ ] All ✅ Required answers collected
- [ ] Secrets placed in the runtime `.env` / secrets store (not the repo)
- [ ] User-access policy (C5) explicitly chosen and approved
- [ ] Google Drive scope (D6) confirmed least-privilege (if used)
