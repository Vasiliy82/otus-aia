from __future__ import annotations

from backend.state import ChunkContext


def dedupe_chunks(chunks: list[ChunkContext]) -> list[ChunkContext]:
    seen: set[int] = set()
    result: list[ChunkContext] = []
    for ch in chunks:
        cid = ch.get("chunk_id")
        if cid is None or cid in seen:
            continue
        seen.add(cid)
        result.append(ch)
    return result


def rerank_chunks(chunks: list[ChunkContext]) -> list[ChunkContext]:
    """Deterministic rerank: vector_score + graph_score (ADR-007)."""
    unique = dedupe_chunks(chunks)
    for ch in unique:
        v = float(ch.get("vector_score") or 0.0)
        g = float(ch.get("graph_score") or 0.0)
        ch["final_score"] = round(v + 0.5 * g, 6)
    return sorted(unique, key=lambda c: float(c.get("final_score") or 0.0), reverse=True)
