# Cortex Project Status

## ✅ Working

- **Indexer**: 72/289 documents indexed (626 chunks) - still running
- **RAG MCP Server**: Running on `http://100.97.25.117:8100`
- **pgvector Database**: Running on `localhost:5433`
- **AnythingLLM Integration**: Connected and working!
- **MetaMCP**: Running on `http://100.97.25.117:12008`

## 🔧 In Progress

- **Indexing**: ~25% complete, running in background
- **HTTPS Setup**: SSL/TLS configuration issues with Caddy

## ❌ Blocked

- **Claude Code Integration**: Requires HTTPS, current SSL setup has handshake errors

## Current Working Configuration

### AnythingLLM
```json
{
  "cortex-rag": {
    "type": "sse",
    "url": "http://100.97.25.117:8100/sse",
    "description": "Cortex RAG - Search Obsidian notes"
  }
}
```

##  Available MCP Tools

- `search_notes` - Semantic search across Obsidian vault
- `get_note` - Retrieve specific note by path
- `list_notes` - List all indexed notes
- `get_stats` - View indexing statistics

## Next Steps

### Short Term
1. Wait for indexer to complete (217 docs remaining)
2. Test RAG queries in AnythingLLM
3. Tune search relevance

### Medium Term
1. Resolve HTTPS/SSL issues for Claude Code
2. Set up nightly re-indexing cron job
3. Dockerize RAG server

### Long Term
1. Add LiteLLM integration for model routing
2. Implement Google Calendar MCP server
3. Query logging and analytics

## Architecture

```
AnythingLLM (working)
    ↓ HTTP/MCP
Cortex RAG Server (http://100.97.25.117:8100)
    ↓ SQL
pgvector (localhost:5433)
    ↑ writes
Indexer (background job)
    ↑ reads
Obsidian Vault (/home/damien/code/shared/gdrive_obsidian)
```

## Performance

- **Indexing Speed**: ~3-4 docs/minute (Ollama embedding bottleneck)
- **Search Latency**: Sub-second query + embedding generation
- **Storage**: ~9 chunks per document average
