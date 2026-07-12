---
id: system-cogs
title: COGS (room control system)
type: system
room: whole-installation
status: draft                     # prototype shape example; NOT engineer-reviewed
describes_firmware: n/a           # COGS itself is not versioned in the corpus
source_documents:
  # There is NO COGS-native documentation in the sampled corpus. [gap]
  # The integration contract below is reconstructed from the puzzle breakdowns that talk to it:
  - name: BattleshipPuzzle_Breakdown.docx
    tier: current
    firmware: v43
  - name: PayphonePuzzle_Breakdown.docx
    tier: current
    firmware: v7
  - name: LaserMazePuzzle_Breakdown.docx
    tier: current
    firmware: v52
used_by:                          # reverse dependency — who relies on COGS
  - puzzle-battleship
  - puzzle-payphone
  - puzzle-laser-maze
  # ...likely every puzzle in the installation  [authored — review]
safety_class: unknown             # COGS may orchestrate life-safety effects (doors/maglocks) — unconfirmed [safety][gap]
sensitivity: internal
last_reviewed: null
last_reviewed_by: null
---

# COGS (room control system)

> **Prototype canonical article — system type.** In the real wiki this would live at
> `hi-orbit-wiki/docs/systems/cogs.md`. Basis tags: **[source]** from a puzzle breakdown ·
> **[authored — review]** inferred · **[gap]** not in the corpus · **[safety]**.

## Scope of this article  ⚠ read first
This documents the **puzzle ↔ COGS integration contract** — how puzzles are started by, and
report back to, the room controller. That contract is **well-evidenced**: it is visible and
consistent across three independent puzzle firmwares (v7, v43, v52).

**COGS *itself* is not documented in the current corpus.** What the controller is, how it is
configured, how the room is started/reset/monitored through it, and whether it drives any
life-safety hardware are all **[gap]** — see [Open questions](#open-questions--contradictions).
Do not infer COGS-native behaviour from this article; it only describes the wire-level
interface the puzzles reveal.

## What COGS appears to be
**[authored — review]** The sources never define COGS; they only show the pins that talk to
it. From that interface — a central controller that **activates each puzzle** and **listens
for completion signals** — COGS is almost certainly the room's **orchestration controller**:
it sequences the experience, decides when each puzzle is live, and reacts when one is solved.

The interface strongly resembles **"Cogs" by Clockwork Dog**, a widely-used commercial
escape-room control system (control software plus GPIO I/O hardware). The all-caps `COGS`
styling in the code could equally be an in-house controller. **Confirm which**, and link its
configuration / "show file" and vendor documentation as the real evidence root. **[gap]**

---

## Band 1 — Operator

### Summary
COGS is what **runs the room**: it turns each puzzle on at the right time and knows when a
puzzle has been solved so the experience can advance. Operators don't usually touch a puzzle's
COGS wiring, but COGS is the layer that ties the room together. **[authored — review]**

### Troubleshooting (cross-cutting)
These are the room-level symptoms that point at the COGS interface rather than at one puzzle.

| Symptom | Likely locus | Operator action | Escalate if | Basis |
|---|---|---|---|---|
| A puzzle was clearly solved, but the room didn't react | The **completion signal** from that puzzle to COGS | Note which puzzle; check it truly reached its win state | Puzzle wins but COGS never advances | [authored — review] |
| A puzzle never "turned on" when it should have | The **activation signal** from COGS to that puzzle | Confirm the room/COGS reached the point that activates it | COGS should have activated it but the puzzle stayed idle | [authored — review] |
| The whole room won't start / won't reset | **COGS itself** | — (no documented operator control in the corpus) | Any room-wide start/reset failure | [gap] → escalate |

### Operating & resetting the room through COGS
**[gap]** Not documented in the current corpus. How an operator starts, resets, or monitors
the room via COGS is unknown here and must come from the COGS documentation. Until then, treat
room-level start/reset as **escalate**.

### When to escalate
Any room-wide failure (nothing starts, room won't reset), or a puzzle-to-room handoff that
fails despite the puzzle itself behaving normally. Hand off: **which puzzle**, **which
direction failed** (activation in, or completion out), and what the puzzle was doing.
**[authored — review]**

---
<!-- ───────────────── depth boundary: operator above · technical below ───────────────── -->

## Band 2 — Integration contract
*The evidenced core: how a puzzle and COGS talk. Shared across all three sampled puzzles.*

### Activation (COGS → puzzle)
A puzzle idles until COGS **pulls its activation line LOW**; the puzzle then runs. Active-LOW is
explicit for Battleship (`INPUT_PULLUP`, waits for LOW) and Payphone (HIGH = standby, LOW =
active); assumed for Laser Maze. **[source]** *(Laser-Maze polarity: [authored — review])*

### Completion & events (puzzle → COGS)
Puzzles report back by driving a digital line with **pulse trains** (timing where stated:
**~100 ms pulse / 200 ms gap**). **The pulse-count meaning is per-puzzle, not a shared
vocabulary** — e.g. "3 pulses" means *round win* on Battleship but *node ON* on Laser Maze. So
the **transport is common; the encoding is puzzle-specific.** **[source]** *(the "per-puzzle,
not standardised" conclusion: [authored — review])*

### Per-puzzle pin map
| Puzzle | Activation in | Completion out | Other event lines |
|---|---|---|---|
| Battleship (v43) | Pin 48 (active-LOW) | Pin 52 "minor" (round), Pin 50 "major" (game) | — |
| Payphone (v7) | Pin 28 (active-LOW) | Pin 30 (win) | — |
| Laser Maze (v52) | Pin A15 | Pin A13 (win, 300 ms blip) | Pin 16/TX2 node events; Pin A14 Force-Win (local override) |
*[source]*

### Signal vocabulary (observed)
| Signal | Meaning | Puzzle |
|---|---|---|
| 1 pulse | Full game win | Battleship (pin 50) |
| 3 pulses | Round/minor win | Battleship (pin 52) |
| 6 pulses | Round reset | Battleship (pin 52) |
| 3 pulses | Node ON | Laser Maze (pin 16) |
| 4 pulses | Node OFF | Laser Maze (pin 16) |
| 300 ms blip | Win | Laser Maze (pin A13) |
| pulse(s) | Win | Payphone (pin 30) |
*[source]* — note the same count means different things on different puzzles.

---

## Band 3 — Engineering / reference
- Pulse timing (Battleship & Laser Maze): **100 ms** HIGH / **200 ms** gap.
- Code hooks seen: Laser Maze `signalStaticNodeActivated()` (3 pulses) / `signalStaticNodeDeactivated()` (4 pulses); Battleship minor/major completion pulses; debug command **`C` = "Test COGS pulse output"** (Laser Maze). **[source]**
- **Version-fragile:** every pin number above belongs to a specific puzzle firmware (v7/v43/v52) and will drift as those change. The *contract* (active-LOW activation, pulsed completion) is the durable part; the pin numbers are not.

### Source evidence & provenance
- Reconstructed **indirectly** from `BattleshipPuzzle_Breakdown.docx` (v43),
  `PayphonePuzzle_Breakdown.docx` (v7), `LaserMazePuzzle_Breakdown.docx` (v52) — each generated
  from its puzzle's firmware.
- **No COGS-native source** is present. The real evidence root is the COGS configuration /
  show file and the controller's own documentation, neither of which is in the sampled corpus. **[gap]**

### Open questions / contradictions
1. **[gap — identify]** What exactly is COGS? Confirm whether it is "Cogs" by Clockwork Dog or an in-house controller, and add its documentation to the corpus.
2. **[safety — high]** Does COGS drive any **life-safety** hardware (door releases, maglocks)? If so, that is the highest-stakes system in the installation and its documentation gap matters most. Currently unknown from the sources. **[gap]**
3. **[gap — operator]** How is the room **started, reset, and monitored** through COGS? No operator procedure exists in the corpus.
4. **[review]** Is the pulse-count vocabulary meant to be standardised, or is it genuinely per-puzzle? Evidence points to per-puzzle.
5. **[review]** Confirm Laser Maze activation polarity (assumed active-LOW) and whether its **Force-Win (A14)** is a COGS line or a purely local maintenance override.
6. **[gap]** Which COGS hardware/I-O boards exist, and the full room-wide pin/wiring map.
