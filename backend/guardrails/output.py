from __future__ import annotations

from backend.state import Citation


def check_output(answer: str | None, citations: list[Citation]) -> tuple[bool, str | None]:
    if not answer or not answer.strip():
        return False, "empty_answer"
    chunk_citations = [
        c for c in citations if c.get("chunk_id") is not None or c.get("external_id")
    ]
    node_citations = [c for c in citations if c.get("node_id")]
    if not chunk_citations and not node_citations:
        return False, "no_citations"
    return True, None
