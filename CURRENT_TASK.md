# Current Task

**Status:** In progress — vision review and roadmap preparation

**Last updated:** 2026-07-11

**Owner:** Next available project agent, with human review at the vision gate

## Objective

Establish a durable product direction for Orbot, confirm it with the human owner, and use
that approved vision to create a phased `ROADMAP.md` with explicit capability and
verification gates.

Do not begin the existing wiki/Cortex implementation plan unchanged. Its product direction
is useful, but the live-repo review identified contract, migration, path, and verification
issues that must be accounted for in the roadmap and the next implementation slice.

## Current deliverables

- [x] Draft [`docs/vision/VISION.md`](docs/vision/VISION.md).
- [x] Create this handoff document.
- [ ] Human reviews and approves or revises the vision.
- [ ] Create root `ROADMAP.md` from the approved vision.
- [ ] Reconcile older planning and deployment docs with the approved roadmap.
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
- Google Drive is the long-term read-only source-evidence system.
- Canonical documentation, normalized evidence, repair history, drafts, and governance
  state remain distinct.
- Orbot can prepare draft changes or pull requests; engineers review substantive changes.
- Role-specific experiences and content gates are deferred until usage demonstrates a
  need, while the architecture should preserve a path to add them.
- The runtime may live on a VPS or onsite host; host location should not define the
  product architecture.
- MVP means reliable use by both onsite hourly staff and remote engineers through the
  Hi-Orbit team Discord.
- Complexity should be driven by observed friction, not speculative product requirements.

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

Use one representative real puzzle to prove the complete loop from mixed source files to
normalized evidence, reviewed canonical documentation, cited Discord troubleshooting,
and a repair or escalation record. The human owner expects to provide offline copies of
key source files soon.

Empty repository scaffolding is enabling work, not proof that the product works.

## Required roadmap shape

The roadmap should use capability tiers with exit gates rather than speculative dates.
Start from this progression and adjust during drafting:

1. Foundations and trust contracts.
2. One-puzzle vertical-slice proof of concept.
3. Hi-Orbit operational-support MVP.
4. Knowledge-stewardship workflows informed by dogfooding.
5. Reliability, security, and deployment hardening.
6. Repeatable deployment and broader productization.
7. Demand-driven stretch capabilities.

Every tier should identify:

- the user-visible outcome;
- scope and explicit non-goals;
- implementation dependencies;
- human decisions or source material required;
- deterministic verification;
- real-world acceptance evidence;
- the gate for proceeding to the next tier.

## Live repo truth relevant to the next agent

- The Google Drive corpus is not available in this checkout; do not invent operational
  content.
- `cortex/` is a vendored, project-specific starting point that is not yet aligned with
  the Orbot vision.
- `single-compose/hermes-agent/` and `single-compose/bot_memory/` are intentionally absent
  or ignored runtime dependencies in this checkout.
- Docker is not installed in the current development environment, so compose-level
  verification requires another host or environment.
- The GitHub CLI is installed, but its current authentication is invalid.
- The current root instructions and build docs disagree about whether Cortex hardening is
  part of the immediate phase. Reconcile them before implementation.

## Findings the roadmap must absorb

The existing [`docs/orbot-llm-wiki-implementation-plan.md`](docs/orbot-llm-wiki-implementation-plan.md)
should not be executed verbatim. At minimum, later implementation planning must address:

- one coherent metadata vocabulary for lifecycle, verification, audience, knowledge tier,
  and retrieval exclusion;
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

1. [`docs/vision/VISION.md`](docs/vision/VISION.md) — draft product north star.
2. [`CURRENT_TASK.md`](CURRENT_TASK.md) — this active handoff.
3. [`docs/orbot-llm-wiki-product-proposal.md`](docs/orbot-llm-wiki-product-proposal.md) —
   detailed knowledge-system proposal; supporting material, not final authority.
4. [`docs/orbot-llm-wiki-implementation-plan.md`](docs/orbot-llm-wiki-implementation-plan.md)
   — earlier implementation plan requiring revision.
5. [`architecture.md`](architecture.md), [`deployment-plan.md`](deployment-plan.md), and
   [`BUILD-KIT.md`](BUILD-KIT.md) — current deployment truth that must be reconciled with
   the product roadmap.

## Immediate next action

Ask the human owner to review `docs/vision/VISION.md`, focusing on product identity, MVP
boundary, repository separation, trust model, and explicit non-goals. Incorporate that
feedback before authoring `ROADMAP.md`.
