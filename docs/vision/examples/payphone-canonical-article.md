---
id: puzzle-payphone
title: Payphone
type: puzzle
room: unknown                 # [gap] not stated in the source document
status: draft                 # prototype shape example; NOT engineer-reviewed
describes_firmware: v7
source_documents:
  - PayphonePuzzle_Breakdown.docx   # itself generated from the payphone firmware; source .ino filename not captured [gap]
depends_on:
  - system-cogs               # activation + completion signalling  [system article not yet written]
  - component-dy-sv17f-audio
  - component-rgb-ring
safety_class: low             # low-voltage Arduino / NeoPixel / audio; no mains, rigging, or maglocks in source
sensitivity: internal         # contains the solution code
last_reviewed: null           # pending engineer review
last_reviewed_by: null
---

# Payphone

> **Prototype canonical article.** Drafted by Orbot from `PayphonePuzzle_Breakdown.docx`
> (firmware **v7**) as a *shape example* for the vision review. In the real wiki this
> would live at `hi-orbit-wiki/docs/puzzles/payphone.md`.
>
> **The operator-facing guidance below is authored/inferred and has not been reviewed by
> an engineer.** Everything is tagged with its basis so a reviewer can see what came from
> the source versus what Orbot reasoned out:
>
> - **[source v7]** — taken from the v7 breakdown document.
> - **[authored — review]** — inferred by Orbot from the mechanism; needs engineer confirmation.
> - **[gap]** — not covered by the source; a real hole to fill.
> - **[sensitive]** / **[safety]** — access/behaviour flags.
>
> Open items are collected under **Open questions** at the end.

---

## Band 1 — Operator
*Default depth the support agent answers at.*

### Summary
The Payphone is a code-entry puzzle disguised as a vintage payphone. Players enter a
5-digit code on nine lit buttons; entering the right sequence triggers a celebration and
tells the room controller the puzzle is solved. It also has a handset (pick-up is
detected), a coloured status ring, and an ambient white light strip. **[source v7]**

### What players do
Pick up / interact with the phone and press the lit buttons in the correct order. Each
press plays a tone; the correct 5-digit sequence wins. **[source v7]**

### Healthy behavior — what "working" looks like
When the room starts the puzzle, you should see this sequence. If you're seeing it, the
phone is fine. **[source v7]** *(phrasing for operators: [authored — review])*

1. **Standby** — everything dark and silent (before the room activates it).
2. **Activated** — the white strip comes on, a **"please dial"** voice prompt plays, and
   the status **ring turns green**.
3. **~6 seconds later** — a **continuous dial tone** starts. Now it's ready for input.
4. **Code entry** — each button lights **green** and plays a tone as it's pressed.
5. **Win** — victory sound, then a **~30-second rainbow** on the strip, then the phone
   **resets itself**.

### Troubleshooting
Symptom → what to check → when to escalate. "Escalate" means stop and hand off to
maintenance/engineering (see *When to escalate*).

| Symptom | Likely cause | Operator action | Escalate if | Basis |
|---|---|---|---|---|
| Phone is dark/silent when the room started | Puzzle never got its start signal from the room controller (COGS) | Confirm the room/COGS actually activated this puzzle | COGS shows it active but the phone stays dark | [authored — review] |
| No dial tone | Dial tone only starts **~6 s after** activation | Wait ~6 seconds after the "please dial" prompt | Still silent well after the prompt, or the prompt never played | [source v7] + [authored — review] |
| A button doesn't light or respond | Debounce timing or that button's wiring | Note whether it's **one** button or **all** buttons | One dead button, or all unresponsive → maintenance | [source v7] |
| Players entered the right code but nothing happens | Only the **last 5 presses** count — a stray extra press after the code breaks it | Have them press the code **cleanly with no trailing presses**: `1 8 5 2 4` | Verified-clean correct entry still won't win | [authored — review] |
| Handset pickup keeps resetting entry | By design, pickup resets the code and replays the prompt | Explain it resets on pickup; keep the handset settled while entering | It resets with the handset **down** (sensor stuck) | [source v7] + [authored — review] |
| Status ring stuck / won't turn green | Ring is driven separately over its own serial link | — (nothing operator-serviceable) | Ring wrong at start or won't change | [source v7] |
| No audio at all | Audio module / SD card / wiring | — | Confirmed no sounds despite an otherwise-normal start | [source v7] |
| Phone reset itself after a win | **Expected** — it auto-resets after the ~30 s celebration | None; this is normal | It resets **mid-game** for no reason | [source v7] + [authored — review] |

### Reset & recovery
- **Handset pickup** clears the current code entry and replays the prompt — the quickest
  way to let a player start the sequence over. **[source v7]**
- **After a win** the phone resets itself automatically (watchdog). **[source v7]**
- **[gap]** There is **no documented way for an operator to reset the puzzle mid-game**
  short of a full room reset (re-triggering activation via COGS) or a power cycle. This is
  the single most important operator hole in the source — **engineer must confirm the
  intended mid-game reset path.** **[authored — review]**

### When to escalate
Stop and hand off when: no audio/dial tone despite a normal-looking start; a correct,
cleanly-entered code won't win; buttons unresponsive across the board; the ring never
initialises; or **anything requires opening the enclosure** (mains adapter may be inside —
maintenance only). When you escalate, say **which state it reached** (did the white light /
"please dial" / green ring happen?), **what players tried**, and **what audio you heard**.
**[authored — review]**

---
<!-- ───────────────── depth boundary: operator above · technical below ───────────────── -->

## Band 2 — Maintenance

### How it works (deeper)
- **Rolling buffer:** only the **last 5 button presses** are compared to the code, so
  players never need to "clear" — they just have to press the right five in a row. A
  trailing stray press is what usually defeats an otherwise-correct entry. **[source v7]**
- **Handset (hall-effect) sensor:** when the handset is picked up (sensor goes LOW) the
  code buffer is reset, the welcome/dial prompt replays, and the dial tone is rescheduled.
  Active-LOW with an internal pull-up. **[source v7]**
- **States:** Standby → Activated → Dial-tone ready → Code entry → Win. **[source v7]**

### Components & wiring
| Component | Purpose | Pin/bus |
|---|---|---|
| 9 NeoPixel buttons | Player input + per-button RGB | Pin 13 (WS2812B, GRB) |
| White LED strip | 96 RGB LEDs, ambience | Pin 53 |
| DY-SV17F audio | Sound effects / prompts | Serial2 (needs SD card of WAVs) |
| Hall-effect sensor | Handset-pickup detection | Pin 7 (active-LOW, pull-up) |
| Activation (from COGS) | Start signal | Pin 28 (input) |
| Completion (to COGS) | Win signal | Pin 30 (output) |
| RGB status ring (external) | Ready/error indicator | Serial2 TX |
*[source v7]*

### Dependencies
- **COGS** room controller — activation in (pin 28), completion out (pin 30). → *see the
  `system-cogs` article* **[gap — not yet written]**.
- **DY-SV17F audio** — requires an SD card containing: `/1.wav`–`/9.wav` (button tones),
  `/wrong.wav`, `/winner.wav`, `/tone.wav` (dial tone, 4:55), `/dial.wav` ("please dial").
- **External RGB ring** over Serial2 (`G`=green/ready, `R`=red/error, `O`=off).
- Libraries: `Arduino.h`, `DYPlayerArduino.h`, `Adafruit_NeoPixel.h`, `Wire.h`, `avr/wdt.h`.
*[source v7]*

### Reference values
- **Solution code: `1 8 5 2 4`** — **[sensitive]** internal only; do not share with players.
- Activation-to-dial-tone delay: **~6 s**.
- Inactivity timeout: **10 s** — but **currently disabled** in firmware (`disableInputTimeout = true`).
- Win celebration: **~30 s** rainbow, then watchdog reset.
*[source v7]*

### Known quirks
- Dial tone is silent for the first ~6 s after activation — sounds dead but isn't. **[source v7]**
- The inactivity timeout is coded but **disabled**, so a player walking away won't auto-reset the puzzle. **[source v7]**
- Handset pickup wipes an in-progress code entry (intended). **[source v7]**
- A stray trailing press defeats an otherwise-correct code (rolling-buffer implication). **[authored — review]**

### Manual overrides
**[gap]** No force-win / maintenance override is documented for the Payphone (unlike the
Laser Maze's force-win pin). Confirm whether one exists. **[authored — review]**

---

## Band 3 — Engineering
*Version-fragile — tied to firmware **v7**; line numbers drift when firmware changes.*

| Setting | Line | Default | Purpose |
|---|---|---|---|
| `pattern[]` (code) | 54 | `{1,8,5,2,4}` | Solution; `patternSize` auto-derived |
| `debounceDelay` | 61 | 50 ms | Button debounce |
| `toneDuration` | 69 | 4:55 | Dial-tone restart interval |
| `dialToToneDelayMs` | 70 | 6000 ms | Gap after "please dial" prompt |
| `wrongToneExtraDelay` | 73 | 4000 ms | Pause after a wrong code |
| `inputTimeoutMs` | 75 | 10000 ms | Inactivity reset (disabled) |
| button pins | 22–30 | 12,3,4,5,6,8,9,10,11 | Button 1–9 inputs |
| pressed-button colour | 319 | `Color(0,150,0)` | Green on press |
| audio volume | 124 | 100 | 0–100 |
| ring command fn | 867 | `sendRingCommand()` | `G`/`R`/`O` |
| win animation | 391–411 | 30 s rainbow | then `wdt_enable(WDTO_15MS)` |
*[source v7]*

### Source evidence & provenance
- Derived from `example_breakdowns/PayphonePuzzle_Breakdown.docx`, firmware **v7**.
- That breakdown is **itself generated from the payphone firmware** (`.ino` filename not
  captured — **[gap]**). The firmware is the closer-to-truth evidence root; the physical
  phone is ultimate truth.
- **Extraction warning:** the source's ASCII state diagram and inline code were reflowed
  during text extraction — verify against the original `.docx`/firmware before relying on
  exact structure.

### Open questions / contradictions
1. **[gap]** Which room/zone is the Payphone in?
2. **[gap]** Mid-game operator reset path — how does an operator recover a stuck puzzle
   without a full room reset? *(highest-value hole)*
3. **[gap]** Does a maintenance/force-win override exist?
4. **[review]** Should the inactivity timeout be **enabled** for live operation?
5. **[gap]** Source firmware `.ino` filename/version tag for provenance.
6. **[dependency]** The `system-cogs` article does not exist yet; every puzzle needs it.
