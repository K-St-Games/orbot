# Example Breakdowns — reference corpus samples

A handful of real documents pulled from the Hi-Orbit Google Drive corpus, landed
here as **reference material** while we design the canonical service-manual article
shape (see [`docs/vision/VISION.md`](../docs/vision/VISION.md)).

These are **samples, not the operational corpus.** The source corpus remains in
Google Drive, read-only, per the vision's knowledge model. These copies exist so
product/design work has concrete content to reason about, and as candidate source
material for the first vertical-slice proof (one real puzzle, end to end).

## What's here

| File | Puzzle / system | Version | Kind | Altitude |
|---|---|---|---|---|
| `BattleshipPuzzle_Breakdown.docx` | Battleship | v43 | Generated breakdown (How It Works / What Can Be Tweaked) | Maintainer + engineer |
| `PayphonePuzzle_Breakdown.docx` | Payphone | v7 | Generated breakdown; includes a real troubleshooting table | Maintainer + engineer |
| `LaserMazePuzzle_Breakdown.docx` | Laser Maze | v52 | Generated breakdown; target-angle reference | Maintainer + engineer |
| `Chain_Light_Logic_Explanation.docx` | Laser Maze | — | Prose software-architecture explainer | Engineer |
| `Vibe_Coding_Notes.docx` | Laser Maze | — | Raw working notes / change intent for node sequencing | Engineer draft |

## Why these are useful as a test case

- **Mixed altitude and provenance.** The `*_Breakdown` docs are generated from
  specific firmware versions ("generated from BattleshipPuzzleV43_thomasFix_110225");
  the Chain Light doc is a prose explainer; the Vibe notes are raw intent. Different
  reliability, different review status.
- **One system, three overlapping documents.** The Laser Maze is described by three
  files that partly overlap and may not fully agree — the canonical layer has to
  reconcile them into one coherent article and flag disagreement rather than silently
  choosing.
- **Engineer-shaped, not operator-shaped.** They lead with code line numbers, pin
  maps, and tunable parameters. The operator-facing "symptom -> what to check ->
  when to escalate" view is mostly latent and must be authored, not just extracted.
- **Version-fragile references.** Pin assignments and line numbers are tied to a
  firmware version, so any canonical article derived from them needs provenance and a
  staleness trigger.
