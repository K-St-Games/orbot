# Implementation Review Feedback

**Verdict:** Changes requested

**Reviewed:** 2026-07-15, parent branch `codex/quill-engineering-review-wip` at
`b7726df`; child commits `hi-orbit-wiki@aa9781f` and
`vendor/kst-beta-ide@7c9c113`.

The implementation behavior now passes independent local browser and HTTP validation.
Repository-first startup loads the full Hi-Orbit tree without narrative startup, documents
open normally, the retained ✎ toggle now loads a populated narrative workspace, and the
read-only/Git-status boundaries hold. Two review-contract issues remain before this slice
is ready for host acceptance.

## Required corrections

### P1 — Reconcile `CURRENT_TASK.md` with the submitted commits and verified results

The governing handoff still combines the old recovery instructions with obsolete evidence:

- Lines 39–51 label the already-fixed `7b8b0c2` crash, state leakage, Git-status ancestry,
  and stale comments as **Current failures**.
- Lines 174–180 claim `git diff --name-only 6d51479...HEAD` has no output and describe the
  earlier `1057eae` diff. The live command returns the two approved files.
- Lines 189, 196, and 249 report 141 tests; the current suite has 142.
- Lines 200, 233, and 245 still identify `1057eae` as the parent pin/final dependency;
  the parent records `7c9c113`.
- Lines 236 and 256 contradict one another by marking clean-browser checks complete and
  then listing the same local browser checks as remaining host gates.
- Line 240 leaves committing/pushing the parent unchecked even though `b7726df` is clean
  and matches `origin/codex/quill-engineering-review-wip`.

**Required correction:** Turn this into a current-state handoff: move the historical crash
and recovery recipe into a short resolved/context section (or remove it), record
`7c9c113`, 142 tests, the real two-file scope diff, and the local browser/HTTP evidence
below. Leave only actual deployment-host work open: Docker/Compose build and restart,
OS-level read-only mount, MkDocs regression, and engineering-lead usability approval.

**Done when:** A new agent can trust every SHA, test count, status label, checkbox, and
remaining-gate statement without reconstructing this review history.

### P2 — Finish the startup-test error contract and cleanup discipline

The repository-start test now records narrative requests, opens a Markdown document, and
covers the repaired toggle. It still intercepts only `console.error`
(`repositories.test.ts:1813-1843`), although the handoff requires failure on uncaught
exceptions and unhandled rejections too. It also restores `console.error` only on the
success path, so a failed assertion or initialization can leak the interception into later
tests. The failure-case repository class is similarly restored only after successful init.

**Required correction:** Capture uncaught/unhandled failures using deterministic process or
window listeners appropriate to this test harness, assert none occurred, and restore all
global mocks/listeners in `finally`/test cleanup. Keep the existing explicit zero-request,
readable-document, failure-state, and toggle assertions.

**Done when:** An unhandled rejection or uncaught startup exception fails the focused test,
and an intentional failure cannot contaminate subsequent tests through `console.error`,
`fetch`, DOM/window, or `HttpFileRepository` globals.

## Independently verified evidence

### Git and automated checks

- Parent and both child worktrees are clean; the parent branch matches its origin.
- Parent records `hi-orbit-wiki@aa9781f` and `vendor/kst-beta-ide@7c9c113`.
- `6d51479` is an ancestor; forbidden `97ce7c5` and `b18be40` are not.
- `git diff --name-only 6d51479...HEAD` returns exactly:
  - `services/quill-api/src/routes/repositories.test.ts`
  - `writer/app.js`
- Git-status implementation search returned no matches.
- `npm test` — 142 passed, 0 failed, 0 cancelled.
- `npm run typecheck` — passed.
- `node --check ../../writer/app.js` — passed.
- `git diff --check` — passed in parent and both children.

### Real-browser and HTTP checks

Environment: headed Chromium against production `writer/` assets and the real Quill API
through a temporary same-origin proxy, using the checked-out `hi-orbit-wiki` and
`QUILL_READ_ONLY=true`.

- `/` returned `302 /writer/?mode=repository`.
- Repository mode was the first visible application state and loaded 24 files.
- Root `README.md` opened and rendered successfully.
- The ✎ transition loaded 8 scenes, 4 characters, and 3 locations.
- Repository metadata returned `readOnly: true`.
- Malformed and valid PUT requests both returned `403 READ_ONLY`.
- The Git-status endpoint returned `404`; no Changes tab was present.
- No application exception appeared. The only browser error was the temporary proxy's
  irrelevant `favicon.ico` 404.

## Validation still requiring the deployment host

- Docker/Compose image build and clean restart.
- OS-level read-only bind-mount enforcement.
- MkDocs canonical-only regression.
- Engineering-lead usability approval.

## Required finish sequence

1. Reconcile `CURRENT_TASK.md` to `b7726df` / `7c9c113` and the evidence above.
2. Add uncaught/unhandled coverage and reliable global cleanup to the focused frontend tests.
3. Rerun the existing automated and browser gates.
4. Commit and push the corrections on the existing parent and child recovery branches.
5. Request independent re-review; do not merge to parent `main` yet.

## Separate earlier review

The prior review of `105b34f` identified a Drive sentinel-default contradiction and a
pending-task plan that bypasses roadmap gates. Those remain separate from this Quill slice.
