---
# ─────────────────────────────────────────────────────────────────────────────
# Puzzle article template  (Orbot canonical service manual)
# Copy this file to orbot-wiki/docs/puzzles/<slug>.md and fill it in.
# Delete the guidance comments (<!-- ... -->) as you complete each part.
# Two worked examples: docs/vision/examples/{payphone,lasermaze}-canonical-article.md
# ─────────────────────────────────────────────────────────────────────────────
id: puzzle-<slug>                 # stable id, e.g. puzzle-payphone
title: <Puzzle Name>
type: puzzle
room: <room/zone or "unknown">    # mark [gap] if the sources don't say
status: draft                     # draft | current | superseded  (new/edited => draft)
describes_firmware: <version>     # the firmware build this article describes
source_documents:                 # every source this article is built from
  - name: <file.docx>
    tier: current                 # current | supporting | draft-intent  (see rules below)
    firmware: <version|unknown>
depends_on:                       # systems/components this puzzle relies on
  - system-cogs
safety_class: low                 # low | elevated | high  — drives escalate-don't-instruct
sensitivity: internal             # internal | public — internal hides solution values from players
last_reviewed: null               # set on engineer approval
last_reviewed_by: null
---

# <Puzzle Name>

> **Basis tags** (keep them — they are the human-review surface):
> **[source <ver>]** faithfully from a source · **[authored — review]** inferred, needs
> engineer confirmation · **[gap]** not covered by any source · **[sensitive]** / **[safety]**.

<!--
SOURCE TIERS — how to classify each source_document, and which wins on conflict:
  • current      = generated-from-firmware / version-stamped / engineer-confirmed. Wins.
  • supporting   = prose explainers, manuals, notes that add context. Use, but flag divergence.
  • draft-intent = change requests, "vibe" notes, proposals. NEVER treated as shipped truth.
NEVER silently resolve a conflict between tiers — record it under "Open questions".
-->

## Sources & reconciliation
<!-- Include ONLY when a puzzle has multiple or conflicting sources; omit for one clean source.
     A short table classifying each source by tier + one line on how conflicts were resolved.
     Put the material conflicts themselves in "Open questions / contradictions". -->

---

## Band 1 — Operator
*Default depth the support agent answers at. Plain language. No line numbers or code.*

### Summary
<!-- 1–2 sentences: what the puzzle is, in operator terms. -->

### What players do
<!-- The intended player interaction, briefly. -->

### Healthy behavior — what "working" looks like
<!-- The normal state sequence (from the source's state/flow diagram), phrased so an operator
     can recognise a healthy run. This is the baseline against which faults are judged. -->

### Troubleshooting
<!-- The highest-value section — usually AUTHORED, since sources rarely provide operator flows.
     Symptom -> likely cause -> operator action -> escalate-if. Tag each row's basis. -->

| Symptom | Likely cause | Operator action | Escalate if | Basis |
|---|---|---|---|---|
| | | | | |

### Reset & recovery
<!-- How an operator recovers the puzzle (mid-game and post-win). If the sources don't cover a
     mid-game reset, say so with [gap] — do not invent one. -->

### When to escalate
<!-- Required (trust contract). When to stop and hand off, and exactly what to include in the
     handoff (which state it reached, what was tried, relevant symptoms). Anything safety_class
     flagged escalates rather than being walked through. -->

---
<!-- ───────────────── depth boundary: operator above · technical below ───────────────── -->

## Band 2 — Maintenance

### How it works (deeper)
<!-- The mechanism a technician needs: state machine, buffers, chain logic, decoys, etc. -->

### Components & wiring
<!-- Hardware table: component | purpose | pin/bus. Flag [safety] parts (lasers, mains, maglocks). -->

| Component | Purpose | Pin/bus |
|---|---|---|
| | | |

### Dependencies
<!-- External systems/components + links to their articles (e.g. system-cogs), audio/SD assets,
     libraries. Mark links to articles that don't exist yet as [gap]. -->

### Reference values
<!-- Operational constants a maintainer needs at hand: codes, target angles, timings, thresholds.
     Solution-revealing values are [sensitive]. -->

### Known quirks
<!-- Hard-won operational facts, often buried in engineer notes (e.g. "disable serial for live
     shows — LED flicker"). High institutional-memory value. -->

### Manual overrides
<!-- Force-win pins, maintenance modes, etc. Usually [safety: authorized only]. [gap] if none documented. -->

---

## Band 3 — Engineering
*Version-fragile — tied to the firmware version in frontmatter; line numbers drift on change.*

<!-- Tunable-parameter table (setting | line | value | purpose), data formats, debug commands. -->

| Setting | Line | Value | Purpose |
|---|---|---|---|
| | | | |

### Source evidence & provenance
<!-- Where this came from: source docs + tiers, firmware version, the closer-to-truth root
     (usually the .ino firmware), and any extraction warnings. -->

### Open questions / contradictions
<!-- Numbered. Every conflict between sources, every [gap], every value needing engineer
     confirmation. Rank the operator-affecting ones first. This is the engineer's worklist. -->
