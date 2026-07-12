# Current Task

**Status:** In progress — review and approve the MVP roadmap

**Last updated:** 2026-07-12

**Owner:** Human owner and engineering lead, with the next agent applying review feedback

## Objective

Review and approve root [`MVP_ROADMAP.md`](MVP_ROADMAP.md). Apply owner and engineering-lead
feedback before implementation begins, then set Tier 0 as the active bounded task.

Do not begin the existing wiki/Cortex implementation plan unchanged. Its product direction
is useful, but the live-repo review identified contract, migration, path, and verification
issues that must be accounted for in the roadmap and the next implementation slice.

## Current deliverables

- [x] Draft and receive owner approval in direction for
  [`docs/vision/VISION.md`](docs/vision/VISION.md).
- [x] Ground the content model with real corpus samples, article prototypes, and
  [`docs/vision/VISION_FEEDBACK.md`](docs/vision/VISION_FEEDBACK.md).
- [x] Reconcile the vision with the owner feedback and architecture review.
- [x] Rewrite root [`AGENTS.md`](AGENTS.md) for the current product phase.
- [x] Establish [`hi-orbit-wiki/`](hi-orbit-wiki/) as the independently versioned
  installation-knowledge submodule.
- [x] Normalize the wiki repository name to `hi-orbit-wiki`.
- [x] Draft root [`MVP_ROADMAP.md`](MVP_ROADMAP.md) from the approved vision and owner
  clarifications.
- [ ] Human owner and engineering lead review and approve or revise the roadmap.
- [ ] Schedule remaining README, SOUL, architecture, deployment-plan, and build-kit
  reconciliation in the appropriate roadmap tier.
- [ ] Select and write the first bounded implementation task.

## Product decisions established

- Orbot is a reusable operational-knowledge product; Hi-Orbit is its first proving
  deployment.
- Primary users are the original engineering team, nontechnical Game Masters, and
  occasional maintenance subcontractors.
- The top outcome is reducing original-engineer involvement in routine break/fix work,
  followed by faster repair and preservation of institutional knowledge.
- Discord is the primary MVP interface.
- A private GitHub repository is an acceptable initial human documentation interface;
  custom documentation authentication is not an MVP requirement.
- Google Drive is the long-term read-only corpus collection point; firmware or other
  source systems may be the closer evidence root for derived documents.
- Canonical documentation, normalized evidence, repair history, drafts, and governance
  state remain distinct.
- Canonical `docs/` is the primary operator-facing retrieval source. A comprehensive
  normalized evidence mirror or evidence-search tier is deferred until the real Drive
  corpus is inspected.
- Minimum source identity and provenance are required even when rich evidence
  normalization is deferred.
- Source role, publication lifecycle, deployment verification, safety classification,
  and content classification are separate metadata concepts.
- Safety is behavioral for MVP: hazardous or unknown procedures remain human-readable in
  the private repository but the chatbot escalates rather than instructs.
- Orbot can prepare draft changes or pull requests; engineers review substantive changes.
- Role-specific experiences and content gates are deferred until usage demonstrates a
  need, while the architecture should preserve a path to add them.
- The runtime may live on a VPS or onsite host; host location should not define the
  product architecture.
- MVP means reliable use by both onsite hourly staff and remote engineers through the
  Hi-Orbit team Discord.
- Complexity should be driven by observed friction, not speculative product requirements.
- Canonical articles use operator, maintenance, and engineering depth bands in one
  article; the authored operator band is the primary human-review surface.
- Repair/ticket writeback is not part of the PoC. Stakeholders must choose a single system
  of record, potentially ClickUp, before Orbot writes repair data anywhere automatically.

## Intended repository boundary

Reusable Orbot code and deployment tooling remain in this repository. Hi-Orbit knowledge
belongs in an independently versioned private repository. Installation-specific runtime
configuration should become isolated under a boundary such as `deployments/hi-orbit/`
without requiring an immediate large-scale repo rewrite.

The knowledge repository is expected to contain:

```text
docs/       canonical service manual
evidence/   normalized source evidence
repairs/    incident and resolution records
drafts/     proposed documentation changes
meta/       contradictions, questions, and ingestion state
```

## First product proof

Use Payphone to prove the complete loop from source material to minimum provenance,
reviewed canonical documentation, cited Discord troubleshooting, behavioral safety,
and escalation. Follow with Laser Maze as the multi-source conflict and contradiction
stress test. No repair-log activity is required in this PoC.

Real source samples and draft Payphone, Laser Maze, and COGS articles now exist. They
validate the content shape but are not completed vertical slices: they remain unreviewed
and have not passed through the wiki, retrieval, Discord, and repair-feedback loop.

## Required roadmap shape

The roadmap should use capability tiers with exit gates rather than speculative dates.
Start from this progression and adjust during drafting:

1. Governance and metadata/safety contracts.
2. Payphone human-readable knowledge slice.
3. Payphone Discord retrieval proof of concept.
4. Batch drafts for roughly 12–15 puzzles and 2–3 systems, led by Laser Maze.
5. Drive-backed source maintenance.
6. VPS-based Hi-Orbit MVP dogfooding.

Every tier should identify:

- the user-visible outcome;
- scope and explicit non-goals;
- implementation dependencies;
- human decisions or source material required;
- deterministic verification;
- real-world acceptance evidence;
- the gate for proceeding to the next tier.

## Live repo truth relevant to the next agent

- The live Google Drive corpus is not mounted in this checkout. Five real offline source
  samples are available under `example_breakdowns/`; do not mistake them for the
  operational corpus or invent missing facts.
- `hi-orbit-wiki/` is the installation-knowledge submodule. Commit its content inside the
  child repository, then update the parent gitlink deliberately.
- `cortex/` is a vendored, project-specific starting point that is not yet aligned with
  the Orbot vision.
- `single-compose/hermes-agent/` and `single-compose/bot_memory/` are intentionally absent
  or ignored runtime dependencies in this checkout.
- Docker is not installed in the current development environment, so compose-level
  verification requires another host or environment.
- The GitHub CLI is installed, but its current authentication is invalid.
- Root `AGENTS.md` now reflects the approved product phase. README, SOUL, architecture,
  deployment-plan, and BUILD-KIT still contain older deployment-only framing and should be
  reconciled in the roadmap before they are treated as current product authority.

## Findings the roadmap must absorb

The existing [`docs/orbot-llm-wiki-implementation-plan.md`](docs/orbot-llm-wiki-implementation-plan.md)
should not be executed verbatim. At minimum, later implementation planning must address:

- one coherent metadata vocabulary for lifecycle, verification, audience, knowledge tier,
  and retrieval exclusion;
- source authority that distinguishes a version-stamped description from an
  engineer-confirmed deployed build;
- machine-readable procedure- or section-level safety metadata propagated to chunks,
  with missing or unknown classifications failing closed;
- consistent safety filtering across every exposed retrieval tool;
- database migration or intentional rebuild behavior when embedding dimensions change;
- namespaced document identity, deletion reconciliation, and stale-index prevention;
- the gap between the promised hybrid/canonical-first retrieval model and current
  vector-only code;
- chunk overlap without corrupting full-document retrieval;
- correct sibling/submodule paths and durable Hermes configuration provisioning;
- deterministic automated tests rather than relying on random synthetic embeddings;
- explicit Ollama readiness and model-warmup ordering;
- reproducible MkDocs dependencies and strict documentation validation.

Some of these belong to later hardening tiers. The roadmap should place them deliberately
rather than allowing the MVP to claim safety or completeness that has not been verified.

## Files to read, in order

1. [`docs/vision/VISION.md`](docs/vision/VISION.md) — approved product north star.
2. [`docs/vision/VISION_FEEDBACK.md`](docs/vision/VISION_FEEDBACK.md) — owner refinements
   and real-corpus findings already reconciled into the vision.
3. [`CURRENT_TASK.md`](CURRENT_TASK.md) — this active handoff.
4. [`docs/orbot-llm-wiki-product-proposal.md`](docs/orbot-llm-wiki-product-proposal.md) —
   detailed knowledge-system proposal; supporting material, not final authority.
5. [`docs/orbot-llm-wiki-implementation-plan.md`](docs/orbot-llm-wiki-implementation-plan.md)
   — earlier implementation plan requiring revision.
6. [`architecture.md`](architecture.md), [`deployment-plan.md`](deployment-plan.md), and
   [`BUILD-KIT.md`](BUILD-KIT.md) — current deployment truth that must be reconciled with
   the product roadmap.

## Immediate next action

Review root `MVP_ROADMAP.md`. Do not begin implementation until the owner and engineering
lead approve its placement of content authoring, retrieval selection, Drive integration,
Hermes, safety, migration, and dogfood gates.
