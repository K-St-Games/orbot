---
# ─────────────────────────────────────────────────────────────────────────────
# Puzzle article template  (Orbot canonical service manual)
# Copy this file to hi-orbit-wiki/docs/puzzles/<slug>.md and fill it in.
# Delete the guidance comments (<!-- ... -->) as you complete each part.
# The worked examples predate schema v0.1; use them for article shape only.
# docs/vision/examples/{payphone,lasermaze}-canonical-article.md
# ─────────────────────────────────────────────────────────────────────────────
schema_version: "0.1"
id: puzzle-<slug>                 # stable id, e.g. puzzle-payphone
title: <Puzzle Name>
type: puzzle
room: <room/zone or "unknown">    # mark [gap] if the sources don't say
status: draft                     # draft | current | superseded  (new/edited => draft)
verification_state: unverified    # unverified | source-verified | deployment-verified | disputed
describes_build:
  type: firmware                  # firmware | configuration | mixed | unknown
  version: <version|unknown>
  commit: null                    # commit/hash when known
sources:                          # every source this article is built from
  - id: src-<stable-id>
    name: <file.docx>
    source_role: generated-breakdown  # firmware | generated-breakdown | supporting-reference | draft-intent | observation
    verification_state: unverified    # unverified | source-verified | disputed
    original_path: <drive path/url|unknown>
    checksum: <sha256:...|unknown>
    describes_build: <version/commit|unknown>
    ingested_at: <YYYY-MM-DD|unknown>
    attributed_to: null               # required for an observation
    extraction_warnings: []
depends_on:                       # systems/components this puzzle relies on
  - system-cogs
known_hazards: [unknown]           # inventory only; remove unknown when reviewed
content_class: internal            # internal | public-candidate; NOT access control
content_flags: []                  # e.g. [solution]
section_policies:                  # required for every orbot-section marker below
  operator-summary: {chat_policy: allow, hazards: []}
  operator-player-interaction: {chat_policy: allow, hazards: []}
  operator-healthy-behavior: {chat_policy: allow, hazards: []}
  operator-troubleshooting: {chat_policy: unknown, hazards: []}
  operator-reset-recovery: {chat_policy: unknown, hazards: []}
  operator-escalation: {chat_policy: allow, hazards: []}
  maintenance-mechanism: {chat_policy: allow, hazards: []}
  maintenance-components-wiring: {chat_policy: unknown, hazards: []}
  maintenance-dependencies: {chat_policy: allow, hazards: []}
  maintenance-reference-values: {chat_policy: unknown, hazards: []}
  maintenance-known-quirks: {chat_policy: unknown, hazards: []}
  maintenance-manual-overrides: {chat_policy: escalate, hazards: [unknown]}
  engineering-reference: {chat_policy: unknown, hazards: []}
last_reviewed: null               # set on engineer approval
last_reviewed_by: null
reviewed_against_build: null      # deployed build/configuration if verified
---

# <Puzzle Name>

> **Draft basis tags** (the human-review surface):
> **[source: src-id]** faithfully from a source · **[authored — review]** inferred, needs
> engineer confirmation · **[gap]** not covered by any source · **[hazard: type]** ·
> **[content: solution]**.
>
> Before promotion to `current`, every **[authored — review]** item must be approved,
> revised, or removed. Approved prose relies on the article review metadata; durable
> `[source: src-id]` citations and unresolved `[gap]`/contradiction markers remain.

<!--
SOURCE ROLE IS NOT DEPLOYMENT TRUTH:
  • firmware/source code        = direct description of a particular build.
  • generated-breakdown         = derived explanation of a particular build.
  • supporting-reference        = prose/manual/context; may be unversioned.
  • draft-intent                = proposed change or working note; never shipped truth.
  • observation                 = reported physical behavior; requires reviewer attribution.
A version-stamped source can describe that build without proving it is deployed. Record
conflicts and the article's working treatment; never silently declare them resolved.
-->

## Sources & reconciliation
<!-- Include when a puzzle has multiple or conflicting sources; single-source provenance
     still belongs in frontmatter and Band 3. Classify each source by role and verification,
     then explain the working treatment without claiming deployment truth.
     Put the material conflicts themselves in "Open questions / contradictions". -->

---

## Band 1 — Operator
*Default depth the support agent answers at. Plain language. No line numbers or code.*

<!-- orbot-section: operator-summary -->
### Summary
<!-- 1–2 sentences: what the puzzle is, in operator terms. -->

<!-- orbot-section: operator-player-interaction -->
### What players do
<!-- The intended player interaction, briefly. -->

<!-- orbot-section: operator-healthy-behavior -->
### Healthy behavior — what "working" looks like
<!-- The normal state sequence (from the source's state/flow diagram), phrased so an operator
     can recognise a healthy run. This is the baseline against which faults are judged. -->

<!-- orbot-section: operator-troubleshooting -->
### Troubleshooting
<!-- The highest-value section — usually AUTHORED, since sources rarely provide operator flows.
     Symptom -> likely cause -> operator action -> escalate-if. Tag each row's basis.
     If one row needs a stricter policy than the rest, move it into its own marked subsection;
     the whole retrieval chunk inherits this section's most restrictive policy. -->

| Symptom | Likely cause | Operator action | Escalate if | Basis |
|---|---|---|---|---|
| | | | | |

<!-- orbot-section: operator-reset-recovery -->
### Reset & recovery
<!-- How an operator recovers the puzzle (mid-game and post-win). If the sources don't cover a
     mid-game reset, say so with [gap] — do not invent one. -->

<!-- orbot-section: operator-escalation -->
### When to escalate
<!-- Required (trust contract). When to stop and hand off, and exactly what to include in the
     handoff (which state it reached, what was tried, relevant symptoms). A section policy of
     escalate or unknown prevents the chatbot from walking through that section. -->

---
<!-- ───────────────── depth boundary: operator above · technical below ───────────────── -->

## Band 2 — Maintenance

<!-- orbot-section: maintenance-mechanism -->
### How it works (deeper)
<!-- The mechanism a technician needs: state machine, buffers, chain logic, decoys, etc. -->

<!-- orbot-section: maintenance-components-wiring -->
### Components & wiring
<!-- Hardware table: component | purpose | pin/bus. Flag [hazard: type] parts (lasers, mains, maglocks). -->

| Component | Purpose | Pin/bus |
|---|---|---|
| | | |

<!-- orbot-section: maintenance-dependencies -->
### Dependencies
<!-- External systems/components + links to their articles (e.g. system-cogs), audio/SD assets,
     libraries. Mark links to articles that don't exist yet as [gap]. -->

<!-- orbot-section: maintenance-reference-values -->
### Reference values
<!-- Operational constants a maintainer needs at hand: codes, target angles, timings, thresholds.
     Solution-revealing values are [content: solution]. content_class/flags do not create access control. -->

<!-- orbot-section: maintenance-known-quirks -->
### Known quirks
<!-- Hard-won operational facts, often buried in engineer notes (e.g. "disable serial for live
     shows — LED flicker"). High institutional-memory value. -->

<!-- orbot-section: maintenance-manual-overrides -->
### Manual overrides
<!-- Force-win pins, maintenance modes, etc. Default chat_policy is escalate. Replace unknown
     hazards only after engineering review. [gap] if none documented. -->

---

## Band 3 — Engineering
*Version-fragile — tied to the firmware version in frontmatter; line numbers drift on change.*

<!-- orbot-section: engineering-reference -->

<!-- Tunable-parameter table (setting | line | value | purpose), data formats, debug commands. -->

| Setting | Line | Value | Purpose |
|---|---|---|---|
| | | | |

### Source evidence & provenance
<!-- Where this came from: stable source IDs + roles, described build, closer evidence root
     (often firmware), deployment-verification state, checksums, and extraction warnings. -->

### Open questions / contradictions
<!-- Numbered. Every conflict between sources, every [gap], every value needing engineer
     confirmation. Rank the operator-affecting ones first. This is the engineer's worklist. -->
