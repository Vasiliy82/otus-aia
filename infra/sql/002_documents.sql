-- Documents and chunks (normative + internal policies)
CREATE TABLE IF NOT EXISTS document (
    document_id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    title TEXT NOT NULL,
    security_level TEXT NOT NULL DEFAULT 'public',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS chunk (
    chunk_id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES document(document_id),
    chunk_text TEXT NOT NULL,
    chunk_order INT NOT NULL,
    allowed_roles TEXT[] NOT NULL DEFAULT ARRAY['analyst'],
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
