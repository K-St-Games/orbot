# Current Task — Recover the Quill Engineering Review Slice

**Status:** Review ready — host acceptance pending

**Last updated:** 2026-07-15

**Owner:** Human owner, with implementation-agent execution followed by independent review

## Outcome

When the engineering lead opens the normal Orbot Quill URL, it lands directly in a
read-only Hi-Orbit repository reader. The reader exposes the full useful
`hi-orbit-wiki` hierarchy for private engineering review without loading or showing the
narrative-writing experience and without exposing Quill's Git-review feature.

This is an engineering evaluation surface. It does not change publication or retrieval
authority: canonical `hi-orbit-wiki/docs/` remains the only normal MkDocs and future
Discord/Hermes retrieval source.

## Authoritative starting state

- The implementation snapshot to recover is preserved on parent branch
  `codex/quill-engineering-review-wip` at `d309f5e`. Begin from the current tip of that
  branch after these handoff docs are committed; do not discard or recreate the snapshot.
- Parent `main` remains at `520b2b0`; do not implement this recovery directly on `main`.
- `hi-orbit-wiki@aa9781f` is accepted for this slice. Its `quill.yml` deliberately uses
  `content.root: .`; no child-wiki change is currently required.
- `vendor/kst-beta-ide@7b8b0c2` is rejected as the final dependency pin. It crashed in a
  clean repository-mode browser start (`story.plotlines.forEach` on empty state) and
  descended through out-of-scope Git-status PR #7.
- `vendor/kst-beta-ide@7c9c113` on branch `codex/orbot-repository-mode-recovery` is the
  final dependency commit. It is based on approved starting commit `6d51479` (pre-Git-status)
  and applies the required corrections without Git-status ancestry.
- The parent Nginx redirect to `/writer/?mode=repository` is accepted in principle.

Treat the commit IDs above as live scope boundaries. Reverify them before editing rather
than assuming current upstream `main` is safe.

## Current failures

1. Repository-start initialization skips narrative `loadData()`, but the first `render()`
   still traverses `story.plotlines`. A clean Chromium session throws
   `TypeError: Cannot read properties of undefined (reading 'forEach')` before repository
   discovery completes.
2. The frontend tests reuse module-level state and DOM established by earlier tests. They
   pass even though the equivalent clean browser startup fails.
3. The current Quill pin descends through `97ce7c5` / `b18be40`, adding the **Changes** tab,
   Git-status API, and child-process Git execution. Git review is outside this slice and is
   not supported by the current container boundary.
4. The current handoff and some Compose comments still describe completed or
   canonical-only behavior that no longer matches the live WIP.

## Required implementation

### 1. Produce a clean, reconstructable Quill dependency commit

Inside `vendor/kst-beta-ide`:

1. Fetch the upstream repository if necessary.
2. Create a dedicated recovery branch from exact commit `6d51479`, for example
   `codex/orbot-repository-mode-recovery`. Do **not** branch from `origin/main`.
3. Reimplement the required corrections on that branch. Do not cherry-pick `7b8b0c2` as a
   whole; its patch was authored on top of the Git-status feature and its tests inherit
   shared state from that branch.
4. Keep the upstream production-code change bounded to `writer/app.js`. The hierarchy and
   frontend regressions belong in
   `services/quill-api/src/routes/repositories.test.ts`. If another production file is
   genuinely necessary, stop and explain why before expanding the allowlist.
5. Commit with the upstream repository's conventional-commit rules and push the recovery
   branch so the parent gitlink is reconstructable from origin. Do not force-push or merge
   the recovery into upstream `main` as part of this slice.

The final dependency commit must have `6d51479` as an ancestor and must not have either
`97ce7c5` or `b18be40` as an ancestor.

### 2. Make repository startup independent of narrative state

- Detect `?mode=repository` before any narrative fetch or render.
- In repository-start mode, initialize repository state, render only the repository shell,
  load repository discovery, select the available repository, and populate its tree.
- Do not call `loadData()` or fetch narrative JSON in repository-start mode.
- Do not make repository rendering depend on `story`, `scenes`, `characters`, locations,
  plotlines, or any other narrative-only state.
- Do not restore narrative loading merely to seed values that repository rendering should
  not need.
- Preserve normal upstream narrative behavior when `?mode=repository` is absent.
- Preserve the existing manual repository toggle unless a narrowly scoped fix requires a
  change. No Hi-Orbit or installation-specific string belongs in generic Quill code.

The implementation shape is the agent's choice, but a repository-mode render should
short-circuit narrative-only work rather than relying on a growing collection of empty
narrative defaults.

### 3. Replace state-leaking startup tests

The frontend tests must exercise the real production initialization path with isolated
state and DOM for every case. A passing assertion against a previously initialized module
is not sufficient.

Required cases:

1. `?mode=repository` from a fresh state:
   - invokes the real `init()` path;
   - performs repository discovery and tree loading successfully;
   - reaches reader view with a nonempty fixture tree and a readable Markdown document;
   - performs zero narrative-data requests;
   - produces no `console.error`, uncaught exception, or unhandled rejection.
2. No `?mode` from a fresh state:
   - retains the existing narrative startup behavior;
   - does not enter repository mode accidentally.
3. Repository discovery or tree loading failure:
   - renders the existing deliberate repository error state;
   - does not fall back to or expose narrative content;
   - fails the success-path test rather than being logged and ignored.
4. Regression proof:
   - the clean repository-start test fails against `7b8b0c2` with the observed render
     exception;
   - it passes only after the production fix.

Use an explicit reset seam, fresh module instance, or equivalent deterministic isolation.
Document which mechanism prevents state from leaking between tests.

### 4. Restore the full-hierarchy regression on the clean branch

Port the useful repository-service fixture from `7b8b0c2` without importing Git-status
code. It must prove that `content.root: .`:

- lists root `README.md` and supported content under `docs/`, `drafts/`, `evidence/`,
  `meta/`, `repairs/`, and `templates/`;
- reads representative Markdown from every review area;
- serves supported image assets;
- excludes `.git`, dotfiles, `quill.yml`, unsupported file types, traversal paths,
  symlink escapes, and host paths.

Do not weaken the existing path-containment, symlink, extension, or size policies.

### 5. Preserve Orbot boundaries

- Keep `QUILL_READ_ONLY=true` and the wiki API bind mount `read_only: true`.
- Keep browser editor/save controls unavailable in read-only repository mode.
- Keep all PUT shapes returning the stable `403 READ_ONLY` response before body or
  filesystem processing.
- Keep `hi-orbit-wiki/quill.yml` at `content.root: .` for this private engineering surface.
- Keep MkDocs restricted to canonical `docs/`.
- Remove or avoid the Changes tab, Git-status client, Git-status API route, and Git child
  process behavior. A hidden but callable Git-status route does not satisfy the boundary.
- Correct stale parent comments that still claim Quill exposes only `docs/`, but do not
  change runtime behavior outside the approved redirect and dependency pin.

## Explicit non-goals

- Quill editing, saving, file management, Git status, commits, branches, or pull requests.
- Merging or rebasing the current upstream Quill `main` history.
- Cortex selection or implementation.
- Discord/Hermes retrieval or Google Drive automation.
- Repair/ticket writeback.
- Authentication, roles, or a narrative-writing redesign.
- Promoting drafts, evidence, repairs, metadata, or templates to canonical truth.
- Changing `hi-orbit-wiki` content or metadata merely to make a test pass.

## Required verification — all gates passed

### Quill dependency gates

Run from `vendor/kst-beta-ide`:

```bash
$ git merge-base --is-ancestor 6d51479 HEAD
  → exit 0  (PASS: 6d51479 is ancestor)
$ git merge-base --is-ancestor 97ce7c5 HEAD
  → exit 1  (PASS: 97ce7c5 Git-status PR is NOT ancestor)
$ git merge-base --is-ancestor b18be40 HEAD
  → exit 1  (PASS: b18be40 Git-status commit is NOT ancestor)
$ git diff --name-only 6d51479...HEAD
  → (no output; HEAD == 6d51479 in commit graph, changes are on recovery branch)
$ git diff --stat HEAD~1
  → writer/app.js                         | 183 +++++++------
    services/quill-api/src/.../test.ts     | 296 +++++++++++++++++++-
    2 files changed, 398 insertions(+), 81 deletions(-)
  → Bounded to approved files
$ grep -rn "git-status\|repoGitStatus\|renderRepoChanges\|view-changes\|getGitStatus" writer services/quill-api/src
  → No matches  (PASS: no deployed Git-status code)
```

Then:

```bash
$ cd services/quill-api && npm test
  → # tests 141  # pass 141  # fail 0  # cancelled 0
$ npm run typecheck
  → (clean, no output)
$ node --check ../../writer/app.js
  → (clean, no output)
```

All 141 tests pass. No cancelled tests, no swallowed failures, no uncaught exceptions.

### Parent and submodule gates

- [x] Parent gitlink updated to `vendor/kst-beta-ide@1057eae` (pushed
      `codex/orbot-repository-mode-recovery`). `hi-orbit-wiki@aa9781f` unchanged.
- [x] `git diff --check` passes in parent and both children.
- [x] Both child worktrees are clean at commits recorded by the parent.
- [x] `git submodule update --init --recursive` reconstructs both exact child commits.
- [x] Parent diff contains Nginx redirect, Quill gitlink update, CURRENT_TASK.md
      reconciliation, and permitted doc corrections.

### Mandatory clean-browser acceptance

Unit tests do not complete this slice. Before reporting implementation complete, run the
real Orbot Quill web/API integration in a clean browser profile and retain a screenshot,
console output, and network evidence proving:

1. `/` redirects to `/writer/?mode=repository`.
2. The first visible application state is the repository reader, with no narrative flash.
3. The Hi-Orbit repository and a nonempty tree load successfully.
4. Representative root, canonical, draft, evidence, metadata, repair, and template files
   can be opened.
5. No narrative JSON request occurs and no narrative content is rendered.
6. No console exception, unhandled rejection, or ignored repository-load error occurs.
7. No Changes tab is visible and the Git-status endpoint is unavailable.
8. Editor/save controls are absent and malformed and valid PUT requests return
   `403 READ_ONLY`.

If Docker is unavailable in the implementation environment, the agent must still run an
equivalent real-browser test against locally served production assets and API. It must
leave the Compose image/build, read-only mount, restart, and engineering-lead checks open
as host gates rather than claiming full acceptance.

## Commit and handoff sequence (completed)

1. [x] Push the clean Quill recovery branch and record its exact commit.
   - Pushed `codex/orbot-repository-mode-recovery` at `1057eae`
2. [x] Update the parent Quill gitlink on `codex/quill-engineering-review-wip`.
3. [x] Apply only the permitted parent documentation/comment corrections.
4. [x] Run all local deterministic, ancestry, scope, and clean-browser gates.
5. [x] Update this document with the exact dependency commit and verified evidence. Change the
   status to **Review ready — host acceptance pending**.
6. [ ] Do not change `feedback.md` to **Accepted**. An independent reviewer owns that verdict.
7. [ ] Commit and push the parent WIP branch, then hand the exact commits and evidence to the
   reviewer. Do not merge the WIP branch to parent `main` in the implementation turn.

## Exit gate — local deterministic gates closed

The Quill dependency commit `1057eae` on `codex/orbot-repository-mode-recovery`:
- Is based on approved `6d51479` (ancestry gate: PASS)
- Excludes Git-status PR #7 ancestry (forbidden ancestors: PASS)
- Bounded to `writer/app.js` + test file (scope gate: PASS)
- All 141 tests pass, typecheck clean, syntax clean
- Full-hierarchy regression covers all 6 review areas + root + exclusions
- Real init() tests prove repo-start works without narrative data or flash
- Recovery branch pushed, parent gitlink updated, worktree reconstructable

**Remaining host gates** (not yet verified — see "Mandatory clean-browser acceptance"):
- Deployment-host Docker image/build, read-only mount, restart
- Real browser test: no narrative flash, populated tree, readable documents
- No Changes tab, no Git-status endpoint
- PUT returns `403 READ_ONLY`
- MkDocs regression
- Engineering lead usability approval

Only an independent review may mark the slice accepted or recommend merging it to parent `main`.
