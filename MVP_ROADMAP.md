# Orbot MVP Roadmap

**Status:** Draft for owner and engineering-lead review

**Last updated:** 2026-07-12

**Scope:** From the current repository state to dependable Hi-Orbit dogfooding through
Discord and the private `hi-orbit-wiki` knowledge repository

## How to use this roadmap

This is a capability roadmap, not a calendar. Each tier must produce a usable result and
pass its exit gate before the next tier becomes the active implementation task. Dates,
large speculative backlogs, and component loyalty are deliberately excluded.

The roadmap is subordinate to [`docs/vision/VISION.md`](docs/vision/VISION.md). When an
implementation choice conflicts with the vision's trust, safety, or scope-discipline
principles, change the implementation rather than weakening the product contract.

## MVP destination

Orbot reaches MVP when onsite Hi-Orbit staff and the remote engineering team can reliably
use Hermes through the private team Discord to retrieve reviewed, current, cited guidance
from the independently versioned Hi-Orbit knowledge base.

At MVP:

- the private GitHub wiki is useful without the chatbot;
- Hermes/Discord is the primary conversational interface;
- normal answers are grounded in reviewed canonical articles;
- drafts, repair data, and raw evidence do not leak into normal operator guidance;
- hazardous, unknown, unsupported, or contradictory procedures escalate rather than
  inviting improvisation;
- engineers can trace claims to source material and described firmware/builds;
- the system runs on the VPS and remains portable to an onsite host;
- the engineering lead and product owner approve continued internal dogfooding.

The final acceptance criteria may be refined after internal testing with the engineering
lead. MVP does not require a metrics platform or a fixed number of operational incidents.

## Fixed product boundaries

These are product commitments through MVP:

- **Hermes + Discord:** primary support interface.
- **`hi-orbit-wiki`:** private, independently versioned GitHub knowledge repository and
  human-readable service manual.
- **GitHub review:** substantive canonical changes require human approval.
- **Google Drive:** long-term read-only collection point for source material.
- **Canonical-first answers:** reviewed wiki `docs/` content grounds normal chatbot
  guidance.
- **Behavioral safety:** hazardous or unknown procedures escalate rather than instruct.
- **Portable deployment:** VPS versus onsite hosting is an operational choice, not a
  different product architecture.

## Replaceable implementation choices

These are means, not product requirements:

- Cortex, its current database schema, and its current MCP implementation;
- Postgres/pgvector versus another retrieval store;
- vector-only, keyword, or hybrid ranking;
- Ollama or a different embedding provider;
- the exact Markdown validation and ingestion packages;
- MkDocs, the current PoC documentation frontend, or a future replacement.

A replacement must beat the existing option against the roadmap contracts. Do not swap
components merely because another package exists.

## Roadmap summary

| Tier | Capability | User-visible result |
|---|---|---|
| 0 | Governance and contracts | Agents share one product direction, repository boundary, metadata vocabulary, and safety contract. |
| 1 | Payphone knowledge slice | Engineers can review one real, traceable service article in the private wiki. |
| 2 | Discord retrieval PoC | Hermes answers Payphone questions through Discord with citations, refusal, and safety behavior. |
| 3 | Corpus breadth and reconciliation | Draft coverage exists for roughly 12–15 puzzles and 2–3 systems, with engineering feedback and explicit gaps. |
| 4 | Drive-backed maintenance | Source identity, changes, and extraction are repeatable against the real read-only Drive corpus. |
| 5 | MVP dogfooding | Onsite and remote staff can rely on the system for internal testing on the VPS. |

---

## Tier 0 — Governance and contracts

### Outcome

Future implementation agents can work without inheriting the old deployment-only scope or
inventing incompatible metadata and safety behavior.

### Scope

- Approve this roadmap and make it the execution authority beneath the vision.
- Reconcile remaining product-facing framing in `README.md`, `SOUL.md`,
  `architecture.md`, `deployment-plan.md`, and `BUILD-KIT.md` without discarding verified
  operational details.
- Keep reusable Orbot code in the parent repository and installation knowledge in the
  `hi-orbit-wiki` submodule.
- Define metadata schema v0 before changing index or validation code.
- Update the article template and authoring prompt to match the schema.
- Define the exact machine-readable syntax for procedure- or section-level safety.
- Define how draft, current, superseded, disputed, and deployment-verified content move
  through GitHub review.

### Metadata schema v0 must distinguish

- publication lifecycle;
- source role;
- source verification versus deployment verification;
- described firmware/build/commit;
- stable source identity and checksum;
- procedure- or section-level safety classification;
- internal/sensitive content classification;
- canonical article identity and dependencies.

A generated version-stamped breakdown may describe that build accurately. It does not
prove that build is installed. Missing or unknown safety classification fails closed.

### Explicit non-goals

- Retrieval-engine implementation.
- Google Drive automation.
- Custom authentication or roles.
- Finalizing repair/ticket workflow.
- Generating the full article corpus.

### Verification

- `git diff --check` passes.
- Governing docs agree on the current phase and repository names.
- No live plan instructs an agent to execute the historical wiki/Cortex plan verbatim.
- The parent and `hi-orbit-wiki` submodule are clean and correctly linked.
- Metadata examples cover at least: reviewed current content, an unreviewed draft, a
  disputed source, a deployment-unverified build, a hazardous procedure, and an unknown
  safety classification.
- A deterministic validator can distinguish valid and invalid fixtures once the schema is
  implemented.

### Human gate and exit

The owner approves `MVP_ROADMAP.md`. An engineering reviewer agrees that the schema and
safety vocabulary are understandable enough to review real articles. Tier 1 may then
begin.

---

## Tier 1 — Payphone knowledge slice

### Outcome

The private wiki contains one engineer-reviewed, human-readable article created from real
source material with honest provenance and gaps.

### Scope

- Use `example_breakdowns/PayphonePuzzle_Breakdown.docx` as the source sample.
- Preserve minimum provenance: source identity, original filename/path, checksum,
  generated-from-firmware relationship, described firmware v7, extraction warnings, and
  deployment-verification state.
- Revise the Payphone prototype to the approved three-band article format and metadata
  schema.
- Place the proposed article into the `hi-orbit-wiki` review workflow as a draft.
- Have an engineer review the authored operator band, especially troubleshooting,
  reset/recovery, escalation, and any solution values.
- Record gaps and disagreements without filling them speculatively.
- Promote the article to `current` only after explicit approval.
- Add lightweight wiki validators for frontmatter, internal links, and required sections.

### Explicit non-goals

- Discord or Hermes integration.
- Retrieval indexing.
- Automated Drive ingest.
- Repair logging or ticketing.
- Full corpus conversion.
- Automatic canonical publication.

### Verification

- The article renders correctly in private GitHub Markdown.
- Required frontmatter and section metadata validate deterministically.
- Every operational claim is sourced, clearly authored for review, or marked as a gap.
- Source/build identity does not imply that firmware v7 is deployed unless an engineer
  confirms it.
- No unreviewed procedure is marked `current`.
- Broken-link and whitespace checks pass in `hi-orbit-wiki`.

### Human gate and exit

An engineer approves or requests explicit revisions to the Payphone article. Tier 1 exits
only when one reviewed `current` article exists and the team agrees the review surface is
workable.

---

## Tier 2 — Discord retrieval proof of concept

### Outcome

Hermes answers Payphone support questions in a private Discord channel from the reviewed
article, cites it, and safely declines unsupported or hazardous instructions.

### 2A — Retrieval implementation decision

Perform a bounded comparison between the current Cortex code and credible simpler
alternatives. Judge them against these requirements:

- Markdown-first indexing;
- filtering by publication and safety metadata;
- section-level citations;
- deterministic exclusion of drafts and noncanonical material;
- no-result behavior rather than weak guessing;
- Hermes-compatible tool or MCP integration;
- straightforward self-hosting, backup, rebuild, and debugging;
- acceptable latency for a small private corpus.

Hybrid BM25 + vector retrieval is not itself an MVP gate. Retrieval behavior is the gate.
Record the decision and rationale before implementation. If Cortex remains the best fit,
modify it deliberately rather than preserving its current Obsidian/homelab assumptions.

### 2B — Retrieval and Hermes integration

- Index only reviewed `current` canonical documentation for normal support queries.
- Preserve article, section, and source provenance in results.
- Propagate safety classification to retrieval chunks.
- Enforce publication and safety filters across every exposed read tool, not only search.
- Return an explicit no-supported-result response below the chosen confidence threshold.
- Ensure full-document retrieval is not corrupted by chunk overlap.
- Handle deleted, renamed, or superseded articles without leaving stale indexed guidance.
- Wire the retrieval tools into Hermes.
- Run Hermes in the designated private Discord channel with mention-required behavior.
- Use Discord server/channel membership as the initial access boundary; do not build
  custom roles or authentication.

### PoC interaction set

Demonstrate at least:

- a documented Payphone symptom returning concise, cited operator guidance;
- an ambiguous symptom causing a clarifying question;
- a source gap producing escalation rather than invention;
- a hazardous or unknown procedure being withheld;
- an unreviewed draft failing to appear;
- a nonsense or unrelated query producing no supported answer;
- an engineer being able to follow the citation back to the canonical article.

### Repair-data boundary

No repair-log or ticket writeback is required in this PoC. The Discord interaction may
produce an ephemeral or copyable summary, but Orbot must not create a second repair-data
system of record before stakeholder discussions decide whether that truth belongs in
GitHub, ClickUp, or another system.

### Verification

- Local deterministic tests cover filters, citations, safety, drafts, stale deletion,
  no-result behavior, and full-document reconstruction.
- VPS integration proves the selected retrieval service, Hermes, and Discord work
  together after a clean restart.
- Secrets remain outside both repositories.
- Management and retrieval surfaces are not publicly exposed.
- The Payphone interaction set passes with retained logs or screenshots suitable for
  engineering review.

### Human gate and exit

The owner and engineering lead approve the Payphone Discord experience as a useful PoC.
They may refine article structure, response depth, or provisional MVP acceptance criteria
before corpus expansion.

---

## Tier 3 — Corpus breadth and reconciliation

### Outcome

The engineering team can review a draft service-manual corpus broad enough to expose
missing systems, repeated dependencies, contradictory sources, and article-shape problems.

### Scope

- Use Laser Maze first to validate the finalized schema against multiple disagreeing
  sources and draft-intent notes.
- Inventory the available source material by puzzle and cross-cutting system.
- Run a bounded batch authoring pass for approximately 12–15 puzzle articles and 2–3
  system articles.
- Use one article per real subject, not one article per source file.
- Include COGS or the actual room-control system as a cross-cutting system article, while
  preserving its current safety-critical unknowns.
- Generate every article as `draft`; do not bulk-promote generated content.
- Record missing operator procedures, contradictions, extraction damage, source/build
  ambiguity, and safety unknowns in persistent review artifacts.
- Solicit engineering feedback across the batch and revise the template or authoring
  procedure when recurring issues emerge.

The computational cost of generating the batch is expected to be modest. Engineering
review is the scarce resource and should be protected. Review the highest-risk and
highest-value material first: cross-cutting systems, safety questions, reset/recovery,
manual overrides, and common downtime sources.

### Review dispositions

Every generated article receives one explicit disposition:

- approved and promoted to `current`;
- returned for revision;
- blocked by missing evidence or physical verification;
- intentionally deferred.

Only reviewed `current` articles enter normal Discord retrieval. The roadmap does not
require every draft to be approved before learning from the batch.

### Explicit non-goals

- Treating batch generation as batch approval.
- Silently merging contradictory sources.
- Requiring complete documentation of every asset before further dogfooding.
- Automated repair/ticket integration.
- Multi-installation abstractions.

### Verification

- The batch contains the intended puzzle and system coverage or clearly records which
  sources were unavailable.
- Laser Maze preserves the v52 versus draft-intent contradiction rather than merging it.
- Validators pass across all articles.
- No draft is retrievable through the normal support toolchain.
- Engineering feedback is captured as review dispositions and actionable template,
  schema, or content revisions.
- At least one cross-cutting system dependency can be navigated from multiple puzzle
  articles.

### Human gate and exit

The owner and engineering lead agree that the content model scales across the sampled
installation, identify the subset suitable for internal support, and approve the template
for continued use.

---

## Tier 4 — Drive-backed source maintenance

### Outcome

The wiki can be maintained from the actual read-only Google Drive corpus without losing
source identity, silently accepting extraction damage, or building an unnecessary full
source mirror.

### Scope

- Establish least-privilege, read-only Drive access on the VPS.
- Inventory the real folder structure, file formats, source relationships, and update
  patterns.
- Compare the real corpus with the offline sample assumptions.
- Build or adopt only the format handling required by observed files.
- Preserve stable source IDs, checksums, original paths, build relationships, and
  extraction warnings.
- Preserve reviewed image/diagram captions as derived evidence.
- Detect changed, removed, or renamed sources and identify affected canonical articles.
- Decide, from corpus evidence, whether `evidence/` needs richer normalized Markdown or
  whether a thin manifest plus selected derived artifacts is sufficient.
- Choose the simplest justified update trigger: manual, scheduled, or change-driven.

### Explicit non-goals

- Automatic publication of source changes.
- A mandatory one-file-per-source Markdown brain.
- Perfect OCR or diagram interpretation.
- Indexing raw evidence for normal operator answers.

### Verification

- The agent and ingest tooling cannot write to the Drive corpus.
- A representative PDF, Word document, diagram/image, and firmware-derived breakdown
  preserve traceable provenance.
- Known `.docx` ASCII diagram/code damage is detected or explicitly warned about.
- A changed source identifies affected drafts/articles without silently changing
  canonical content.
- Removed or superseded source material does not leave stale operator guidance without a
  visible review requirement.
- A clean rebuild produces the same approved canonical retrieval corpus.

### Human gate and exit

The owner grants Drive access. Engineering reviews representative extraction and caption
quality. The team approves the chosen evidence-layer depth and update trigger.

---

## Tier 5 — Hi-Orbit MVP dogfooding

### Outcome

Onsite Game Masters and remote engineers can use Orbot through the team Discord for
internal operational-support testing with confidence about what it knows, what it cites,
and when it stops.

### Scope

- Deploy the approved wiki checkout, retrieval service, Hermes, and Discord gateway on
  the VPS through a reproducible configuration.
- Keep host-specific paths, credentials, and deployment values outside reusable product
  code.
- Index the engineering-approved canonical subset from Tier 3/4.
- Provide restart, reindex, backup/restore, health, and rollback procedures proportionate
  to a small-team MVP.
- Exercise onsite-operator and remote-engineer support scenarios.
- Resolve high-impact content or retrieval failures found during dogfooding.
- Decide the repair/ticket system of record with stakeholders. Do not add automated
  GitHub or ClickUp writeback unless that decision and a real workflow justify it.
- Update `CURRENT_TASK.md` and active deployment docs to reflect live operating truth.

### MVP acceptance scenarios

- A documented puzzle fault returns accurate, concise, cited guidance.
- A user can navigate from the answer to the private canonical article.
- An unsupported issue says the documentation does not cover it and escalates.
- A hazardous or unknown procedure is withheld even when a semantically similar chunk
  exists.
- A draft, disputed claim, superseded build, repair record, or raw evidence note does not
  appear as settled operator guidance.
- A known source contradiction remains visible to engineers.
- The service recovers after a clean restart and can rebuild its disposable index.
- Onsite and remote users complete representative Discord sessions and consider the
  system useful enough for continued dogfooding.

### Reliability and security gates

- Private Discord/channel access is the only required MVP access boundary.
- Secrets are absent from Git history and runtime logs shown to users.
- Management, database, and retrieval services are private.
- Dependency and model versions are pinned or deliberately recorded.
- Backup and restore protect durable wiki/configuration state; the retrieval index remains
  rebuildable.
- Failure of retrieval or embedding services produces an explicit unavailable/escalate
  response rather than an ungrounded model answer.
- VPS deployment instructions can be adapted to an onsite host without changing the
  knowledge repository or product contracts.

### Final human gate

The product owner and engineering lead review internal testing and decide whether the MVP
is ready for continued use by the Hi-Orbit team. They may amend the final acceptance
criteria based on observed workflows without retroactively weakening safety or canonical
review requirements.

---

## Cross-tier human dependencies

| Dependency | Needed by | Owner action |
|---|---|---|
| Roadmap and schema approval | Tier 0 | Approve priorities, vocabulary, and deferrals. |
| Payphone operational review | Tier 1 | Confirm authored procedures, deployed build, gaps, and safety. |
| Discord bot credentials/channel | Tier 2 | Supply secrets and approve private channel behavior. |
| VPS access and runtime secrets | Tier 2 onward | Provide host access and keep secrets outside Git. |
| Engineering article review | Tier 3 | Triage the batch and approve only supported content. |
| Google Drive read access | Tier 4 | Supply least-privilege credentials and corpus scope. |
| Repair/ticket system decision | Tier 5 or later | Decide whether GitHub, ClickUp, or another system is authoritative. |
| MVP dogfood approval | Tier 5 | Product owner and engineering lead approve continued use. |

## Known risks to manage

- **Engineering review bandwidth:** batch generation is cheap; trustworthy approval is
  not. Preserve explicit review dispositions and prioritize high-risk material.
- **Deployed-version uncertainty:** versioned source documents may not match the physical
  installation. Keep deployment verification separate and visible.
- **Safety metadata leakage:** document-level warnings or prompt-only behavior are
  insufficient. Test chunk/tool enforcement.
- **Source extraction damage:** Word diagrams, code, OCR, and images can lose meaning.
  Preserve originals, warnings, and reviewed derivatives.
- **Retrieval-engine inheritance:** the current Cortex copy contains unrelated paths,
  schema assumptions, and provider settings. Treat it as a candidate, not sunk cost.
- **Stale index state:** deletions, renames, superseded builds, and metadata-only changes
  must reconcile cleanly.
- **Documentation drift:** governing docs, runtime truth, and status handoffs must evolve
  together.
- **Writeback scope creep:** do not build repair/ticket synchronization before the system
  of record and stakeholder workflow are known.

## Post-MVP / stretch backlog

Consider these only when observed demand justifies them:

- ClickUp MCP or another repair/ticket integration after a system-of-record decision;
- role-aware answer depth or content restrictions;
- private hosted documentation with search and mobile optimization;
- automated low-risk documentation maintenance;
- richer source-drift and documentation-health automation;
- downtime, deflection, and support-quality measurement;
- hybrid retrieval if evaluation shows vector or keyword search alone is insufficient;
- repeated deployment tooling for a second installation;
- multi-installation administration;
- broader operational-knowledge productization beyond immersive experiences.

## Next action after roadmap approval

Update `CURRENT_TASK.md` to Tier 0, finish the metadata and safety contracts, reconcile the
remaining governing deployment docs, and produce the first bounded implementation task.
Do not begin by bulk-editing Cortex or batch-generating articles before Tier 0 exits.
