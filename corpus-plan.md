# Hi-Orbit — Corpus Ingestion Plan

**Status:** v0.1 draft
**Source:** Puzzle design documents in **Google Drive**, read via an **rclone FUSE
mount** (read-only). See [`playbooks/rag-setup.md`](playbooks/rag-setup.md)
and [`playbooks/google-drive.md`](playbooks/google-drive.md).

The agent answers troubleshooting questions **only** from this corpus, with
citations. Garbage-in shows up directly as bad operator guidance, so ingestion
quality is the pilot's main lever.

---

## Formats and how each is handled

| Format | Handling at ingest | Notes |
|---|---|---|
| **Markdown / text** | Index directly. | Cleanest; best citations. Prefer this format for new docs. |
| **Word (.docx)** | Extract text (+ headings) → chunk. | Clean; preserve section structure for citation. |
| **PDF (digital)** | Extract text layer → chunk. | Keep page numbers for citation. |
| **PDF (scanned)** | OCR first, then as above. | Flag low-confidence OCR; scanned docs are error-prone. |
| **Images / diagrams** | **See decision below.** | Wiring diagrams, schematics, photos — not text-searchable as-is. |

## The diagram problem (main technical risk)

Escape-room design docs lean heavily on **wiring diagrams, schematics, and photos**.
Plain text-RAG can't retrieve or reason over an image. Three options:

1. **Caption-at-ingest (recommended for v0.1).** Run each image through a
   vision model once at ingest to produce a text description + extracted labels;
   index that text, and **keep a link to the original image** so the agent can say
   *"see `puzzle-3-maglock.png`"* and surface it to the operator. Searchable + the
   operator still sees the real diagram.
2. **Surface-as-asset only.** Don't caption; just index the surrounding doc text and
   let the agent link the image by filename. Cheapest; weakest retrieval (you can't
   find a diagram by what's *in* it).
3. **Multimodal at query time.** Show relevant images to a vision-capable model when
   answering. Most capable; higher cost/complexity, and depends on the runtime's
   model support.

**Recommendation:** start with **(1)** — caption-at-ingest + keep the asset link.
Re-evaluate (3) if operators need the agent to reason over diagram detail.

> **Direction update (2026-06-04):** rather than caption inline into the vector
> index, captions become part of a curated **markdown "second brain"** — a
> git-tracked, reviewable derived layer over the Drive corpus. See the reusable
> [`playbooks/gdrive-markdown-brain.md`](playbooks/gdrive-markdown-brain.md)
> proposal; this corpus plan becomes Hi-Orbit's application of that playbook.

> ⚠️ Captions are model-generated interpretations of safety-relevant hardware. Tag
> them as derived (cf. the cartridge "phenomenology" guardrail) and have the design
> engineer spot-check captions for critical diagrams before operators rely on them.

## Chunking & citation

- **Chunk per puzzle / per section** so a retrieved passage maps to one puzzle.
  (Confirm whether docs are one-per-puzzle or a master doc — drives this.)
- Carry **source path + section/page** on every chunk so answers cite precisely and
  the engineer can audit.
- Keep image captions linked to both their source doc and the image asset.

## Freshness

- Docs change as puzzles are re-tuned. Decide a **re-index trigger** (on Drive
  change, or scheduled). Stale guidance on a changed puzzle is a real failure mode.
- Record ingest provenance (doc version/modified-time) so the agent can flag when its
  source may be outdated.

## Open decisions
1. Diagram handling: confirm option (1) vs (3).
2. Per-puzzle vs master-doc structure → final chunking.
3. Re-index cadence/trigger.
4. Whether scanned PDFs are present (→ OCR step needed?).
