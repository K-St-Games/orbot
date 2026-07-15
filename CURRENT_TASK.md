# Current Task

**Status:** Local verification complete; deployment-host acceptance pending

**Last updated:** 2026-07-15

**Owner:** Human owner, with implementation-agent execution and engineering-lead testing

## Outcome

When the engineering lead opens the Orbot Quill URL, it should land directly in the
Hi-Orbit repository reader rather than the narrative-writing interface. The read-only tree
should expose the full useful `hi-orbit-wiki` content hierarchy so the engineering lead can
review canonical articles, drafts, evidence, metadata, repairs, and templates in one test
interface.

This is an engineering evaluation surface, not a change to publication or retrieval
authority. Canonical `docs/` remains the only normal operator-facing and future retrieval
source.

## Confirmed baseline

- Parent `main` is at `520b2b0` (working tree includes uncommitted child gitlink updates).
- `hi-orbit-wiki` is recorded at `aa9781f` (`content.root: .`).
- Quill is pinned through `vendor/kst-beta-ide` at `7b8b0c2`.
- Both child commits are pushed and reconstructable via `git submodule update --init --recursive`.
- Quill now defaults to repository reader mode when accessed via `/writer/?mode=repository`.
  The nginx root (`/`) redirects to that URL. Narrative mode remains available via the
  folder toggle and when `?mode` is absent.
- `hi-orbit-wiki/quill.yml` has `content.root: .`, exposing the full useful tree (docs,
  drafts, evidence, meta, repairs, templates, root Markdown) while excluding `.git`,
  dotfiles, `quill.yml`, and unsupported types.
- The API and browser are read-only, the wiki is mounted read-only, PUT returns `403 READ_ONLY`.
  These controls must not regress.
- The startup-order fix detects `?mode=repository` before any async narrative load,
  preventing narrative-page flash. `loadData()` is skipped entirely for repository-start
  requests.
- Deterministic tests: `npm test` 163/163 pass, `npm run typecheck` clean.

## Owner-approved decisions

1. The default Orbot Quill experience should be repository mode. It is acceptable to leave
   the narrative mode available behind its existing toggle; it must not be the initial page
   reached from the normal Orbot URL.
2. The engineering lead may view the full useful `hi-orbit-wiki` repository tree.
3. This wider visibility is approved only for the private engineering test interface. It
   does not promote drafts/evidence/repairs/meta/templates to canonical status and must not
   broaden Discord retrieval or the MkDocs fallback.
4. The entire surface remains read-only for this slice. Editing, Git mutation, and PR
   authoring remain deferred.

## Implementation scope

### 1. Add a generic repository-start mode to Quill

Implement this capability in the upstream `K-St-Games/kst-beta-ide` Quill source rather
than hardcoding Hi-Orbit behavior into the reusable frontend.

- Support an explicit URL mode such as `/writer/?mode=repository`.
- During initialization, enter repository reader mode, load repository discovery, select
  the available repository, and render its tree without requiring the folder-toggle click.
- Avoid a visible narrative-page flash before repository mode loads.
- Keep the existing manual toggle unless removing it is materially simpler and does not
  damage Quill's reusable narrative-writing use case.
- The generic Quill implementation must not contain the string `hi-orbit-wiki` or assume a
  single installation name. The Orbot deployment currently mounts one repository, so
  selecting the first discovered repository is sufficient for this slice.
- Add deterministic frontend tests for repository-start initialization and normal/default
  initialization. Existing narrative behavior without the explicit mode must remain valid
  upstream.

### 2. Make repository mode the Orbot entry point

- Update the Orbot-owned Nginx adapter so `/` redirects to the explicit repository-start
  URL.
- Preserve the existing `/api/quill/v1/` proxy and static `/writer/` route.
- Do not deploy the full KSt Beta IDE web image or add other Beta IDE surfaces.

### 3. Expose the full useful Hi-Orbit wiki tree

In the independently versioned `hi-orbit-wiki` repository, change `quill.yml` from
`content.root: docs` to `content.root: .`.

With Quill's current file policy, "full repository" means the supported reviewable content
tree: Markdown and supported image assets beneath the repository root. It should include
root Markdown plus `docs/`, `drafts/`, `evidence/`, `meta/`, `repairs/`, and `templates/`.
It should continue excluding `.git`, dotfiles such as `.DS_Store`, `quill.yml`, and
unsupported file types. Do not weaken path-containment, symlink, extension, size, or
host-path protections to make more files appear.

Add or update deterministic API tests proving a root content directory is valid and that
representative supported paths across the full hierarchy can be listed/read safely.

### 4. Preserve deployment and trust boundaries

- Keep `QUILL_READ_ONLY=true`.
- Keep the API wiki bind mount `read_only: true`.
- Keep browser editor/save controls unavailable in read-only repository mode.
- Keep every PUT shape returning `403 READ_ONLY` before body or filesystem processing.
- Keep MkDocs restricted to canonical `docs/` and available as the fallback.
- Do not change Cortex, Discord/Hermes retrieval, Google Drive automation, ticketing, or
  authoring credentials in this slice.

## Repository and commit sequence (completed)

1. [x] Make the generic repository-start change and its tests in `vendor/kst-beta-ide`.
2. [x] Commit and push that change to `K-St-Games/kst-beta-ide`; recorded at `7b8b0c2`.
3. [x] Change `hi-orbit-wiki/quill.yml`, commit and push; recorded at `aa9781f`.
4. [x] Update both parent gitlinks deliberately.
5. [x] Apply the Orbot-owned Nginx redirect/configuration change in the parent repository.
6. [x] Do not leave required behavior as dirty submodule changes; a recursive fresh checkout
      (`git submodule update --init --recursive`) reconstructs the full slice.

## Required verification

### Local deterministic checks

- `npm test` passes in `vendor/kst-beta-ide/services/quill-api` with the new start-mode and
  repository-root coverage included.
- `npm run typecheck` passes there.
- JavaScript syntax checks pass for modified browser files.
- YAML parsing confirms `hi-orbit-wiki/quill.yml` has `content.root: .`.
- `git diff --check` passes in the parent and both child repositories.
- Both child worktrees are clean at commits recorded by the parent.
- `git submodule update --init --recursive` reconstructs the integration.

### Deployment-host acceptance

1. A clean build and restart of `quill-api` and `quill-web` succeeds.
2. Opening `http://<host>:${QUILL_WEB_PORT}/` lands directly in the Hi-Orbit repository
   reader without a folder-toggle click or visible narrative-page flash.
3. The tree exposes representative files from each populated review area, including:
   root `README.md`, `docs/index.md`, drafts, evidence, `meta/`, `repairs/`, and templates.
4. `.git`, `.DS_Store`, `quill.yml`, unsupported files, traversal paths, symlink escapes,
   and host paths remain unavailable.
5. Existing relative Markdown links and supported image assets render correctly from both
   canonical and noncanonical directories.
6. Repository changes appear after refresh without rebuilding the Quill images, and a
   clean restart reconstructs the same tree.
7. The browser exposes no usable editor/save action; malformed and valid PUT requests both
   return the stable `403 READ_ONLY` envelope; an in-container write attempt against the
   wiki mount fails.
8. MkDocs still serves only canonical `docs/` content.

## Exit gate

The slice exits when the engineering lead can open the normal Quill URL, immediately browse
the full useful Hi-Orbit repository hierarchy, and confirm that the interface is suitable
for documentation review without gaining write capability. Record any usability friction
as evidence for the later editing/review phase rather than expanding this slice in place.

## Explicit non-goals

- Quill editing or repository file management.
- Git commits, branches, pull requests, or automated promotion from Quill.
- Authentication or role-specific UI.
- Reclassifying noncanonical content as reviewed truth.
- Indexing drafts, evidence, repairs, metadata, or templates for Discord answers.
- Cortex selection or implementation, MCP wiring, Drive ingestion, or repair writeback.
- General redesign of the narrative-writing product.

## Separate outstanding review

Root `feedback.md` contains review notes about commit `105b34f`'s Drive healthcheck default
and pending-task plan. Those are separate from this bounded Quill slice. Do not silently
fold Cortex, authoring-loop, or Drive-healthcheck work into this implementation.
