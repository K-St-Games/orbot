# Playbook (Proposal): Google Drive → Markdown "Second Brain"

**Type:** deployment-playbook / component (proposal)
**Status:** Proposal / draft — **resurface to refine against a preliminary doc batch**
**Owner:** —
**Last reviewed:** 2026-06-04
**Emerged from:** the Hi-Orbit pilot
([`../corpus-plan.md`](../corpus-plan.md)), but
written as a **reusable** component — many projects will need "external corpus →
clean, reviewable knowledge layer."

> ⚠️ The tooling below is a **candidate** stack. Validate and trim it against a real
> batch of documents before treating any of it as settled. Format converters in
> particular behave very differently on messy real-world files.

---

## 1. Goal & output

Turn a heterogeneous document corpus (a Google Drive folder of PDFs, Word docs,
markdown, images/diagrams) into a **curated markdown "second brain"**: one sidecar
markdown file per source document, carrying provenance frontmatter and a chosen level
of extracted detail, plus a navigable index — all **git-tracked and human-reviewable**.
A weekly/monthly job keeps it in sync via a cheap diff.

"Done" = an agent (or a human) can answer from the brain with citations back to the
original source, and a refresh run produces a reviewable diff rather than a rebuild.

## 2. Architecture — three layers, each derived from the one above

```
Google Drive originals  →  markdown brain (canonical-for-the-agent)  →  vector index (rebuildable cache)
   raw source of truth        sidecars + frontmatter + map, git-tracked     throwaway speed layer
```

- **Originals** stay in Drive (read-only rclone mount). Never mutated by this pipeline.
- **The brain** is the curated derived layer the agent actually reads. It is
  *canonical for knowledge* but *derived from* originals — provenance links keep it
  honest. This is the same canonical-vs-rebuildable-cache discipline as the cartridge
  spec, applied to an external corpus.
- **The index** (vectors / keyword) is rebuilt **from the brain**, never from raw
  docs. Deleting it loses nothing.

## 3. Brain layout

Mirror the Drive folder structure 1:1 so source↔brain mapping is obvious and diffs
are trivial:

```
brain/
  index.md                      # generated map / table of contents (links per topic)
  manifest.json                 # every source: path, hash, level, status, last-processed
  Puzzles/
    Maglock Room/
      wiring.pdf.md             # sidecar for wiring.pdf
      reset-sequence.docx.md
      maglock-photo.jpg.md      # caption + extracted labels for the image
  tombstones/                   # records of sources that were deleted upstream
```

- Sidecar naming: `<original-filename>.md` (keep the extension so the source type and
  collisions are obvious).
- `index.md` and `manifest.json` are **generated**, never hand-edited.

## 4. The keystone: sidecar frontmatter

Every sidecar begins with provenance frontmatter. This is what makes incremental
refresh and review possible — get it right first.

```yaml
---
source_path: "Puzzles/Maglock Room/wiring.pdf"
source_type: pdf                 # pdf | docx | md | image | …
source_hash: "sha256:…"          # content hash → drives incremental refresh
source_modified: 2026-05-30
source_bytes: 184321
original_link: "https://drive.google.com/…"   # so the agent can surface the original
extraction_level: summary        # index | summary | full  (see §5)
extraction_version: v1           # bump when the extraction prompt improves
generated_by: "<model> @ 2026-06-04"
review_status: unreviewed        # unreviewed | engineer-approved | flagged
confidence: ok                   # ok | low  (e.g. OCR'd scan, ambiguous diagram)
tags: [maglock, reset, electrical]
---
```

Below the frontmatter: the markdown body (synopsis / structured extraction / caption,
per level), with **extracted vs. inferred** clearly distinguished and claims cited to
page/section.

## 5. Extraction levels (per-document, recorded)

A small enum, chosen **per document or per folder** — not globally. Most docs don't
deserve full extraction (cost + noise).

| Level | Body contains | Use for |
|---|---|---|
| `index` | Title, 1–2 line synopsis, tags, link | Low-value / reference docs |
| `summary` | Structured synopsis + key facts/parameters + tags | The sensible default |
| `full` | Full text extraction + structured fields | High-value docs the agent must reason over in detail |

The chosen level is recorded in frontmatter so you always know what fidelity you have,
and can re-run a subset at a higher level later.

## 6. Pipeline: deterministic harness vs. LLM extraction (keep them separate)

### Stage A — Deterministic (testable, cheap, reproducible)
Discovery → format conversion → hashing → frontmatter scaffolding. **No model calls.**

- Walk the mounted corpus; for each file compute `sha256` (and capture mtime/bytes as
  a cheap pre-check).
- Convert to text/markdown by type (see §10 tooling).
- Write/refresh the sidecar's frontmatter and the deterministic body (raw extracted
  text for `full`, or a stub awaiting Stage B).

### Stage B — LLM extraction (only the "understanding")
Synopsis, structured fields, tags, and **image/diagram captions** — the parts that
need a model. Driven by a **versioned prompt** (`extraction_version`). For images:
caption + extracted labels into the sidecar, always keeping `original_link` so the
agent can show the operator the real diagram.

### Stage C — Map + manifest
Regenerate `index.md` (navigable TOC, grouped by folder/topic) and `manifest.json`
(the authoritative list of sources + hashes + levels + statuses). For a bounded
domain, **navigation-first** retrieval (agent walks the map) often beats pure vector
search.

## 7. Refresh as a diff (the cron story)

A refresh is **not** a rebuild:

```
for each source in mount:
    if source.hash == manifest[source].hash:  skip            # unchanged
    elif source new:                           build sidecar    # Stage A+B
    else:                                       re-extract       # changed
for each manifest entry missing from mount:     tombstone        # deleted upstream (don't silently drop)
regenerate index.md + manifest.json
```

- **Single-writer**: take a lock for the run (same lease idea as the cartridge
  `runtime/.session_lock`) so a refresh can't collide with itself.
- **Re-extract on prompt change**: a bump to `extraction_version` is treated like a
  content change for the affected scope — deliberate, not accidental.
- The job's output is a **git diff a human can review** before it's trusted.

## 8. Safety & review gating

This corpus drives operator guidance on physical hardware, so:

- `review_status` gates trust. Safety-relevant docs (wiring, mag-locks, anything that
  could injure) stay `unreviewed` until the design engineer approves the sidecar.
- Distinguish **extracted** ("the doc says…") from **inferred** ("summarized as…")
  in the body — the same phenomenology guardrail from the cartridge work; never let a
  model summary read as fact.
- `confidence: low` flags OCR'd scans and ambiguous diagrams for human attention.
- The agent consuming the brain should prefer `engineer-approved` content and surface
  the original for anything safety-critical.

## 9. RAG on top

Build the retrieval index **from the brain** (per
[`rag-setup.md`](rag-setup.md)) — clean markdown chunks with frontmatter-derived
citations. The index is a rebuildable cache; the brain is the canonical knowledge.

## 10. Deterministic tooling recommendations (candidates)

| Concern | Candidate(s) | Notes |
|---|---|---|
| Drive access | **rclone** FUSE mount, read-only | Agent-agnostic; presents Drive as plain files |
| One-shot doc→markdown | **MarkItDown** (Microsoft) | Broad format coverage (docx/pptx/pdf/images), optional LLM image captions; good first try |
| Word (.docx) | **pandoc** or **mammoth** | mammoth gives clean semantic HTML/markdown; pandoc is robust/general |
| PDF (digital text) | **PyMuPDF (fitz)** or **pdfplumber** | Keep page numbers for citation |
| PDF (scanned) | **ocrmypdf** + **tesseract** | Flag `confidence: low`; OCR is error-prone |
| Images / diagrams | vision model for captions; **tesseract** for text-in-image | Caption → sidecar; keep the original link |
| Hashing / change detect | stdlib **hashlib** (sha256) + mtime/size pre-check | The basis of incremental refresh |
| Frontmatter | **python-frontmatter** / PyYAML | One schema, validated |
| Orchestration | small **Python** CLI (stdlib + above) | Idempotent; single-writer lock |
| Versioning / review | **git** | Diff-based review is the whole point |
| Scheduling | **cron** or **systemd timer** | Weekly/monthly refresh |

Suggested CLI surface (mirrors the `agentpack` style):

```bash
brain build   <mount> <brain>     # one-off full build (Stage A+B+C)
brain refresh <mount> <brain>     # incremental diff (§7)
brain status  <brain>             # what's stale / unreviewed / low-confidence
brain index   <brain>             # regenerate map + manifest only
```

## 11. First pass (the zip approach)

- Tune on a **representative subset** (5–10 docs spanning each format) before batch.
- **Lock the frontmatter schema + folder convention first** — painful to retrofit.
- Have the tool emit a **manifest of what it found and the level it chose per doc** for
  review *before* full extraction.
- Keep an **extraction log** (files processed, model, flagged items).
- Decide rename/delete handling on day one (hash + tombstones).
- Build the schema as if it's already coming from the live rclone mount, so the
  one-off and the cron share one pipeline.

## 12. Pitfalls

- Over-extracting everything to `full` (cost + noise) — tier it.
- Silent drift from source — prevented by hash tracking + tombstones.
- Cron self-collision — single-writer lock.
- Model/extraction drift — versioned prompts make re-runs deliberate.
- Treating model captions of safety hardware as fact — gate with `review_status`.

## 13. Open questions (resurface against the real batch)

1. Which converter(s) survive the actual files? (MarkItDown alone, or per-format?)
2. Are scanned PDFs present → is the OCR path needed?
3. Default extraction level, and which folders warrant `full`?
4. Diagram strategy: caption-at-ingest (this playbook) vs. multimodal-at-query —
   confirm once we see the diagram density/complexity.
5. Per-puzzle vs. master-doc structure → final chunking + map grouping.
6. Refresh cadence + trigger (scheduled vs. on Drive change).
