---
id: puzzle-laser-maze
title: Laser Maze
type: puzzle
room: unknown                 # [gap] not stated in the sources
status: draft                 # prototype shape example; NOT engineer-reviewed
describes_firmware: v52
source_documents:
  - name: LaserMazePuzzle_Breakdown.docx
    tier: current             # generated from v52 firmware; most authoritative for "what ships"
    firmware: v52
  - name: Chain_Light_Logic_Explanation.docx
    tier: supporting          # prose architecture explainer; unversioned; partly inconsistent w/ v52
    firmware: unknown
  - name: Vibe_Coding_Notes.docx
    tier: draft-intent         # raw change-request handed to an AI; NOT verified shipped behavior
    firmware: unknown
depends_on:
  - system-cogs               # activation + completion + node-event pulses  [system article not yet written]
safety_class: elevated        # LASERS (26 beams). Eye-safety hazard; laser class unconfirmed [safety][gap]
sensitivity: internal         # target angles + chain order are effectively the solution
last_reviewed: null
last_reviewed_by: null
---

# Laser Maze

> **Prototype canonical article.** Drafted by Orbot from three overlapping source
> documents. In the real wiki this would live at `hi-orbit-wiki/docs/puzzles/laser-maze.md`.
>
> **Operator-facing guidance is authored/inferred and unreviewed.** Basis tags:
> **[source v52]** (from the version-stamped breakdown) · **[authored — review]** ·
> **[gap]** · **[sensitive]** / **[safety]**.

## Sources & reconciliation
This puzzle is described by **three documents that disagree.** They are not equal:

| Tier | Document | How it's treated |
|---|---|---|
| **Current** | `LaserMazePuzzle_Breakdown.docx` (v52) | Generated from shipped firmware → **treated as current truth** where sources conflict. |
| **Supporting** | `Chain_Light_Logic_Explanation.docx` | Useful mechanism/explanation, but **unversioned** and inconsistent with v52 in places → used for context, **flagged** where it diverges. |
| **Draft intent** | `Vibe_Coding_Notes.docx` | A **change request** ("change sequence... to follow this mapping"), not confirmed shipped → **NOT** used as truth; contradictions recorded below. |

**Material conflicts are collected under [Open questions / contradictions](#open-questions--contradictions).** The most important: the Vibe notes' **Mode B sequence contradicts the v52 firmware.** This article follows **v52**.

---

## Band 1 — Operator
*Default depth the support agent answers at.*

### Summary
The Laser Maze is a light-routing puzzle. Players rotate **9 mirrors** to the correct
angles to complete a "chain" of light from the start node through to the end. Get the
whole chain right and it wins, then it **switches to a different solution** for the next
group. **[source v52]**

> **[safety]** This puzzle uses **lasers** (26 beams). Avoid direct or reflected beam
> exposure to eyes. Alignment/optics work is **maintenance-only** — laser class is
> unconfirmed **[gap]**; treat cautiously until an engineer classifies it.

### What players do
Rotate the physical mirrors. Each mirror's light turns **green when it's at the right
angle**, **red when it's wrong**. Correct mirrors in sequence extend the lit path.
**[source v52]**

### Healthy behavior — what "working" looks like
**[source v52]** *(operator phrasing: [authored — review])*
1. **Start** — node 10 lights (rainbow, its two lasers on) when the room activates the puzzle.
2. **Progress** — as each mirror is set correctly **in order**, the next node(s) light dim
   green, showing the path advancing. Encoder LEDs: **green = correct, red = wrong**.
3. **Win** — full chain correct → rainbow celebration + the room controller (COGS) gets a
   win pulse. The puzzle then **switches to the other mode** (A↔B) for next time.

### Troubleshooting

| Symptom | Likely cause | Operator action | Escalate if | Basis |
|---|---|---|---|---|
| Maze won't complete, mirrors look right | The chain **stops at the first wrong mirror** — it's a domino | Find the **last green node**; the break is the **next** mirror in the path. Nudge it until green | A mirror can't be made green at all | [authored — review] |
| One mirror never turns green | Miscalibrated target, or a bad encoder / I2C mux | — (maintenance can read live angle via the `E#` debug command) | Any mirror can't reach green | [source v52] + [authored — review] |
| Solution seems different than before | **Expected** — it alternates **Mode A / Mode B** after each win; **both angles *and* mirror order change** | Reassure; testers/resetters need **both** solution sets | Modes stop alternating | [source v52] + [authored — review] |
| Lights on that aren't on the path | Possibly **decoys** (if enabled in this build) meant to mislead — or a node-mapping fault | Note which nodes | Persistent, or blocks solving | [authored — review] **[gap: see contradictions]** |
| Nothing lights / node 10 dark | Not activated (pin A15) or power | Confirm the room/COGS activated it | Active but dark | [authored — review] |

### Reset & recovery
- The puzzle **switches mode automatically after each win** — no operator action. **[source v52]**
- A **Force-Win input (pin A14)** exists to force completion — a **maintenance override**,
  not a normal operator control. **[source v52] [safety: authorized use]**
- **[gap]** No documented operator mid-game reset short of a room reset (re-triggering
  activation via COGS). Engineer to confirm. **[authored — review]**

### When to escalate
A mirror that never reads correct (sensor/mux/I2C); lasers not firing; **any physical
laser or optics alignment** beyond rotating a mirror; remapping nodes to LEDs. Hand off:
**which node the chain stopped at**, which mirror, and whether it was Mode A or B.
**[authored — review]**

---
<!-- ───────────────── depth boundary: operator above · technical below ───────────────── -->

## Band 2 — Maintenance

### How it works (deeper)
- A **chain** is an ordered list of nodes (encoders 1–9 and static nodes 10+). The puzzle
  lights the chain step by step; each **encoder** must be within the **angle threshold
  (±20°)** of its target before the next node activates. First out-of-range encoder =
  **chain break**, halting progress. **[source v52]**
- Two modes (**A** and **B**) each have their **own target angles and their own chain
  order**; the mode toggles after every win. **[source v52]**
- **Decoys** (per the supporting explainer): alternate angles that light non-chain LEDs to
  mislead players. **Presence in v52 is unconfirmed** — see contradictions. **[supporting] [gap]**

### Components & wiring
| Component | Purpose | Pin/bus |
|---|---|---|
| NeoPixel Strip 1 | Encoder nodes 1–9 (9 LEDs) | Pin 4 |
| NeoPixel Strip 2 | Static nodes 19–25 (73 LEDs) | Pin 2 |
| NeoPixel Strip 3 | Static nodes 10–18 (121 LEDs) | Pin 3 |
| 9× AS5600 encoders | Magnetic rotation sensors (the mirrors) | I2C via TCA9548A muxes |
| 26 laser transistors | Drive the laser beams | Various GPIO **[safety]** |
| Activation (from COGS) | Start signal | Pin A15 (input) |
| Force-Win | Override to win | Pin A14 (input) |
| COGS Output 1 | Win signal (300 ms blip) | Pin A13 |
| COGS Output 2 | Node-event pulses (3=on, 4=off) | Pin 16 / TX2 |
*[source v52]*

### Dependencies
- **COGS** — activation in (A15), win out (A13, 300 ms), node-event pulses out (pin 16:
  3 pulses = node ON, 4 = node OFF). → *see `system-cogs`* **[gap — not yet written]**.
- I2C bus + **TCA9548A** multiplexers for the 9 encoders.
- Libraries: `Wire.h`, `Adafruit_NeoPixel.h`, `PeripheralFunctions.h` (custom encoder/mux classes).
*[source v52]*

### Reference values  **[sensitive]** *(effectively the solution — internal only)*
**Target angles (±20° threshold):**

| Encoder | Mode A | Mode B |
|---|---|---|
| 1 | 61° | 354° |
| 2 | 331° | 309° |
| 3 | 90° | 116° |
| 4 | 280° | 280° |
| 5 | 187° | 183° |
| 6 | 6° | 359° |
| 7 | 288° | 34° |
| 8 | 318° | 145° |
| 9 | 163° | 303° |

**Chain order (v52 firmware, encoders in bold):**
- **Mode A:** 11·**1**·12·13·**2**·14·**3**·15·**4**·16·**5**·17·**6**·18·**7**·19·**8**·22·**9**·23  → encoder order **1‑2‑3‑4‑5‑6‑7‑8‑9**
- **Mode B:** 12·**2**·13·14·**6**·15·**1**·16·**4**·17·**3**·24·**5**·25·**8**·20·**7**·22·**9**  → encoder order **2‑6‑1‑4‑3‑5‑8‑7‑9**

*[source v52]*

### Known quirks
- The two modes have **different mirror sequences**, not just different angles — a real gotcha for anyone testing/resetting. **[source v52]**
- Encoder tolerance below ~10° is frustrating due to sensor precision. **[source v52]**
- Node numbers are **logical**; a separate `mapNodeToLedIndex()` maps them to physical LED indices (e.g. node 10 → LED 31). Don't confuse logical nodes with LED indices. **[source v52]**

### Manual overrides
- **Force-Win (pin A14)** forces completion. **[source v52] [safety: authorized only]**

---

## Band 3 — Engineering
*Version-fragile — tied to firmware **v52**; line numbers drift when firmware changes.*

| Setting | Line | Value | Purpose |
|---|---|---|---|
| `angleThreshold` | 330 | 20.0 | ±degrees tolerance |
| `expectedAnglesA[]` | 111 | 61,331,90,280,187,6,288,318,163 | Mode A targets |
| `expectedAnglesB[]` | 112 | 354,309,116,280,183,359,34,145,303 | Mode B targets |
| `chainA[]` | 114 | 11,1,12,13,2,14,3,15,4,16,5,17,6,18,7,19,8,22,9,23 | Mode A path |
| `chainB[]` | 114–117 | 12,2,13,14,6,15,1,16,4,17,3,24,5,25,8,20,7,22,9 | Mode B path |
| `animationInterval` | 320 | 50 ms | Chain update rate |
| LED brightness | 820–828 | 64 | 0–255 |
| Node→LED map | 375–402 | — | `mapNodeToLedIndex()` |
| COGS pulse timing | 435–436 | 100 ms / 200 ms | pulse / gap |

**Debug commands (Serial):** `L#`/`M#`/`P#` flash strip LEDs · `E#` live-poll encoder · `T#` pulse transistor · `N#` flash logical node · `S` sweep all · `C` test COGS output. **[source v52]**

**Win:** rainbow + 300 ms COGS blip + mode switch (`chainComplete()`). **[source v52]**

### Source evidence & provenance
- **Current:** `example_breakdowns/LaserMazePuzzle_Breakdown.docx`, firmware **v52** (generated from the `.ino`; source filename not captured **[gap]**).
- **Supporting:** `Chain_Light_Logic_Explanation.docx` (unversioned prose).
- **Draft intent:** `Vibe_Coding_Notes.docx` (change request; not confirmed shipped).
- **Extraction warning:** ASCII node diagrams and code were reflowed during text extraction; verify against originals/firmware.

### Open questions / contradictions
1. **[contradiction — high]** **Mode B sequence.** `Vibe_Coding_Notes` gives **2‑1‑3‑5‑6‑8‑7‑9 (skips encoder 4)**; v52 `chainB` is **2‑6‑1‑4‑3‑5‑8‑7‑9 (all 9)**. This article follows **v52**. Is the vibe-notes mapping an unimplemented proposal, or was v52 later changed? Engineer must confirm which is live.
2. **[contradiction]** **Encoder 4 in Mode B** — v52 uses it (angle 280°, present in `chainB`); the vibe notes drop it. Same resolution as #1.
3. **[contradiction]** **Decoys** — central in `Chain_Light_Logic_Explanation`, absent from the v52 breakdown's chain arrays/debug. Are decoys in v52?
4. **[contradiction]** **Win audio** — the explainer's `chainComplete()` plays `/dogs.wav` via an audio player, but the v52 breakdown lists **no audio hardware** for this puzzle. Stale/other build, or removed by v52?
5. **[numbering]** The explainer uses indices up to 31 (looks like **physical LED indices**); v52 separates **logical nodes (1–25)** from LED indices via `mapNodeToLedIndex()`. Confirm the numbering the team wants canonical.
6. **[gap]** Room/zone; operator mid-game reset path; laser class (safety); `system-cogs` article.
