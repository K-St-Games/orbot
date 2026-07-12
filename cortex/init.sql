-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table - stores source file metadata
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_hash TEXT NOT NULL,
    title TEXT,
    last_indexed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chunks table - stores document chunks with embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    heading_context TEXT,  -- breadcrumb of headings for context
    embedding vector(4096), -- qwen/qwen3-embedding-8b dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Vector index intentionally omitted:
-- ivfflat/hnsw in pgvector cannot index 4096-dim vectors.

-- Index for document lookups
CREATE INDEX IF NOT EXISTS documents_file_path_idx ON documents(file_path);
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON chunks(document_id);
