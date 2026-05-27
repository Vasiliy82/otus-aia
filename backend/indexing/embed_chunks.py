from __future__ import annotations

import logging

from backend.config import EMBEDDING_DIM, EMBEDDING_MODEL
from backend.db import get_connection
from backend.embeddings.model import get_embedding_model

logger = logging.getLogger(__name__)


def embed_all_chunks() -> int:
    model = get_embedding_model()
    dim = model.dimension
    if dim != EMBEDDING_DIM:
        logger.warning(
            "Model dimension %s differs from EMBEDDING_DIM=%s; update migration if needed",
            dim,
            EMBEDDING_DIM,
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.chunk_id, c.chunk_text
                FROM chunk c
                LEFT JOIN chunk_embedding ce ON ce.chunk_id = c.chunk_id
                ORDER BY c.chunk_id
                """
            )
            rows = cur.fetchall()

        if not rows:
            logger.warning("No chunks found — run make data-load first")
            return 0

        texts = [r["chunk_text"] for r in rows]
        vectors = model.encode(texts)

        with conn.cursor() as cur:
            for row, vec in zip(rows, vectors):
                literal = "[" + ",".join(str(float(x)) for x in vec) + "]"
                cur.execute(
                    """
                    INSERT INTO chunk_embedding (chunk_id, embedding, model_name, updated_at)
                    VALUES (%s, %s::vector, %s, NOW())
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        model_name = EXCLUDED.model_name,
                        updated_at = NOW()
                    """,
                    (row["chunk_id"], literal, EMBEDDING_MODEL),
                )
        conn.commit()

    logger.info("Indexed %d chunk embeddings with model %s", len(rows), EMBEDDING_MODEL)
    return len(rows)
