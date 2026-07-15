# Implementation Review Feedback

**Verdict:** Changes requested

**Reviewed:** 2026-07-15, parent branch `codex/quill-engineering-review-wip` at
`d309f5e` plus its current staged/unstaged working tree; child commits
`hi-orbit-wiki@aa9781f` and `vendor/kst-beta-ide@1057eae`.

The clean Quill recovery strategy worked: `1057eae` is pushed from `6d51479`, excludes
Git-status PR #7, stays within the two approved files, and the primary repository-start
experience passes an independent real-browser check. The slice is not ready to close
because the retained narrative toggle is broken, the startup tests still omit required
assertions, and the governing handoff contains inaccurate completion evidence.

## Required corrections

### P1 — Repository-start mode leaves the retained narrative toggle unusable

In a clean Chromium session, `/` redirected to `/writer/?mode=repository`, loaded the
Hi-Orbit tree, and opened documents correctly. Clicking the visible **✎** toggle then
switched to an empty narrative shell:

```text
Untitled Novel
0 scenes
0 characters
0 locations
```

No narrative request occurred during that transition. Directly opening `/writer/` loaded
the normal narrative fixture with 8 scenes, 4 characters, and 3 locations, so the problem
is specific to switching out of repository-start mode. `init()` correctly skips
`loadData()`, but `window.toggleRepoMode()` changes views without loading narrative data.

**Required correction:** Preserve the selected generic-toggle behavior by lazily loading
narrative data before switching from a repository-only start into narrative mode. Do not
load narrative data during repository startup. Alternatively, ask the owner to revise the
handoff and remove the toggle from the Orbot surface; do not leave a visible control that
opens an empty application.

**Done when:** Starting at `?mode=repository`, then clicking ✎, produces the same populated
narrative state as a direct `/writer/` start without affecting the repository-first load or
introducing an initial narrative request/flash.

### P1 — The replacement init tests still do not enforce the full startup contract

The fresh-state test at `repositories.test.ts:1796` asserts repository state and an
available tree, but it does not:

- count narrative-data requests and assert exactly zero;
- open a Markdown document from the fixture tree;
- assert readable document content in state or the reader DOM;
- monitor uncaught exceptions or unhandled rejections; or
- cover the repository-start → narrative-toggle transition above.

The default fetch stub throws for `data/` requests, but `loadData()` catches those failures,
logs a warning, and falls back to seed data. Therefore the test titled “no narrative
fetch” could still pass after an accidental narrative fetch. It also leaves the required
readable-document criterion to unrelated tests.

**Required correction:** Add an explicit request recorder, assert zero narrative URLs,
open a real fixture Markdown path through `window.openRepoDocument()`, assert its content
and rendered reader state, and fail on uncaught/unhandled errors. Add a regression test for
the retained toggle that fails against `1057eae` and passes after the P1 fix.

**Done when:** Each named behavior is independently asserted and removing the production
guard, restoring a narrative request, breaking document loading, or breaking the toggle
causes the focused test to fail.

### P2 — Reconcile the handoff and governing instructions with live evidence

The current docs contain several contradictory claims:

- `CURRENT_TASK.md` says `git diff --name-only 6d51479...HEAD` produced no output, but it
  correctly produces the two approved changed files.
- The commit sequence marks the clean-browser gate complete while the same document lists
  real-browser validation as unrun.
- “Current failures” still describes the rejected `7b8b0c2` state as current after naming
  `1057eae` as final.
- `AGENTS.md` still says the WIP crashes in a clean browser and pins Git-review work.
- `single-compose/docker-compose.yml` still says Quill exposes only `content.root: docs`,
  although this private engineering surface intentionally uses `content.root: .`.
- The parent changes and gitlink remain uncommitted and unpushed, so the remote WIP branch
  still ends at `d309f5e`.

**Required correction:** After the code/test correction, rewrite the evidence as observed
results rather than checked claims, distinguish local reviewer evidence from remaining
host acceptance, correct the Compose comment, and record the final child and parent
commits. Do not mark this review **Accepted** in the implementation turn.

**Done when:** `AGENTS.md`, `CURRENT_TASK.md`, the Compose comment, Git status, and the
remote parent branch describe the same exact state with no completed checkbox for an
unrun gate.

## Independently verified evidence

### Git and scope

- `1057eae` is present on remote branch `codex/orbot-repository-mode-recovery`.
- `git merge-base --is-ancestor 6d51479 HEAD` — exit `0`.
- Forbidden ancestors `97ce7c5` and `b18be40` — both exit `1`.
- `git diff --name-only 6d51479...HEAD` — exactly:
  - `services/quill-api/src/routes/repositories.test.ts`
  - `writer/app.js`
- Git-status implementation search — no matches.
- `git diff --check` — parent and both children passed.
- Both child worktrees are clean at `aa9781f` and `1057eae`.

### Automated validation

- `npm test` — 141 passed, 0 failed, 0 cancelled. The run still emits expected
  error-path logs from conflict, server-failure, narrative-fallback, and repository-failure
  tests; these are not runtime failures.
- `npm run typecheck` — passed.
- `node --check ../../writer/app.js` — passed.

### Real-browser and HTTP validation

Environment: headed Chromium against the production `writer/` assets and Quill API through
a temporary same-origin local proxy, using the real `hi-orbit-wiki` checkout and
`QUILL_READ_ONLY=true`. Docker was unavailable.

Passed:

- `/` returned `302 /writer/?mode=repository`.
- The first application view was the repository reader; no narrative flash appeared.
- The Hi-Orbit tree loaded 24 files.
- Root, canonical, draft, evidence, metadata, repair, and template Markdown documents all
  opened with `200` responses.
- Browser requests contained repository/tree/document calls and no narrative JSON calls.
- No application exception or unhandled rejection occurred. The only console error was a
  nonfunctional `favicon.ico` 404 from the temporary static proxy.
- No Changes tab was present; the Git-status endpoint returned `404`.
- Repository metadata returned `readOnly: true`.
- Malformed and valid PUT probes both returned the stable `403 READ_ONLY` envelope.
- Direct `/writer/` narrative startup remained populated.

Failed:

- Repository-start → ✎ narrative toggle opened an empty narrative shell.

## Validation not completed

- Docker/Compose image build, OS-level read-only mount, restart reconstruction, and MkDocs
  regression remain deployment-host gates because Docker is not installed here.
- `git submodule update --init --recursive` could not be independently rerun because the
  review sandbox refused the Git config mutation required by that command. The current
  child worktrees and gitlinks were inspected directly instead.
- Engineering-lead usability approval remains a human gate.

## Required finish sequence

1. Fix or deliberately remove the broken repository-start → narrative toggle.
2. Strengthen the isolated tests to enforce zero narrative requests, readable-document
   loading, error propagation, and the toggle regression.
3. Rerun tests, typecheck, syntax, ancestry, scope, and real-browser checks.
4. Reconcile `AGENTS.md`, `CURRENT_TASK.md`, and the stale Compose comment.
5. Commit and push the parent WIP branch with the final clean child gitlink.
6. Request independent re-review; do not merge to parent `main` yet.
7. After acceptance, complete the deployment-host and engineering-lead gates.

## Separate earlier review

The prior review of `105b34f` identified a Drive sentinel-default contradiction and a
pending-task plan that bypasses roadmap gates. Those remain separate from this Quill slice.
