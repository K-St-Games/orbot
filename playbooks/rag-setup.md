# RAG Setup — Retrieval for an Agent

**Type:** deployment-playbook
**Status:** draft
**Owner:** —
**Last reviewed:** 2026-06-04
**Applies to:** Tier 2+ agents (augmented retrieval). For Tier 3 cartridge agents,
the retrieval index is a **rebuildable cache**, never canonical memory.

> ⚠️ This playbook describes the *shape* of a RAG deployment. Exact vector-store and
> embedding-model choices drift fast — confirm current options before committing.

---

## 1. Goal

Give an agent the ability to answer from a corpus it wasn't trained on (project
docs, a shared drive export, a spec set) by retrieving relevant chunks at query
time, exposed through a single tool call — without bloating the context window.

Done = the agent can answer a question about the corpus with a cited snippet, and
the index can be deleted and rebuilt from source without data loss.

## 2. Architecture (how it fits our model)

```
source docs ──► chunk ──► embed ──► vector store ──┐
                                                   ├─► RAG MCP service ──► agent (tool call)
keyword index (optional, hybrid) ──────────────────┘
```

- **Retrieval is a backend, not a differentiator.** Prefer wrapping an existing
  stack behind a `search` tool over building retrieval from scratch (see
  `docs/memory_platform/cartridge-module-roadmap.md` §8; `Memory OS Review.md`).
- **Expose via an MCP service** so the agent searches with a tool call instead of
  receiving a dumped corpus (Epic 2, `docs/memory_platform/roadmap.md`).
- **Caches are rebuildable.** The vector index is derived from canonical source
  docs. Record enough provenance (source path, chunk offsets) to rebuild and to
  cite.

## 3. Prerequisites

- An agent runtime that can register an MCP server / external tool.
- A corpus location the operator can read (local export, mounted drive, or a
  connector — e.g. the Google Drive playbook for a live source).
- An embedding model endpoint and a vector store (chosen per deployment).

## 4. Secrets & config (placeholders only)

| Value | Placeholder | Lives in |
|---|---|---|
| Embedding API key | `<EMBEDDING_API_KEY>` | runtime `.env` / secrets manager |
| Vector store URL/key | `<VECTOR_STORE_URL>`, `<VECTOR_STORE_KEY>` | runtime `.env` |
| Corpus path/connector | `<CORPUS_SOURCE>` | deployment config |

## 5. Steps

1. **Inventory the corpus.** Confirm formats (md/pdf/docx), size, and update
   cadence. → *Verify:* you can list source files and counts.
2. **Choose chunking.** Start with recursive character chunks (~512 tokens, small
   overlap); adjust for document structure. → *Verify:* a sample doc chunks into
   sensible, self-contained passages.
3. **Embed + index.** Run embeddings into the vector store; persist source path and
   chunk offsets alongside each vector for provenance/citations. → *Verify:* a
   nearest-neighbor query on a known phrase returns the expected chunk.
4. **(Optional) Add a keyword/hybrid fallback** for exact-match queries (IDs, error
   strings) that embeddings handle poorly. → *Verify:* an exact-ID query hits.
5. **Stand up the RAG MCP service.** Expose one `search(query, k)` tool returning
   ranked chunks **with citations** (source + offset). → *Verify:* calling the tool
   directly returns cited results.
6. **Register the tool with the agent** and instruct it to retrieve-then-answer and
   to cite. → *Verify:* the agent calls `search` rather than guessing.

## 6. Verification (end-to-end)

Ask the agent a question whose answer is in exactly one source doc. It should call
`search`, return the correct answer, and cite the source file. Then ask something
*not* in the corpus — it should say it can't find it, not hallucinate.

## 7. Rollback / teardown

- Deregister the MCP tool from the agent.
- Delete the vector index and any keyword index (both rebuildable; no canonical
  data lost).
- Revoke the embedding/vector-store keys if the deployment is ending.

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Irrelevant chunks | Chunk size too large / no overlap | Re-chunk smaller; add overlap |
| Exact IDs never found | Pure-vector retrieval | Add keyword/hybrid fallback (step 4) |
| Agent ignores the tool | Tool not registered / weak instruction | Confirm registration; instruct retrieve-then-answer |
| Stale answers | Index not rebuilt after source change | Schedule re-index on corpus update |

## 9. Staleness notes

Re-check on review: current embedding-model names/dimensions, vector-store SDK and
API, and whether the runtime's MCP registration mechanism has changed.
