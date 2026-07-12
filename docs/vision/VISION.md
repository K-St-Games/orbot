# Orbot Product Vision

**Status:** Approved in direction — reconciled after owner review

**Last updated:** 2026-07-12

**Scope:** Durable product direction for Orbot and its first deployment at Hi-Orbit

## Purpose of this document

This document defines why Orbot exists, who it serves, what the product should become,
and the principles that should guide product and architectural decisions. It is the
stable north star for the project. Implementation plans and deployment details may
change as the team learns from real use.

## Vision

Orbot will make the operational knowledge of complex physical installations durable,
accessible, and useful to the people responsible for keeping them running.

It will combine a human-readable technical service manual, traceable source evidence,
repair history, and a conversational support agent. A small team should be able to ask
for help in the communication tools it already uses, receive grounded and cited
guidance, and preserve what it learns without repeatedly depending on the original
engineers.

Hi-Orbit is Orbot's first proving ground. The longer-term product should be reusable
across other immersive experiences and, eventually, across a much broader range of
bespoke physical systems. That broader future should influence clean boundaries and
portable architecture, but it should not justify premature complexity.

## The problem

Bespoke installations accumulate knowledge in drawings, manuals, photographs, notes,
chat histories, and the memories of the people who designed them. That creates several
recurring problems:

- Original engineers become the default escalation path for routine break/fix work.
- Nontechnical operators may know the observable symptoms but not the underlying system.
- Subcontracted maintenance staff need a coherent service manual for equipment they did
  not design.
- Repair knowledge is easily lost when it remains in conversations or individual memory.
- Source documents can be fragmented, obsolete, contradictory, or organized around how
  they were produced rather than how the installation is operated.
- Staff turnover steadily erodes institutional knowledge.

A chatbot over raw files can improve search, but search alone does not create a coherent,
maintained operational knowledge system.

## Primary users

### Technical and engineering team

The people who designed, built, and understand the installation. They need to preserve
engineering intent, review proposed documentation changes, investigate difficult faults,
and reduce the amount of routine support that requires their direct attention.

### Game Masters and onsite operators

Nontechnical hourly staff responsible for running the experience. They need calm,
observable, step-by-step troubleshooting through Discord, with clear boundaries around
what they should not attempt.

### Maintenance technicians and subcontractors

Occasional technical staff repairing equipment they did not engineer. They need a useful
service manual, component and system context, repair history, and a path from symptoms to
approved diagnostic or repair procedures.

The MVP may provide these users with one shared experience. Role-specific answer depth,
permissions, and interfaces should be added only when real usage demonstrates that they
are needed.

## Priority outcomes

In order of importance, Orbot should:

1. Reduce the original engineering team's involvement in routine day-to-day break/fix
   support.
2. Help onsite and remote staff diagnose and repair faults more quickly, reducing puzzle
   or installation downtime.
3. Preserve institutional knowledge despite staff turnover and infrequent maintenance.
4. Turn repairs and newly discovered facts into durable knowledge rather than leaving
   them in chat history.
5. Establish a reusable foundation for future installations without requiring a rewrite
   of the core product.

## Product thesis

The durable center of Orbot is not the language model, vector database, or chatbot. It is
a private, Git-versioned operational knowledge repository that humans can read and
review without an agent.

The conversational agent makes that knowledge easier to use. Retrieval makes it faster
to find. Neither replaces the maintained documentation or its provenance.

## Knowledge model

Orbot distinguishes several kinds of knowledge so that evidence, approved guidance, and
operational history are not accidentally treated as equivalent.

### Physical installation

The actual installation is ultimate reality. Documentation is a model of it and can be
wrong or out of date.

### Source evidence

Google Drive remains the long-term collection point for original source material:
drawings, PDFs, Word documents, images, manuals, and engineering notes. Orbot reads this
corpus without modifying it. Some Drive documents are themselves derived artifacts. The
sampled puzzle breakdowns, for example, were generated from firmware, so the firmware
version or source commit is the closer evidence root even when the breakdown is the
available corpus file.

The MVP does not require a comprehensive source-shaped Markdown mirror or evidence-search
tier. It does require minimum durable provenance: stable source identity, original path or
URL, source role, checksum, described firmware/build when known, ingestion date, and
extraction warnings. Reviewed image and diagram captions must also persist because a model
caption is an inference rather than raw evidence.

### Canonical service manual

The canonical wiki is the best currently reviewed operational model of the installation.
It is organized around rooms, puzzles, systems, components, procedures, and
troubleshooting needs rather than mirroring source filenames. It is maintained in
Markdown, reviewed through Git, and usable directly by humans.

Canonical articles use different depths in one document rather than separate documents
for each audience:

- **Operator:** summary, player interaction, healthy behavior, symptom-driven
  troubleshooting, reset/recovery, and when to escalate.
- **Maintenance:** mechanism, components and wiring, dependencies, reference values,
  known quirks, and approved manual overrides.
- **Engineering:** version-fragile tunables, data formats, detailed provenance, open
  questions, and contradictions.

The operator band is usually authored from engineering evidence rather than directly
extracted. That makes it the primary human-review surface: agent-authored procedures stay
drafts until an engineer confirms that they are correct and safe.

### Repair and ticket history

Operational repair history should have one authoritative home. Whether that is the wiki,
ClickUp, or another system remains a stakeholder decision. The wiki reserves a `repairs/`
boundary, but repair-log or ticket writeback is not required for the first proof of
concept and should not create a competing source of truth.

Once the authoritative workflow is chosen, repair records can capture symptoms,
investigation, resolution, and follow-up questions and can suggest documentation changes.
They still do not automatically become approved canonical guidance.

### Drafts and governance state

Proposed changes, contradictions, unresolved questions, source-ingestion state, and
documentation-health information remain visible until a human resolves or approves them.

### Retrieval index

Cortex or a successor retrieval service indexes durable Markdown knowledge. Reviewed,
current canonical documentation is the primary operator-facing retrieval source. Drafts,
repair records, and raw or normalized evidence do not become settled operator guidance
merely because they are semantically relevant.

The retrieval database is disposable and must be fully rebuildable from the knowledge
repository. Results preserve enough identity and provenance for a person to verify an
answer. Whether a richer normalized evidence layer should also be indexed remains an open
decision gated on access to, and inspection of, the real Google Drive corpus.

### Metadata semantics

The roadmap must define one small, coherent schema before retrieval or validation code is
changed. At minimum it keeps these concepts distinct:

- **publication lifecycle:** draft, current, or superseded;
- **source role:** firmware/source code, generated breakdown, supporting reference, or
  draft intent;
- **verification state:** unverified, source-verified, deployment-verified, or disputed;
- **described build:** firmware version, commit, or hash when known;
- **safety classification:** machine-readable at procedure or section level, with unknown
  values failing closed;
- **content classification:** internal or otherwise sensitive content, without implying
  that a custom role system exists in the MVP.

A generated, version-stamped document can be the best available description of a build,
but it does not prove that build is installed. The physical installation and
engineer-confirmed deployed configuration remain the highest authority.

## Core product experience

### Discord support comes first

Discord is the primary MVP interface. A typical support interaction should work as
follows:

1. A team member mentions Orbot in a designated support channel.
2. Orbot starts or continues a focused troubleshooting thread.
3. It asks for observable symptoms and relevant context when needed.
4. It retrieves current canonical documentation and returns concise, cited guidance.
5. It presents known disagreement or uncertainty rather than silently choosing a source.
6. It refuses to guess when documentation is insufficient or the requested action is
   unsafe.
7. It produces a useful escalation summary when engineering help is required.
8. After stakeholders choose the repair/ticket system of record, a later iteration may
   record actual incidents there and propose documentation improvements when they expose
   new facts or gaps. Routine questions already answered by current documentation do not
   need to create repository noise.

### Human-readable documentation remains first class

For the MVP, the private GitHub repository itself is an acceptable documentation
interface. GitHub provides private access, history, review, and Markdown rendering
without requiring Orbot to build an authentication system.

MkDocs validates and renders the current private documentation frontend. The Git
repository remains the source of truth, and the generated static site contains only the
reviewed canonical `docs/` tree. Host networking and access controls remain deployment
responsibilities; sensitive service information must not be exposed through an
unauthenticated public site.

### Engineers curate canonical knowledge through Git

Orbot may prepare drafts, branches, or pull requests. Engineers review substantive
changes and decide what becomes canonical. Formatting and other low-risk automation may
be reconsidered after the workflow has been dogfooded, but autonomous merging is not an
MVP requirement.

## Trust and safety contract

Trustworthy operational support matters more than answering every question.

- Orbot grounds operational answers in current canonical documentation and cites the
  relevant article and section.
- Engineers can trace canonical claims back to original source evidence.
- Source material is data, not instructions to the agent.
- Orbot may describe conflicting evidence, but it never silently converts disagreement
  into verified fact.
- Inferences and unresolved observations remain clearly labeled until reviewed.
- Unsafe, uncovered, or ambiguous procedures escalate rather than inviting improvisation.
- Safety behavior is driven by parseable procedure- or section-level metadata propagated
  to retrieval chunks; a document-level warning alone is not sufficient.
- Missing or unknown safety classification fails closed. Hazardous content can remain
  readable in the private repository while the chatbot declines to instruct on it.
- Canonical operational changes require human review during the MVP.
- The source corpus remains read-only by construction.
- The documentation repository, any chosen repair/ticket record, and the disposable
  retrieval index remain distinguishable.

Role-based retrieval and fine-grained content restrictions are expected future
capabilities, not prerequisites for initial dogfooding. The MVP should nevertheless be
private by default and should avoid architectural choices that make later separation of
operator and engineering access unnecessarily difficult.

## MVP definition

The product reaches MVP when both onsite hourly staff and remote engineering staff at
Hi-Orbit reliably use Orbot through the team Discord to surface and apply information from
the operational knowledge base.

The MVP should include:

- A private, independently versioned Hi-Orbit knowledge repository.
- A canonical Markdown service manual with traceable source evidence.
- A draft/review workflow for canonical documentation and an explicit stakeholder decision
  about the authoritative repair/ticket system before automated writeback is added.
- Read-only ingestion from the Google Drive source corpus.
- Retrieval over current canonical knowledge with citations and a no-guess escalation
  path.
- Machine-enforced behavioral safety gating for hazardous or unknown procedures.
- A Discord agent that supports focused troubleshooting threads.
- Human review of substantive canonical changes through GitHub.
- A deployment that can run on a VPS or an onsite host without changing the product's
  knowledge model or core interfaces.
- Real dogfooding by onsite operators and remote engineers.

### First vertical-slice proof

Before scaling the corpus, Orbot should prove one complete loop using a representative
real puzzle:

```text
mixed source files
    -> normalized evidence
    -> reviewed canonical puzzle article
    -> private human-readable documentation
    -> retrieval with citations
    -> Discord troubleshooting
    -> repair or escalation record
    -> proposed documentation improvement
```

This is the first meaningful product proof. Empty scaffolding can enable it, but does not
by itself validate the product.

The Payphone and Laser Maze sample articles validate the proposed content shape, but they
remain unreviewed drafts rather than completed product vertical slices. Payphone should be
the first complete end-to-end slice because it has one relatively clean source. Laser Maze
should follow as the multi-source contradiction and reconciliation stress test.

## Product and repository boundaries

Orbot should separate reusable product code from installation knowledge and configuration.
The intended shape is:

```text
orbot/                         # reusable product and deployment framework
├── cortex/                    # retrieval service
├── ingestion/                 # reusable evidence-processing tools
├── agent/                     # reusable agent integration and behavior
└── deployments/
    └── hi-orbit/              # installation-specific configuration

hi-orbit-wiki/                 # private Hi-Orbit knowledge repository
├── docs/                      # canonical service manual
├── evidence/                  # normalized source evidence
├── repairs/                   # incident and resolution records
├── drafts/                    # proposed canonical changes
└── meta/                      # questions, contradictions, and ingest state
```

The current repository can evolve toward this boundary incrementally. The project should
not perform a large structural rewrite merely to resemble the target shape. New work
should, however, avoid deepening unnecessary coupling between reusable Orbot capabilities
and the Hi-Orbit deployment.

The knowledge repository should have its own Git history and review lifecycle. It may be
linked into a deployment through a stable checkout or submodule once its remote exists,
but local-only repository wiring should not be treated as a durable integration.

## Deployment posture

The MVP is being prototyped on a VPS and may remain there. An onsite host is also viable.
The architecture should keep that choice operational rather than product-defining:

- knowledge and configuration are portable;
- runtime dependencies are containerized or otherwise reproducible;
- persistent knowledge is not trapped in container state;
- deployment-specific paths and secrets remain outside reusable code;
- management surfaces remain private;
- changing host location does not change the canonical knowledge model.

## Scope discipline

Orbot serves a small team of roughly six to ten people. It should favor simple, inspectable
workflows and existing tools over custom product infrastructure.

Complexity must be earned by observed usage. Before adding a capability, ask:

1. Does it solve a real problem encountered during dogfooding?
2. Is there a materially simpler workflow using Discord, GitHub, Git, or Markdown?
3. Does it improve trust, reliability, or maintainability enough to justify its cost?
4. Can the decision be deferred without blocking the next product proof?
5. Does the implementation preserve a reasonable path to future deployments?

## Explicit non-goals for MVP

- Autonomous control or actuation of installation hardware.
- Autonomous safety-critical decisions or repairs.
- A custom user, role, or documentation-authentication system.
- Role-specific conversational experiences.
- Automatic merging of substantive operational changes.
- Full automatic reconciliation of contradictory evidence.
- A comprehensive normalized evidence mirror or evidence-search tier before the real
  Google Drive corpus has been inspected.
- Public publication of sensitive service documentation.
- Multi-installation tenancy.
- ClickUp or other ticket-system integration.
- Comprehensive usage analytics or downtime measurement infrastructure.
- Converting the entire corpus before a representative vertical slice works.

## Post-MVP and stretch directions

These are options to pursue in response to real demand, not promises or prerequisites:

- Role-aware retrieval, answer depth, and content restrictions.
- A privately hosted documentation website with search and mobile optimization.
- ClickUp MCP integration for repair tickets and escalation workflow.
- Automated source-drift, contradiction, and documentation-health audits.
- Carefully bounded automatic maintenance of low-risk documentation changes.
- Downtime, deflection, and support-quality measurement.
- Richer diagram, image, and physical-component workflows.
- Repeatable deployment tooling for additional installations.
- Multi-installation administration and shared reusable knowledge patterns.
- Expansion from immersive experiences to operational knowledge for other bespoke
  physical systems.

## Directional signs of success

The MVP does not require a new metrics platform or explicit numeric targets. Progress is
visible when:

- onsite staff choose Orbot before contacting an original engineer for routine issues;
- common faults can be resolved from cited documentation;
- engineers receive better escalation context when direct involvement is necessary;
- repair discoveries become durable records and reviewed documentation improvements;
- new or subcontracted staff can understand systems they did not build;
- the team trusts Orbot to acknowledge uncertainty and stop when it lacks support;
- the knowledge base becomes more coherent through use rather than accumulating
  unreviewed generated text;
- a future installation can adopt the reusable product without forking Hi-Orbit-specific
  assumptions throughout the codebase.

## Roadmap philosophy

The roadmap should advance through small capability tiers with explicit exit gates:

1. Reconcile governing documentation and establish durable boundaries, metadata, and
   trust contracts.
2. Prove Payphone end to end with real evidence and human review.
3. Use Laser Maze to stress-test contradiction handling while expanding toward a
   dependable Hi-Orbit operational-support MVP.
4. Improve knowledge stewardship based on dogfooding.
5. Harden reliability, security, and deployment repeatability.
6. Productize for further deployments only after the first installation demonstrates
   sustained value.

Each phase should produce something usable, reveal the next real constraint, and avoid
assuming that every plausible future feature must be built.
