# Vision Feedback — Owner Review

**Date:** 2026-07-12
**For:** the agent maintaining Orbot's vision and authoring `ROADMAP.md`
**From:** human owner review session
**Re:** [`VISION.md`](VISION.md) and [`../../CURRENT_TASK.md`](../../CURRENT_TASK.md)

## Status

The vision is **approved in direction** — no part was rejected. The owner engaged with
product identity, the evidence/retrieval model, the safety model, and the Discord role.
This review produced **confirmations, refinements, and newly-surfaced corpus realities**
to fold into `ROADMAP.md` and the doc reconciliation, plus two concrete artifacts to
ground the first vertical slice (real corpus samples + a prototype canonical article).

## Decisions confirmed / refined

### 1. Full docs rewrite is a roadmap item
- `README.md`, `AGENTS.md`, and `SOUL.md` still describe the older "single operator-support
  chatbot pilot" and now **contradict** the vision.
- **`AGENTS.md` is the highest-priority rewrite** — it is the first thing any agent reads
  and currently instructs agents "you are a deployment agent, this is ops not design,"
  actively pulling work back toward the old product.
- Roadmap action: schedule this in Tier 1 (foundations/trust). `AGENTS.md` leads; README/SOUL follow.

### 2. Canonical-first retrieval; evidence-layer robustness deliberately deferred
- **Canonical `docs/` is the retrieval center and the priority** — confirmed, and
  consistent with the vision's own "retrieval over current canonical knowledge."
- **Do not build a full source-shaped "brain."** Indexing a source mirror alongside
  canonical re-introduces the duplication + drift the owner wants to avoid and muddies
  citations.
- **Evidence-folder robustness is an intentionally open decision**, deferred until GDrive
  access is dialed in and the real source structure is visible. If the source docs "leave
  something to be desired," a more robust normalized `evidence/` layer may be warranted.
- **New wrinkle from the samples:** the `*_Breakdown.docx` files are **themselves generated
  from the puzzle firmware** — the true evidence root is the code, and these docs are
  already a derived explainer layer. Factor this into the eventual evidence decision.
- Regardless of how thin `evidence/` stays, **reviewed image/diagram captions likely must
  persist** (an LLM caption is an inference; the trust contract says label until reviewed).
- Roadmap action: state canonical-first as an architecture decision; **gate the
  evidence-robustness decision on real GDrive access** rather than settling it now.

### 3. Safety is behavioral, not access-control (for MVP)
- **Role-based access is deferred** ("down the road").
- Safety is enforced by **agent behavior**: the chatbot is **hands-off with anything
  flagged as a hazard** — it escalates rather than instructs.
- Hazard-flagged content is **not hidden from humans**; it stays fully readable in the
  GitHub repo (engineers/maintenance use it there). Only the chatbot declines to walk an
  operator through it.
- Content-model implication: canonical articles carry a lightweight **`safety_class`** label
  per procedure. This is *content metadata that drives chatbot behavior*, **not** human
  access control.
- Owner's framing: an expensive mixing-console service manual — engineers can open the
  cabinet, but don't go under the hood without approval. Caveat folded in: because the bot
  is *active* and proactively surfaces procedures, the escalate-don't-instruct behavior is
  the one safety mechanism the MVP cannot defer.

### 4. Discord/Hermes is the primary surfacing interface — and must feed the repo
- Confirmed: relieving the lead engineering team by surfacing knowledge through Discord is
  still a core outcome. Discord/Hermes is important, not deprecated.
- Reconciliation with the "repo is the product" thesis: *what* the product is (maintained
  knowledge) vs *how* it is reached (Discord) are compatible.
- **Rule to encode:** the Discord loop must **feed the repo** — each resolved thread leaves
  a repair-log entry and, where it exposes a doc gap, a draft canonical improvement. A
  well-answered question that leaves nothing behind is the failure mode that collapses
  Orbot back into "just a chatbot." (Matches the vision's vertical-slice steps 7–8.)

## Canonical article shape (agreed)

Three depth bands in one article ("different depths, not different documents"), operator-first:

- **Operator band** (agent's default answer depth): Summary · What players do · Healthy
  behavior (normal state sequence) · Troubleshooting (symptom → check → fix/escalate) ·
  Reset & recovery · **When to escalate**
- **Maintenance band:** How it works (deeper) · Components & wiring · Dependencies
  (→ system articles like COGS) · **Reference values** (codes/angles — `sensitivity`-flagged)
  · Known quirks · Manual overrides (`safety_class`-flagged)
- **Engineering band:** Tunables + line numbers · Data formats · Source evidence &
  provenance · Open questions / contradictions

Additions vs. the proposal §9 template: an explicit **"When to escalate"** section
(trust-contract mandated) and a **"Reference values"** section, plus an explicit
operator/technical **depth boundary**. Frontmatter carries provenance
(`describes_firmware`, `source_documents`), `status`, and per-section
`safety_class`/`sensitivity`.

**Key realization:** the article's highest-value sections (troubleshooting, reset,
escalation) are **authored, not extracted** — the sources barely contain them. That
authored operator layer is precisely where the **human review gate** does its work.

## Corpus realities the roadmap must absorb

From five real samples now committed under [`../../example_breakdowns/`](../../example_breakdowns/):

- **Sources are engineer-shaped** (pin maps, line numbers, tunables). The operator layer
  must be authored, not just reformatted.
- **Multiple docs per system, at different altitudes, possibly inconsistent** — the Laser
  Maze appears in three files, one of which (`Vibe_Coding_Notes.docx`) is raw change-intent,
  not verified shipped behavior. The agent must **classify draft vs canonical and surface
  contradictions**, never silently merge.
- **COGS is a cross-cutting system** referenced by every puzzle → validates **system/component
  articles** over 1:1 file mirroring.
- **Version-fragility is structural** (pin maps/line numbers pinned to firmware builds) →
  provenance + **staleness triggers** are not optional.
- Practical note: naive `.docx` text extraction **mangles ASCII state diagrams and code
  blocks** — a data point for the deferred evidence-robustness decision.

## First vertical slice

- **Payphone first** to define/validate the shape — a prototype draft now exists at
  [`examples/payphone-canonical-article.md`](examples/payphone-canonical-article.md),
  authored from the real v7 breakdown with the operator layer inferred and gaps flagged.
- **Laser Maze second** as the reconciliation stress test (three overlapping sources).
- Real source samples for both are in `example_breakdowns/`.

## Artifacts produced this session

- `example_breakdowns/` — five real corpus samples + README (reference material; **not** the
  operational corpus).
- `docs/vision/examples/payphone-canonical-article.md` — prototype canonical article.
- This feedback doc.

## Suggested roadmap deltas vs. the current draft

1. Put the **`AGENTS.md`/README/SOUL rewrite** explicitly in Tier 1.
2. State **canonical-first retrieval** as an architecture decision; mark **evidence-layer
   robustness as an open decision gated on GDrive access**.
3. Encode the **`safety_class` behavioral gate** (escalate-don't-instruct) as an MVP
   requirement; keep **role-based access as post-MVP**.
4. Make **"Discord loop feeds the repo"** an explicit MVP acceptance criterion (repair-log
   entry + draft improvement per resolved thread).
5. Adopt the **three-band canonical article shape** as the content model; treat the
   **authored operator layer as the primary human-review surface**.
6. Sequence the vertical slice **Payphone → Laser Maze**.
