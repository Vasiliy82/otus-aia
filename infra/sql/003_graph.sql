-- Knowledge graph (GraphRAG expansion)
CREATE TABLE IF NOT EXISTS graph_node (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    ref_table TEXT,
    ref_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS graph_edge (
    edge_id SERIAL PRIMARY KEY,
    source_node_id TEXT NOT NULL REFERENCES graph_node(node_id),
    target_node_id TEXT NOT NULL REFERENCES graph_node(node_id),
    edge_type TEXT NOT NULL,
    weight NUMERIC NOT NULL DEFAULT 1.0,
    confidence NUMERIC NOT NULL DEFAULT 1.0,
    source_chunk_id INT REFERENCES chunk(chunk_id),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
