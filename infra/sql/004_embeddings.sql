-- Vector embeddings for chunk retrieval (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunk_embedding (
    chunk_id INT PRIMARY KEY REFERENCES chunk(chunk_id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    model_name TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunk_embedding_hnsw
    ON chunk_embedding
    USING hnsw (embedding vector_cosine_ops);
