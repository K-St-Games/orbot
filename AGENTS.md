# Orbot — Agent Entry Point

Orbot is a reusable operational-knowledge product. Hi-Orbit is its first proving
deployment. The durable center of the product is a private, Git-versioned service manual
with traceable evidence and repair history; Discord/Hermes is the primary MVP interface
for surfacing that knowledge.

## Current phase

The product vision and tiered roadmap are approved in direction and grounded by real
Hi-Orbit corpus samples. The first canonical-only read-only Quill integration passed
owner-reported host validation. The WIP recovery slice in
[`CURRENT_TASK.md`](CURRENT_TASK.md) makes repository mode the Orbot default and exposes
the full useful `hi-orbit-wiki` tree. It has been corrected to pass a clean-browser
startup (no narrative flash, no TypeError on empty narrative state) and the dependency
no longer pins unrelated Git-review work. Local deterministic gates pass;
deployment-host acceptance and engineering-lead approval remain open. Do not merge to
parent `main` before those host gates close. Do not execute the older wiki/Cortex
implementation plan verbatim or resume the previous deployment-only "get it running" mode
without first reconciling the task against the vision and roadmap.

Keep the MkDocs service as a canonical-only fallback. Do not add Quill editing, Git review,
retrieval, Drive automation, or repair writeback to this slice.

Complexity must be earned by observed usage. Build the smallest trustworthy vertical
slice, verify it with real material, and defer speculative product infrastructure.

## Start here

Read these in order before making product, architecture, or planning changes:

1. [`docs/vision/VISION.md`](docs/vision/VISION.md) — durable product north star.
2. [`CURRENT_TASK.md`](CURRENT_TASK.md) — active scope, live repo truth, and next gate.
3. [`docs/vision/VISION_FEEDBACK.md`](docs/vision/VISION_FEEDBACK.md) — approved
   refinements grounded in real corpus samples.
4. [`MVP_ROADMAP.md`](MVP_ROADMAP.md) — tiered execution plan once approved.
5. [`architecture.md`](architecture.md), [`deployment-plan.md`](deployment-plan.md), and
   [`BUILD-KIT.md`](BUILD-KIT.md) — current deployment history and operational detail;
   useful evidence, but not higher authority than the approved vision.

## Repository boundaries

| Path | Responsibility |
|---|---|
| [`docs/vision/`](docs/vision/) | Product vision, feedback, prototypes, and content-model design. |
| [`hi-orbit-wiki/`](hi-orbit-wiki/) | Independently versioned Hi-Orbit knowledge repository, linked as a submodule. |
| `vendor/kst-beta-ide/` | Temporary pinned source dependency for Quill; keep the submodule at the exact reviewed commit in `CURRENT_TASK.md`. |
| [`cortex/`](cortex/) | Vendored retrieval starting point; not yet aligned with the approved product contracts. |
| [`single-compose/`](single-compose/) | Current Hermes/rclone deployment scaffold and runtime integration. |
| [`example_breakdowns/`](example_breakdowns/) | Real corpus samples for design and testing, not the operational corpus. |
| [`playbooks/`](playbooks/) and [`hermes-recipe/`](hermes-recipe/) | Vendored or earlier operational guidance; validate assumptions before reuse. |

Reusable product code and deployment tooling belong in this repository. Installation
knowledge belongs in `hi-orbit-wiki/`. New work should isolate Hi-Orbit-specific runtime
configuration from reusable capabilities without forcing a premature large-scale rewrite.

## Product and knowledge rules

- **Canonical first.** Reviewed Markdown under the wiki's `docs/` is the primary
  operator-facing retrieval source.
- **Evidence is not truth.** Source files, generated breakdowns, notes, and repair records
  may be incomplete, stale, or contradictory. Never silently convert them into canonical
  guidance.
- **Physical deployment wins.** A version-stamped source describes that version; it does
  not prove that version is deployed. Preserve source role and deployment-verification
  state separately.
- **No synthetic installation facts.** Do not invent procedures, repair outcomes,
  citations, provenance, or safety classifications to make an artifact look complete.
- **Human review is the publication gate.** Agent-authored operator procedures remain
  drafts until an engineer approves them.
- **Do not duplicate repair truth.** Repair/ticket writeback is deferred until stakeholders
  choose whether GitHub, ClickUp, or another system is authoritative. The PoC may produce
  copyable summaries but must not create a competing repair-data store.
- **Retrieval indexes are disposable.** Durable knowledge and provenance must be
  rebuildable without preserving a vector database.

## MVP safety contract

Role-based access control is deferred unless dogfooding demonstrates a need. Safety cannot
be deferred:

- Hazardous, unknown, uncovered, or ambiguous procedures escalate rather than instruct.
- Safety classification must be machine-readable at the procedure or section level and
  propagated to retrieval chunks; a document-level label alone is insufficient.
- Missing or unknown safety classification fails closed.
- Hazardous content may remain readable to engineers and maintenance staff in the private
  Git repository even when the chatbot declines to walk a user through it.
- The Google Drive corpus remains read-only by construction.

## Operational and security rules

- Secrets never go in this repository or `hi-orbit-wiki/`. Keep Discord tokens, rclone
  OAuth data, model/API keys, and credentials in runtime `.env` files or a secrets store.
- Do not publish management surfaces such as rclone WebGUI, the Hermes dashboard, the
  gateway, Cortex, or Postgres to a venue network. Use localhost or a private network.
- Preserve the wiki submodule boundary. Commit knowledge changes inside
  `hi-orbit-wiki/`, push them there, then update the parent gitlink deliberately.
- Treat Quill as an external pinned dependency. Do not copy `writer/` into Orbot, follow a
  moving upstream branch, or deploy the upstream full Beta IDE web image unchanged.
- The completed canonical-only Quill gate used `content.root: docs`. The current private
  engineering-review slice deliberately uses `content.root: .` so the engineering lead
  can inspect canonical docs, drafts, evidence, metadata, repairs, and templates. This
  wider Quill visibility does not broaden MkDocs or future Discord retrieval beyond
  canonical `docs/`.
- Mount the wiki read-only into the Quill API only, disable browser editing, and make
  write requests fail explicitly as read-only rather than as generic filesystem errors.
- The recovery dependency is at `vendor/kst-beta-ide@7c9c113` on branch
  `codex/orbot-repository-mode-recovery`. It descends from `6d51479`, not current upstream
  `main`; Git-status/Changes behavior is explicitly excluded.
- A human-gated step requires the human's secret, approval, source material, or operational
  verification. Ask rather than guessing.

## Working method

1. Read the governing docs and inspect both parent and submodule status.
2. Confirm the requested scope against `CURRENT_TASK.md` and the vision.
3. Use real corpus samples for content or retrieval claims.
4. Keep changes bounded to the current roadmap tier; name explicit non-goals.
5. Add deterministic verification before claiming a safety, retrieval, or migration gate.
6. Update `CURRENT_TASK.md` when the active scope or handoff truth changes.

## Still out of scope

Hardware actuation, autonomous safety-critical decisions, custom authentication,
multi-installation tenancy, role-specific experiences, and ticketing integrations are not
MVP requirements unless the roadmap is explicitly revised by the human owner. Vendored
references to cartridges, memory reflection, runtime experiments, or engine forks are not
part of Orbot's current product scope.
