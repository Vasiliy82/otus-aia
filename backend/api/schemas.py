from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    role: Literal["analyst", "risk_manager"] = "analyst"


class CitationModel(BaseModel):
    chunk_id: int | None = None
    external_id: str | None = None
    document_title: str | None = None
    node_id: str | None = None
    node_type: str | None = None
    label: str | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationModel]
    trace_id: str
    blocked: bool = False
    reason: str | None = None
    audit_steps: list[str] = Field(default_factory=list)
    intent: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool = False
    workflow_ready: bool = False
    ready: bool = False
    error: str | None = None


def state_to_response(state: dict[str, Any]) -> AskResponse:
    citations = [
        CitationModel(**{k: v for k, v in c.items() if k in CitationModel.model_fields})
        for c in (state.get("citations") or [])
    ]
    return AskResponse(
        answer=state.get("answer") or "",
        citations=citations,
        trace_id=state.get("trace_id") or "",
        blocked=bool(state.get("blocked")),
        reason=state.get("block_reason"),
        audit_steps=list(state.get("audit_steps") or []),
        intent=state.get("intent"),
    )
