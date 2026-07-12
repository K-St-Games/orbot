#!/usr/bin/env python3
"""
Cortex RAG MCP Server - Semantic search over Obsidian notes.

Exposes MCP tools for searching and retrieving notes from pgvector.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from pydantic_settings import BaseSettings
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse


class Settings(BaseSettings):
    database_url: str = "postgresql://cortex:cortex@localhost:5433/cortex"
    litellm_url: str = "http://100.67.191.114:4000"
    litellm_api_key: str | None = None
    embedding_model: str = "qwen/qwen3-embedding-8b"
    default_limit: int = 5
    host: str = "0.0.0.0"
    port: int = 8100

    class Config:
        env_file = ".env"


settings = Settings()

# Global connection pool
db_pool: asyncpg.Pool | None = None


async def get_embedding(text: str) -> list[float]:
    """Get embedding from LiteLLM (OpenAI-compatible embeddings endpoint)."""
    headers = {"Content-Type": "application/json"}
    if settings.litellm_api_key:
        headers["Authorization"] = f"Bearer {settings.litellm_api_key}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.litellm_url.rstrip('/')}/v1/embeddings",
            json={
                "model": settings.embedding_model,
                "input": text
            },
            headers=headers,
            timeout=60.0
        )
        response.raise_for_status()
        payload = response.json()
        embedding = payload.get("data", [{}])[0].get("embedding")
        if not embedding:
            raise RuntimeError(f"LiteLLM response missing embedding data: {payload!r}")
        return embedding


async def search_similar_chunks(query_embedding: list[float], limit: int = 5) -> list[dict]:
    """Search for similar chunks in pgvector."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                d.file_path,
                d.title,
                c.content,
                c.heading_context,
                c.embedding <=> $1::vector AS distance
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> $1::vector
            LIMIT $2
            """,
            str(query_embedding),
            limit
        )
        return [
            {
                "file_path": row["file_path"],
                "title": row["title"],
                "content": row["content"],
                "heading_context": row["heading_context"],
                "relevance_score": 1 - row["distance"]  # Convert distance to similarity
            }
            for row in rows
        ]


async def get_note_by_path(file_path: str) -> dict | None:
    """Get a note and all its chunks by file path."""
    async with db_pool.acquire() as conn:
        doc = await conn.fetchrow(
            "SELECT id, file_path, title FROM documents WHERE file_path = $1",
            file_path
        )
        if not doc:
            return None

        chunks = await conn.fetch(
            """
            SELECT content, heading_context, chunk_index
            FROM chunks
            WHERE document_id = $1
            ORDER BY chunk_index
            """,
            doc["id"]
        )

        # Reconstruct full content
        full_content = "\n\n".join(c["content"] for c in chunks)

        return {
            "file_path": doc["file_path"],
            "title": doc["title"],
            "content": full_content,
            "chunk_count": len(chunks)
        }


async def list_all_notes() -> list[dict]:
    """List all indexed notes."""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT d.file_path, d.title, COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN chunks c ON d.id = c.document_id
            GROUP BY d.id, d.file_path, d.title
            ORDER BY d.title
            """
        )
        return [
            {
                "file_path": row["file_path"],
                "title": row["title"],
                "chunk_count": row["chunk_count"]
            }
            for row in rows
        ]


# Create MCP server
mcp_server = Server("cortex-rag")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_notes",
            description="Search Obsidian notes using semantic similarity. Returns relevant note chunks based on the query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query - can be a question or topic"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_note",
            description="Retrieve a specific note by its file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The file path of the note (e.g., '70-Software Development/Python Tips.md')"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="list_notes",
            description="List all indexed notes with their titles and file paths.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_stats",
            description="Get statistics about the indexed notes.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""

    if name == "search_notes":
        query = arguments.get("query", "")
        limit = arguments.get("limit", settings.default_limit)

        if not query:
            return [TextContent(type="text", text="Error: query is required")]

        # Get embedding for query
        query_embedding = await get_embedding(query)

        # Search for similar chunks
        results = await search_similar_chunks(query_embedding, limit)

        if not results:
            return [TextContent(type="text", text="No matching notes found.")]

        # Format results
        output = f"Found {len(results)} relevant results:\n\n"
        for i, result in enumerate(results, 1):
            output += f"## {i}. {result['title']}\n"
            output += f"**File:** {result['file_path']}\n"
            if result['heading_context']:
                output += f"**Section:** {result['heading_context']}\n"
            output += f"**Relevance:** {result['relevance_score']:.2%}\n\n"
            output += f"{result['content']}\n\n"
            output += "---\n\n"

        return [TextContent(type="text", text=output)]

    elif name == "get_note":
        file_path = arguments.get("file_path", "")

        if not file_path:
            return [TextContent(type="text", text="Error: file_path is required")]

        note = await get_note_by_path(file_path)

        if not note:
            return [TextContent(type="text", text=f"Note not found: {file_path}")]

        output = f"# {note['title']}\n\n"
        output += f"**File:** {note['file_path']}\n"
        output += f"**Chunks:** {note['chunk_count']}\n\n"
        output += "---\n\n"
        output += note['content']

        return [TextContent(type="text", text=output)]

    elif name == "list_notes":
        notes = await list_all_notes()

        if not notes:
            return [TextContent(type="text", text="No notes indexed yet.")]

        output = f"# Indexed Notes ({len(notes)} total)\n\n"
        for note in notes:
            output += f"- **{note['title']}** ({note['chunk_count']} chunks)\n"
            output += f"  `{note['file_path']}`\n"

        return [TextContent(type="text", text=output)]

    elif name == "get_stats":
        async with db_pool.acquire() as conn:
            doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
            chunk_count = await conn.fetchval("SELECT COUNT(*) FROM chunks")

        output = "# Cortex RAG Stats\n\n"
        output += f"- **Documents indexed:** {doc_count}\n"
        output += f"- **Total chunks:** {chunk_count}\n"
        output += f"- **Embedding model:** {settings.embedding_model}\n"
        output += f"- **LiteLLM URL:** {settings.litellm_url}\n"

        return [TextContent(type="text", text=output)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# SSE Transport setup
sse_transport = SseServerTransport("/messages/")


async def handle_sse(request):
    """Handle SSE connection for MCP."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


async def handle_messages(request):
    """Handle POST messages for MCP."""
    await sse_transport.handle_post_message(request.scope, request.receive, request._send)


async def health_check(request):
    """Health check endpoint."""
    async with db_pool.acquire() as conn:
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
        chunk_count = await conn.fetchval("SELECT COUNT(*) FROM chunks")

    return JSONResponse({
        "status": "healthy",
        "documents": doc_count,
        "chunks": chunk_count
    })


@asynccontextmanager
async def lifespan(app):
    """Application lifespan - setup and teardown."""
    global db_pool
    print(f"Connecting to database: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    db_pool = await asyncpg.create_pool(settings.database_url)
    print("Database connected")
    print(f"Cortex RAG MCP Server running on {settings.host}:{settings.port}")
    yield
    await db_pool.close()
    print("Database connection closed")


# Create Starlette app
app = Starlette(
    debug=False,
    routes=[
        Route("/health", health_check),
        Route("/sse", handle_sse),
        Route("/messages/", handle_messages, methods=["POST"]),
    ],
    lifespan=lifespan,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
