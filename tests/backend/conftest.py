from __future__ import annotations

import os

os.environ.setdefault("OTEL_TRACES_ENABLED", "false")
os.environ.setdefault("JSON_LOGS", "false")

import pytest
import psycopg

from backend.config import DATABASE_URL


def _db_available() -> bool:
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except Exception:
        return False


def _embeddings_available() -> bool:
    if not _db_available():
        return False
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM chunk_embedding")
                row = cur.fetchone()
                return row is not None and row[0] > 0
    except Exception:
        return False


requires_db = pytest.mark.skipif(
    not _db_available() or os.getenv("RUN_INTEGRATION", "").lower() not in ("1", "true", "yes"),
    reason="Set RUN_INTEGRATION=1 and ensure PostgreSQL with migrated schema",
)

requires_embeddings = pytest.mark.skipif(
    not _embeddings_available() or os.getenv("RUN_INTEGRATION", "").lower() not in ("1", "true", "yes"),
    reason="Set RUN_INTEGRATION=1, run make data-all && make embed-chunks",
)
