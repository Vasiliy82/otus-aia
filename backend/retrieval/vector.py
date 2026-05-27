from __future__ import annotations

import logging

import psycopg

from backend.config import TOP_K
from backend.db import get_connection
from backend.embeddings.model import EmbeddingModel, get_embedding_model
from backend.state import ChunkContext

logger = logging.getLogger(__name__)


def _row_to_chunk(row: dict, source: str = "vector") -> ChunkContext:
    metadata = row.get("metadata") or {}
    external_id = metadata.get("external_id") if isinstance(metadata, dict) else None
    return {
        "chunk_id": row["chunk_id"],
        "external_id": external_id,
        "chunk_text": row["chunk_text"],
        "document_title": row.get("document_title"),
        "document_id": row.get("document_id"),
        "allowed_roles": list(row.get("allowed_roles") or []),
        "vector_score": float(row.get("score") or 0.0),
        "graph_score": 0.0,
        "source": source,
    }


def vector_search(
    query: str,
    *,
    top_k: int = TOP_K,
    conn: psycopg.Connection | None = None,
    model: EmbeddingModel | None = None,
) -> list[ChunkContext]:
    model = model or get_embedding_model()
    embedding = model.encode_one(query)
    embedding_literal = "[" + ",".join(str(x) for x in embedding) + "]"

    sql = """
        SELECT
            c.chunk_id,
            c.chunk_text,
            c.allowed_roles,
            c.metadata,
            c.document_id,
            d.title AS document_title,
            1 - (ce.embedding <=> %s::vector) AS score
        FROM chunk_embedding ce
        JOIN chunk c ON c.chunk_id = ce.chunk_id
        JOIN document d ON d.document_id = c.document_id
        ORDER BY ce.embedding <=> %s::vector
        LIMIT %s
    """

    if conn is not None:
        with conn.cursor() as cur:
            cur.execute(sql, (embedding_literal, embedding_literal, top_k))
            rows = cur.fetchall()
        return [_row_to_chunk(r) for r in rows]

    with get_connection() as connection:
        return vector_search(query, top_k=top_k, conn=connection, model=model)
