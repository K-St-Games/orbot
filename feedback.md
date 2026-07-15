# Implementation Review Feedback

**Verdict:** Changes requested

**Reviewed:** 2026-07-15, parent `main` at `520b2b0` plus the current integration
working tree, staged gitlinks `hi-orbit-wiki@aa9781f` and
`vendor/kst-beta-ide@7b8b0c2`, and the active `CURRENT_TASK.md` contract.

The startup-order branch, actual-init test calls, full-hierarchy fixture, child commits,
and handoff reconciliation are present. However, a clean real-browser run fails before
repository discovery, and the new dependency pin imports an unrelated Git-review feature
that is explicitly outside this slice.

## Required corrections

### P0 — Fresh repository-mode startup crashes before loading the wiki

In a clean Chromium session, `/` correctly redirected to
`/writer/?mode=repository`, but initialization threw:

```text
TypeError: Cannot read properties of undefined (reading 'forEach')
    at render (writer/app.js:964)
    at init (writer/app.js:3289)
```

The new startup branch skips `loadData()`, leaving the narrative `story` object without a
`plotlines` array. The first `render()` still executes narrative sidebar rendering and
calls `story.plotlines.forEach(...)` even though repository mode is active. The browser
remained on an "Untitled Novel" manuscript shell with the repository sidebar stuck at
"Loading…"; the Hi-Orbit tree never loaded.

**Required correction:** Make repository-mode rendering independent of initialized
narrative data. Prefer skipping creative/narrative rendering work entirely when
`state.repoMode` is true; alternatively establish complete safe state invariants before
the first render. Do not restore the unnecessary narrative fetch as the workaround.

**Done when:** A clean browser profile reaches the Hi-Orbit repository reader with no
console exception, no narrative fetch, no narrative content, and a populated tree.

### P1 — The init tests pass through shared state that hides the production crash

The expanded tests invoke `window.onload()`, but they reuse a module-level singleton and
DOM/state populated by earlier narrative tests. They therefore do not reproduce a fresh
repository-only start. The suite passed 163/163 while the same committed code failed in a
clean browser. Test output also contains repository-load errors that the relevant test does
not treat as failures.

**Required correction:** Isolate/reset startup state and DOM for each initialization case.
The repository-start test must begin with no narrative data, invoke the real init path,
await repository discovery, and assert a populated repository UI plus zero startup errors.
The no-narrative-fetch assertion must also require repository loading to succeed rather
than checking only `repoMode`.

**Done when:** The new test fails against `7b8b0c2`, passes after the P0 fix, and fails on
either a render exception or repository-discovery failure.

### P1 — The pinned dependency imports an out-of-scope Git-review feature

`7b8b0c2` is not merely `6d51479` plus the requested corrections. Its ancestry includes
PR #7 / `b18be40`, which adds a visible **Changes** tab, a Git-status API route, child
process execution of `git`, and more than 900 lines of Git-review implementation. The
browser snapshot confirmed that the Changes tab is exposed in Orbot.

This directly conflicts with `AGENTS.md` and `CURRENT_TASK.md`, which exclude Git review
from this slice. It is also not operational in the current container boundary:
`Dockerfile.quill-api` does not install Git, and the API receives only the wiki worktree,
not the parent submodule Git metadata a reconstructed checkout would reference.

**Required correction:** Pin Orbot to a pushed, reconstructable Quill commit containing
the repository-start/read-only/full-tree work without the Tier 2 Git-status feature, or
add a clean generic capability flag that disables both the Changes UI and Git-status API
for this Orbot deployment. Do not expose a dead Git-review surface as incidental upstream
drift.

**Done when:** The normal Orbot reader exposes only the approved read-only browsing
surface, the Git-status route is unavailable or deliberately disabled, and the pinned
commit remains reproducible from the upstream repository.

### P2 — Reconcile `CURRENT_TASK.md` after the corrected pin

The handoff currently claims local verification is complete, but the clean-browser gate
fails. After correcting the startup and dependency scope, update it with the final exact
child commit, independently verified local evidence, and the remaining host/engineering-
lead acceptance step.

## Resolved portions

- Startup-mode detection now occurs before narrative loading.
- Repository-start requests skip `loadData()`.
- Tests now call the real `window.onload()` path, though their isolation is insufficient.
- The committed full-hierarchy fixture covers all six review directories, root Markdown,
  representative reads, supported assets, and control-file exclusions.
- `hi-orbit-wiki@aa9781f` correctly records `content.root: .`.
- Both child worktrees are clean and pushed; parent gitlinks record their current commits.

## Independently verified evidence

- `npm test` — passed, 163/163. The count includes 14 Git-status tests and other
  out-of-scope Tier 2 tests inherited by the dependency pin.
- `npm run typecheck` — passed.
- `node --check ../../writer/app.js` — passed.
- Full-hierarchy fixture — passed.
- Real Chromium startup — failed with `story.plotlines.forEach` exception; wiki tree did
  not load; visible controls included the out-of-scope Changes tab.
- `git diff --check` in the parent and both children — passed.
- Dependency history inspection — `7b8b0c2` descends through Git-status PR #7
  (`2a37ad9`, `b18be40`, `89807da`, `97ce7c5`) after `6d51479`.

## Remaining host gate

Do not redeploy this revision yet. After local browser and scope corrections pass, run the
full `CURRENT_TASK.md` host acceptance list: clean image build/restart, direct repository
landing, full tree and exclusions, links/assets, refresh/restart reconstruction, browser/
API/OS read-only enforcement, canonical-only MkDocs behavior, and engineering-lead
usability approval.

## Separate earlier review

The prior review of `105b34f` identified a Drive sentinel-default contradiction and a
pending-task plan that bypasses roadmap gates. Those remain separate from this Quill slice.
