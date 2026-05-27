from __future__ import annotations

from typing import Any, TypedDict


class ChunkContext(TypedDict, total=False):
    chunk_id: int
    external_id: str
    chunk_text: str
    document_title: str
    document_id: int
    allowed_roles: list[str]
    vector_score: float
    graph_score: float
    final_score: float
    source: str


class GraphNodeContext(TypedDict, total=False):
    node_id: str
    node_type: str
    label: str
    ref_table: str | None
    ref_id: str | None


class Citation(TypedDict, total=False):
    chunk_id: int | None
    external_id: str | None
    document_title: str | None
    node_id: str | None
    node_type: str | None
    label: str | None


class AskState(TypedDict, total=False):
    trace_id: str
    query: str
    role: str
    blocked: bool
    block_reason: str | None
    intent: str | None
    demo_inn: str | None
    retrieved_chunks: list[ChunkContext]
    expanded_nodes: list[GraphNodeContext]
    context_chunks: list[ChunkContext]
    citations: list[Citation]
    answer: str | None
    audit_steps: list[str]


def audit(state: AskState, step: str, detail: str = "") -> dict[str, Any]:
    msg = f"{step}" + (f": {detail}" if detail else "")
    steps = list(state.get("audit_steps") or [])
    steps.append(msg)
    return {"audit_steps": steps}
