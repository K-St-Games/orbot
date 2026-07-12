#!/usr/bin/env python3
"""
Cortex Indexer - Indexes Obsidian markdown files into pgvector.

Reads markdown files, chunks by headings, generates embeddings via Ollama,
and stores in PostgreSQL with pgvector for semantic search.
"""

import asyncio
import hashlib
import os
import re
from pathlib import Path
from dataclasses import dataclass

import asyncpg
import httpx
from pydantic_settings import BaseSettings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


class Settings(BaseSettings):
    database_url: str = "postgresql://cortex:cortex@localhost:5433/cortex"
    litellm_url: str = "http://100.67.191.114:4000"
    litellm_api_key: str | None = None
    obsidian_path: str = "/data/obsidian"
    embedding_model: str = "qwen/qwen3-embedding-8b"
    embedding_timeout_seconds: float = 120.0
    embedding_max_retries: int = 3
    embedding_retry_base_seconds: float = 2.0
    chunk_max_tokens: int = 512
    chunk_overlap_tokens: int = 50

    class Config:
        env_file = ".env"


settings = Settings()


@dataclass
class Chunk:
    content: str
    heading_context: str
    chunk_index: int


@dataclass
class Document:
    file_path: str
    content: str
    file_hash: str
    title: str


def compute_file_hash(content: str) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(content.encode()).hexdigest()


def extract_title(content: str, file_path: str) -> str:
    """Extract title from markdown content or use filename."""
    # Try to find H1 heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fall back to filename
    return Path(file_path).stem


def chunk_markdown(content: str, max_tokens: int = 512) -> list[Chunk]:
    """
    Chunk markdown by headings, preserving heading context.

    Each chunk includes a breadcrumb of parent headings for context.
    """
    chunks = []
    lines = content.split('\n')

    # Track heading hierarchy
    heading_stack = []  # [(level, text), ...]
    current_chunk_lines = []
    chunk_index = 0

    def estimate_tokens(text: str) -> int:
        # Rough estimate: ~4 chars per token for English
        return len(text) // 4

    def flush_chunk():
        nonlocal chunk_index, current_chunk_lines
        if current_chunk_lines:
            content = '\n'.join(current_chunk_lines).strip()
            if content:
                # Build heading context breadcrumb
                context = ' > '.join(h[1] for h in heading_stack) if heading_stack else ''
                chunks.append(Chunk(
                    content=content,
                    heading_context=context,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
        current_chunk_lines = []

    for line in lines:
        # Check if this is a heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if heading_match:
            # Flush current chunk before starting new section
            flush_chunk()

            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()

            # Update heading stack - pop any headings at same or lower level
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, text))

            current_chunk_lines.append(line)
        else:
            current_chunk_lines.append(line)

            # Check if we need to split due to size
            current_text = '\n'.join(current_chunk_lines)
            if estimate_tokens(current_text) > max_tokens:
                # Split at a paragraph boundary if possible
                flush_chunk()

    # Flush remaining content
    flush_chunk()

    return chunks


async def get_embedding(client: httpx.AsyncClient, text: str) -> list[float]:
    """Get embedding from LiteLLM."""
    last_error: Exception | None = None
    for attempt in range(1, settings.embedding_max_retries + 1):
        try:
            headers = {"Content-Type": "application/json"}
            if settings.litellm_api_key:
                headers["Authorization"] = f"Bearer {settings.litellm_api_key}"

            response = await client.post(
                f"{settings.litellm_url.rstrip('/')}/v1/embeddings",
                json={
                    "model": settings.embedding_model,
                    "input": text
                },
                headers=headers,
                timeout=settings.embedding_timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            embedding = data.get("data", [{}])[0].get("embedding")
            if not embedding:
                raise RuntimeError(f"LiteLLM response missing embedding data: {data!r}")
            return embedding
        except Exception as e:
            last_error = e
            if attempt < settings.embedding_max_retries:
                wait_seconds = settings.embedding_retry_base_seconds * attempt
                console.print(
                    f"[yellow]Embedding attempt {attempt}/{settings.embedding_max_retries} failed "
                    f"({type(e).__name__}: {e!r}). Retrying in {wait_seconds:.1f}s...[/yellow]"
                )
                await asyncio.sleep(wait_seconds)
            else:
                break

    if last_error is None:
        raise RuntimeError("Embedding failed without an exception")
    raise RuntimeError(
        f"Embedding failed after {settings.embedding_max_retries} attempts: "
        f"{type(last_error).__name__}: {last_error!r}"
    ) from last_error


async def get_existing_hashes(pool: asyncpg.Pool) -> dict[str, str]:
    """Get existing document hashes from database."""
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT file_path, file_hash FROM documents")
        return {row['file_path']: row['file_hash'] for row in rows}


async def delete_document(pool: asyncpg.Pool, file_path: str):
    """Delete a document and its chunks."""
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM documents WHERE file_path = $1", file_path)


async def insert_document(pool: asyncpg.Pool, doc: Document) -> int:
    """Insert or update a document, returning its ID."""
    async with pool.acquire() as conn:
        # Delete existing if present
        await conn.execute("DELETE FROM documents WHERE file_path = $1", doc.file_path)
        # Insert new
        row = await conn.fetchrow(
            """
            INSERT INTO documents (file_path, file_hash, title)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            doc.file_path, doc.file_hash, doc.title
        )
        return row['id']


async def insert_chunks(pool: asyncpg.Pool, doc_id: int, chunks: list[Chunk], embeddings: list[list[float]]):
    """Insert chunks with embeddings."""
    async with pool.acquire() as conn:
        # Use copy for bulk insert
        await conn.executemany(
            """
            INSERT INTO chunks (document_id, chunk_index, content, heading_context, embedding)
            VALUES ($1, $2, $3, $4, $5)
            """,
            [
                (doc_id, chunk.chunk_index, chunk.content, chunk.heading_context, str(emb))
                for chunk, emb in zip(chunks, embeddings)
            ]
        )


def find_markdown_files(base_path: str) -> list[Path]:
    """Find all markdown files in directory."""
    base = Path(base_path)
    if not base.exists():
        console.print(f"[red]Path does not exist: {base_path}[/red]")
        return []
    return list(base.rglob("*.md"))


async def index_document(
    pool: asyncpg.Pool,
    client: httpx.AsyncClient,
    file_path: Path,
    base_path: str
) -> tuple[int, int]:
    """Index a single document. Returns (chunks_indexed, chunks_skipped)."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        console.print(f"[yellow]Skipping {file_path}: {e}[/yellow]")
        return 0, 0

    # Use relative path for storage
    rel_path = str(file_path.relative_to(base_path))
    file_hash = compute_file_hash(content)
    title = extract_title(content, rel_path)

    doc = Document(
        file_path=rel_path,
        content=content,
        file_hash=file_hash,
        title=title
    )

    # Chunk the document
    chunks = chunk_markdown(content, settings.chunk_max_tokens)
    if not chunks:
        return 0, 0

    # Generate embeddings for all chunks
    embeddings = []
    for chunk in chunks:
        # Include heading context in embedding
        text_to_embed = f"{chunk.heading_context}\n\n{chunk.content}" if chunk.heading_context else chunk.content
        try:
            embedding = await get_embedding(client, text_to_embed)
        except Exception as e:
            raise RuntimeError(
                f"Embedding error in chunk {chunk.chunk_index} "
                f"for {rel_path}: {type(e).__name__}: {e!r}"
            ) from e
        embeddings.append(embedding)

    # Store in database
    doc_id = await insert_document(pool, doc)
    await insert_chunks(pool, doc_id, chunks, embeddings)

    return len(chunks), 0


async def run_indexer():
    """Main indexer entry point."""
    console.print("[bold blue]Cortex Indexer[/bold blue]")
    console.print(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    console.print(f"LiteLLM: {settings.litellm_url}")
    console.print(f"Embedding model: {settings.embedding_model}")
    console.print(f"Obsidian path: {settings.obsidian_path}")
    console.print()

    # Connect to database
    pool = await asyncpg.create_pool(settings.database_url)

    # Get existing document hashes
    existing_hashes = await get_existing_hashes(pool)
    console.print(f"Found {len(existing_hashes)} existing documents in database")

    # Find markdown files
    files = find_markdown_files(settings.obsidian_path)
    console.print(f"Found {len(files)} markdown files")

    if not files:
        console.print("[yellow]No files to index[/yellow]")
        await pool.close()
        return

    # Determine which files need indexing
    files_to_index = []
    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8')
            rel_path = str(file_path.relative_to(settings.obsidian_path))
            file_hash = compute_file_hash(content)

            if rel_path not in existing_hashes or existing_hashes[rel_path] != file_hash:
                files_to_index.append(file_path)
        except Exception:
            continue

    console.print(f"Files needing indexing: {len(files_to_index)} (skipping {len(files) - len(files_to_index)} unchanged)")

    if not files_to_index:
        console.print("[green]All files up to date![/green]")
        await pool.close()
        return

    # Index files
    total_chunks = 0
    async with httpx.AsyncClient() as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Indexing...", total=len(files_to_index))

            for file_path in files_to_index:
                try:
                    chunks_indexed, _ = await index_document(pool, client, file_path, settings.obsidian_path)
                    total_chunks += chunks_indexed
                    progress.update(task, advance=1, description=f"Indexed {file_path.name}")
                except Exception as e:
                    console.print(
                        f"[red]Error indexing {file_path}: {type(e).__name__}: {e!r}[/red]"
                    )
                    progress.update(task, advance=1)

    console.print()
    console.print(f"[green]Indexed {len(files_to_index)} documents with {total_chunks} chunks[/green]")

    await pool.close()


if __name__ == "__main__":
    asyncio.run(run_indexer())
