from __future__ import annotations

import logging

import psycopg

from backend.config import EXPAND_EDGE_TYPES, EXPAND_HOPS
from backend.db import get_connection
from backend.observability.logging import log_rag_step
from backend.observability.tracing import traced_span
from backend.state import ChunkContext, GraphNodeContext

logger = logging.getLogger(__name__)

_REACHABLE_NODES_SQL = """
WITH RECURSIVE graph_walk AS (
    SELECT node_id, 0 AS depth, ARRAY[node_id]::text[] AS visited
    FROM unnest(%s::text[]) AS node_id

    UNION

    SELECT neighbor.node_id, gw.depth + 1, gw.visited || neighbor.node_id
    FROM graph_walk gw
    CROSS JOIN LATERAL (
        SELECT CASE
            WHEN e.source_node_id = gw.node_id THEN e.target_node_id
            ELSE e.source_node_id
        END AS node_id
        FROM graph_edge e
        WHERE e.edge_type = ANY(%s)
          AND (e.source_node_id = gw.node_id OR e.target_node_id = gw.node_id)
    ) neighbor
    WHERE gw.depth < %s
      AND NOT (neighbor.node_id = ANY(gw.visited))
)
SELECT DISTINCT ON (gw.node_id)
    gw.node_id,
    n.node_type,
    n.label,
    n.ref_table,
    n.ref_id,
    n.metadata
FROM graph_walk gw
JOIN graph_node n ON n.node_id = gw.node_id
ORDER BY gw.node_id, gw.depth
"""


def _chunk_node_id(external_id: str) -> str:
    return f"chunk:{external_id}"


def _fetch_reachable_nodes(
    cur: psycopg.Cursor,
    seed_node_ids: list[str],
    *,
    hops: int,
    edge_types: tuple[str, ...],
) -> list[dict]:
    if not seed_node_ids:
        return []
    cur.execute(
        _REACHABLE_NODES_SQL,
        (seed_node_ids, list(edge_types), hops),
    )
    return list(cur.fetchall())


def _chunks_for_nodes(cur: psycopg.Cursor, nodes: list[dict]) -> list[ChunkContext]:
    chunk_external_ids: list[str] = []
    for node in nodes:
        if node["node_type"] == "Chunk" and node.get("ref_id"):
            chunk_external_ids.append(node["ref_id"])
        elif node["node_id"].startswith("chunk:"):
            chunk_external_ids.append(node["node_id"].split(":", 1)[1])

    document_external_ids = [
        n["ref_id"]
        for n in nodes
        if n["node_type"] == "Document" and n.get("ref_id")
    ]

    chunks: list[ChunkContext] = []

    if chunk_external_ids:
        cur.execute(
            """
            SELECT c.chunk_id, c.chunk_text, c.allowed_roles, c.metadata,
                   c.document_id, d.title AS document_title
            FROM chunk c
            JOIN document d ON d.document_id = c.document_id
            WHERE c.metadata->>'external_id' = ANY(%s)
            """,
            (chunk_external_ids,),
        )
        for row in cur.fetchall():
            meta = row.get("metadata") or {}
            chunks.append(
                {
                    "chunk_id": row["chunk_id"],
                    "external_id": meta.get("external_id") if isinstance(meta, dict) else None,
                    "chunk_text": row["chunk_text"],
                    "document_title": row.get("document_title"),
                    "document_id": row.get("document_id"),
                    "allowed_roles": list(row.get("allowed_roles") or []),
                    "vector_score": 0.0,
                    "graph_score": 1.0,
                    "source": "graph",
                }
            )

    if document_external_ids:
        cur.execute(
            """
            SELECT c.chunk_id, c.chunk_text, c.allowed_roles, c.metadata,
                   c.document_id, d.title AS document_title,
                   d.metadata->>'external_id' AS doc_external_id
            FROM chunk c
            JOIN document d ON d.document_id = c.document_id
            WHERE d.metadata->>'external_id' = ANY(%s)
            """,
            (document_external_ids,),
        )
        for row in cur.fetchall():
            meta = row.get("metadata") or {}
            chunks.append(
                {
                    "chunk_id": row["chunk_id"],
                    "external_id": meta.get("external_id") if isinstance(meta, dict) else None,
                    "chunk_text": row["chunk_text"],
                    "document_title": row.get("document_title"),
                    "document_id": row.get("document_id"),
                    "allowed_roles": list(row.get("allowed_roles") or []),
                    "vector_score": 0.0,
                    "graph_score": 0.8,
                    "source": "graph",
                }
            )

    return chunks


def expand_from_chunks(
    seed_chunks: list[ChunkContext],
    *,
    hops: int = EXPAND_HOPS,
    conn: psycopg.Connection | None = None,
    trace_id: str | None = None,
) -> tuple[list[GraphNodeContext], list[ChunkContext]]:
    seed_node_ids: list[str] = []
    for ch in seed_chunks:
        ext = ch.get("external_id")
        if ext:
            seed_node_ids.append(_chunk_node_id(ext))

    if not seed_node_ids:
        return [], []

    def _run(connection: psycopg.Connection) -> tuple[list[GraphNodeContext], list[ChunkContext]]:
        with connection.cursor() as cur:
            node_rows = _fetch_reachable_nodes(
                cur,
                seed_node_ids,
                hops=hops,
                edge_types=EXPAND_EDGE_TYPES,
            )
            all_nodes: list[GraphNodeContext] = [
                {
                    "node_id": row["node_id"],
                    "node_type": row["node_type"],
                    "label": row["label"],
                    "ref_table": row.get("ref_table"),
                    "ref_id": row.get("ref_id"),
                }
                for row in node_rows
            ]
            graph_chunks = _chunks_for_nodes(cur, node_rows)

        return all_nodes, graph_chunks

    if conn is not None:
        with traced_span("rag.graph_expand_db", attributes={"rag.trace_id": trace_id or ""}):
            result = _run(conn)
            if trace_id:
                log_rag_step(
                    trace_id,
                    "graph_expand_db",
                    hops=hops,
                    nodes=len(result[0]),
                    chunks=len(result[1]),
                )
        return result

    with get_connection() as connection:
        return expand_from_chunks(seed_chunks, hops=hops, conn=connection, trace_id=trace_id)
