Perfect. I have enough to draft the architecture now. Let me summarize what we're building and propose the component structure:

---

**Summary of requirements:**

- ~1,000 Markdown files in nested folders (Obsidian vault)
- Source of truth: Google Drive, mounted via rclone to homelab server
- Embeddings: Local via Ollama (nomic-embed-text or similar)
- Vector store: Postgres with pgvector (leverages existing infra) or dedicated store
- Indexing: Nightly batch job
- LLM routing: LiteLLM to enable testing multiple backends (Ollama, Claude, OpenAI, etc.)
- MCP layer: RAG server exposed via MetaMCP, with room to add Calendar and other integrations later
- Clients: Multiple (Claude Code, AnythingLLM, VSCode, Open WebUI)—all pointing to MetaMCP
- Goal for v1: Ask a question → search notes → synthesized answer with references

---

**Proposed architecture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENTS                                   │
│  Claude Code  │  AnythingLLM  │  VSCode  │  Open WebUI  │  Mobile   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ MCP Protocol
                               ▼
                        ┌─────────────┐
                        │  MetaMCP    │  (aggregates all MCP servers)
                        └──────┬──────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
   ┌───────────┐        ┌─────────────┐       ┌──────────┐
   │ RAG MCP   │        │ Calendar    │       │ Future   │
   │ Server    │        │ MCP (later) │       │ MCPs     │
   └─────┬─────┘        └─────────────┘       └──────────┘
         │
         │ queries
         ▼
   ┌─────────────┐       ┌─────────────┐
   │  pgvector   │◄──────│  Indexer    │  (nightly cron)
   │  (Postgres) │       │  Service    │
   └─────────────┘       └──────┬──────┘
                                │ reads
                                ▼
                         ┌─────────────┐
                         │  rclone     │
                         │  mount      │
                         │  (GDrive)   │
                         └─────────────┘

   ┌─────────────┐
   │  Ollama     │  ← embeddings (indexer) + optional inference
   └─────────────┘

   ┌─────────────┐
   │  LiteLLM    │  ← inference routing (Ollama, Claude, OpenAI, etc.)
   └─────────────┘
```

---

**Proposed phases:**

| Phase | Milestone | Key components |
|-------|-----------|----------------|
| 1 | Indexing pipeline works | rclone mount → Indexer → pgvector, using Ollama embeddings |
| 2 | RAG MCP server works | Query interface that retrieves relevant chunks from pgvector |
| 3 | MetaMCP integration | RAG MCP exposed via MetaMCP, testable from one client |
| 4 | Multi-client testing | Connect Claude Code, AnythingLLM, VSCode, Open WebUI |
| 5 | LiteLLM integration | Route synthesis queries through LiteLLM for model comparison |
| 6 | Polish & expand | Add Google Calendar MCP, improve chunking, tune retrieval |

---

**Next steps I'd suggest:**

1. Confirm the rclone sync frequency (we can add a file watcher later if needed)
2. Decide between pgvector (simpler, one less service) vs. dedicated vector DB (Qdrant/Chroma offer nicer tooling)
3. Pick a starting point for the RAG MCP server—I can help you evaluate options or scaffold a custom one

Does this architecture match your mental model? Any components you'd add, remove, or restructure?

---

## Available Services Reference

These existing homelab services will be leveraged for the Cortex project:

| Service | Endpoint | Role in Cortex |
|---------|----------|----------------|
| **LiteLLM** | `http://100.67.191.114:4000` | LLM routing for inference (Claude, Ollama, OpenAI, etc.) |
| **Rclone Obsidian** | `http://100.97.25.117:5573` | Source mount for Obsidian vault files |
| **Rclone GDrive** | `http://100.97.25.117:5572` | Google Drive mount (source of truth) |
| **AnythingLLM** | `http://100.97.25.117:3001` | Target client for RAG queries |
| **Obsidian RAG** | `http://100.97.25.117:8089` | Existing RAG API (reference/potential integration) |
| **Ollama** | `http://100.92.38.43:11434` | Embeddings (nomic-embed-text) + inference |

**Provisioned Services:**

| Service | Endpoint | Status |
|---------|----------|--------|
| **MetaMCP** | `http://100.97.25.117:12008` | Running |
| **Cortex pgvector** | `localhost:5433` | Running |
| **RAG MCP Server** | `http://100.97.25.117:8100` | Running (local) |
| **Indexer** | N/A (batch job) | Running |

---

## Project Plan

### Phase 1: Infrastructure Setup
- [x] Set up Postgres with pgvector extension (Docker container)
- [x] Verify Ollama is running and has `nomic-embed-text` model
- [x] Confirm rclone Obsidian mount is accessible and syncing
- [x] Create project directory structure and Docker Compose scaffold

### Phase 2: Indexing Pipeline
- [x] Design document chunking strategy (heading-aware, ~500 tokens)
- [x] Build indexer service to read markdown files from rclone mount
- [x] Generate embeddings via Ollama API
- [x] Store chunks + embeddings in pgvector
- [ ] Set up nightly cron trigger for re-indexing
- [x] Add incremental indexing (hash-based change detection)

### Phase 3: RAG MCP Server
- [x] Scaffold MCP server (Python)
- [x] Implement vector similarity search against pgvector
- [x] Add context retrieval with source references
- [x] Expose MCP-compliant tool interface (`search_notes`, `get_note`, `list_notes`, `get_stats`)
- [ ] Test standalone with sample queries
- [ ] Dockerize and add to docker-compose.yaml

### Phase 4: MetaMCP Integration
- [x] Deploy MetaMCP instance
- [x] Register RAG MCP server with MetaMCP
- [ ] Configure authentication/access controls (optional)
- [ ] Test MCP protocol flow end-to-end

### Phase 5: Client Integration
- [ ] Connect Claude Code to MetaMCP (blocked: needs HTTPS, investigating SSL issues)
- [x] Connect AnythingLLM to Cortex RAG directly (working!)
- [ ] Test VSCode MCP extension
- [x] Document client configuration

### Phase 6: LiteLLM Integration
- [ ] Configure RAG server to route synthesis through LiteLLM
- [ ] Add model selection parameter to queries
- [ ] Test with multiple backends (Ollama, Claude, OpenAI)
- [ ] Add response caching layer (optional)

### Phase 7: Polish & Expansion
- [ ] Add Google Calendar MCP server
- [ ] Tune chunking and retrieval parameters
- [ ] Add query logging and analytics
- [ ] Build simple web UI for testing (optional)
- [ ] Document architecture and usage

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Vector DB** | pgvector | Simpler, reuses Postgres, SQL-based |
| **MCP server language** | Python | Easier data processing, good MCP SDK |
| **Chunking strategy** | Heading-aware | Preserves document structure context |
| **Incremental indexing** | File hash | Reliable change detection |

---

## File Structure

```
cortex/
├── docker-compose.yaml     # pgvector, rag-server, indexer
├── .env                    # Configuration
├── init.sql                # Database schema
├── mcp-config.json         # MCP client configuration
├── Claude.md               # This file
├── rag-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py           # MCP server with SSE transport
└── indexer/
    ├── Dockerfile
    ├── requirements.txt
    └── indexer.py          # Batch indexing service
```