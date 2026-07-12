# Google Drive — Connect an Agent to a Drive Document Store

**Type:** deployment-playbook
**Status:** draft
**Owner:** —
**Last reviewed:** 2026-06-04
**Applies to:** Any tier needing read access to a Google Drive corpus. Pairs with
[`rag-setup.md`](rag-setup.md) when the Drive contents should be searchable.

> ⚠️ Verify every Google-console and API detail below against current Google
> documentation (last checked: 2026-06-04). Google changes OAuth scopes, consent
> requirements, and API surfaces on its own schedule — assume specifics drift.

---

## 1. Goal

Give an agent **read/search** access to a Google Drive (or a Shared Drive / specific
folder), so it can list, fetch, and answer from documents there. Done = the agent
can retrieve a named document's contents on request, scoped to only what it should
see.

## 2. Choose an auth model first

This decision shapes everything else:

- **Service account (recommended for unattended/team agents).** A non-human
  identity. Either share the specific Drive folder *with the service account's
  email*, or (Workspace only) use domain-wide delegation to impersonate a user.
  Best when the agent runs without a human present.
- **OAuth user delegation (3-legged).** The agent acts as a specific human who
  grants consent. Best for personal-scope agents; requires a consent flow and
  refresh-token storage.

> ⚠️ Domain-wide delegation grants broad access — use the narrowest scope and prefer
> per-folder sharing with a service account over delegation when possible.

## 3. Prerequisites

- A Google Cloud project (the operator can create one).
- The Drive API enabled on that project.
- Admin rights to either share the target folder with the service account, or (for
  delegation) configure it in the Workspace Admin console.

## 4. Secrets & config (placeholders only)

| Value | Placeholder | Lives in |
|---|---|---|
| Service-account JSON key | `<GDRIVE_SA_KEY_JSON>` | secrets manager / mounted file, **never the repo** |
| (OAuth) client ID/secret | `<GDRIVE_OAUTH_CLIENT_ID>` / `<...SECRET>` | runtime secrets |
| (OAuth) refresh token | `<GDRIVE_REFRESH_TOKEN>` | secrets manager |
| Target folder/Drive ID | `<GDRIVE_FOLDER_ID>` | deployment config |

## 5. Scopes (least privilege)

Start read-only. Common scopes (⚠️ confirm current names/behavior):

- `drive.readonly` — read all files the identity can access.
- `drive.metadata.readonly` — list/search metadata without content.
- `drive.file` — only files the app created/opened (narrowest; often too narrow for
  a corpus).

Prefer `drive.readonly` **combined with sharing only the target folder** to the
service account, so scope breadth is bounded by what's actually shared.

## 6. Steps

1. **Create/select a Google Cloud project** and **enable the Drive API**.
   → *Verify:* Drive API shows enabled in the console.
2. **Create the identity.** Service account (download a key) *or* OAuth client.
   → *Verify:* you have `<GDRIVE_SA_KEY_JSON>` or `<GDRIVE_OAUTH_CLIENT_ID>` stored
   in the secrets store (not the repo).
3. **Grant access narrowly.** Share `<GDRIVE_FOLDER_ID>` with the service account's
   email (Viewer), or run the OAuth consent flow and capture the refresh token.
   → *Verify:* the identity can see the folder.
4. **Wire the connector** in the agent's environment using the stored credential;
   point it at `<GDRIVE_FOLDER_ID>`. → *Verify:* a `files.list` call returns the
   folder's files.
5. **Fetch content.** For Google-native docs (Docs/Sheets/Slides) use **export**
   (e.g. to text/markdown); for binaries use **get media**. → *Verify:* you can
   pull one document's text.
6. **(If searchable) hand off to RAG.** Feed exported text into
   [`rag-setup.md`](rag-setup.md) as the corpus source. → *Verify:* the document is
   retrievable via the `search` tool.

## 7. Verification (end-to-end)

Ask the agent to fetch or answer from a specific document in the shared folder. It
returns the right content. Then confirm **negative scope**: it cannot access a
document *outside* the shared folder.

## 8. Rollback / teardown

- Un-share the folder from the service account, or revoke the OAuth grant
  (console → Security → third-party access).
- Delete the service-account key / refresh token from the secrets store.
- Disable the Drive API or delete the Cloud project if the deployment is ending.

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 403 on list/get | Folder not shared with the identity, or scope too narrow | Share folder; widen to `drive.readonly` |
| Native docs return empty/binary | Used "get media" on a Google-native doc | Use the **export** endpoint with a text/md MIME type |
| Auth works, no files | Wrong `<GDRIVE_FOLDER_ID>` or Shared Drive not added | Confirm the ID; add the identity to the Shared Drive |
| Token expired | Refresh token revoked/rotated | Re-run consent; rotate the stored token |

## 10. Staleness notes

Re-check on review: current scope names and consent-screen requirements, whether
domain-wide delegation policy changed, export MIME-type support, and the Drive API
version / client SDK names. Update the "last checked" date above when you do.
