from __future__ import annotations

import logging

from fastapi import APIRouter

from backend.api.schemas import AskRequest, AskResponse, HealthResponse, state_to_response
from backend.graph.workflow import run_ask

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    state = run_ask(body.query, body.role)
    return state_to_response(state)
