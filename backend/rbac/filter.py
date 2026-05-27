from __future__ import annotations

from backend.state import ChunkContext


def chunk_accessible(chunk: ChunkContext, role: str) -> bool:
    roles = chunk.get("allowed_roles") or []
    return role in roles


def filter_chunks_by_role(chunks: list[ChunkContext], role: str) -> list[ChunkContext]:
    return [c for c in chunks if chunk_accessible(c, role)]
