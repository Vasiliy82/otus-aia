from __future__ import annotations

import logging
import uuid
from typing import Literal

from langgraph.graph import END, StateGraph

from backend.config import DEMO_INN
from backend.guardrails.input import check_input
from backend.guardrails.output import check_output
from backend.llm.mock import MockLLMClient
from backend.rbac.filter import filter_chunks_by_role
from backend.rerank.score import dedupe_chunks, rerank_chunks
from backend.retrieval.graph_expand import expand_from_chunks
from backend.retrieval.vector import vector_search
from backend.state import AskState, audit

logger = logging.getLogger(__name__)

_llm = MockLLMClient()


def _blocked_route(state: AskState) -> Literal["blocked", "ok"]:
    return "blocked" if state.get("blocked") else "ok"


def node_input_guardrails(state: AskState) -> dict:
    ok, reason = check_input(state.get("query", ""))
    update: dict = audit(state, "input_guardrails", "ok" if ok else reason or "blocked")
    if not ok:
        update.update(
            {
                "blocked": True,
                "block_reason": reason,
                "answer": "Запрос отклонён политикой безопасности (input guardrail).",
                "citations": [],
            }
        )
    else:
        update["blocked"] = False
    return update


def node_classify_intent(state: AskState) -> dict:
    q = (state.get("query") or "").lower()
    intent = "general"
    if any(w in q for w in ("риск", "risk", "выручк", "revenue", "ромашк")):
        intent = "risk_analysis"
    elif any(w in q for w in ("закон", "норм", "политик", "policy")):
        intent = "compliance"
    demo_inn = DEMO_INN or None
    return audit(
        state,
        "classify_intent",
        intent,
    ) | {"intent": intent, "demo_inn": demo_inn}


def node_vector_retrieve(state: AskState) -> dict:
    chunks = vector_search(state.get("query", ""))
    return audit(state, "vector_retrieve", f"{len(chunks)} chunks") | {
        "retrieved_chunks": chunks,
    }


def node_graph_expand(state: AskState) -> dict:
    seeds = state.get("retrieved_chunks") or []
    nodes, extra_chunks = expand_from_chunks(seeds)
    merged = dedupe_chunks(list(seeds) + extra_chunks)
    return audit(
        state,
        "graph_expand",
        f"{len(nodes)} nodes, {len(extra_chunks)} graph chunks",
    ) | {
        "expanded_nodes": nodes,
        "context_chunks": merged,
    }


def node_rbac_filter(state: AskState) -> dict:
    role = state.get("role", "analyst")
    chunks = state.get("context_chunks") or state.get("retrieved_chunks") or []
    filtered = filter_chunks_by_role(chunks, role)
    return audit(state, "rbac_filter", f"{len(filtered)}/{len(chunks)} allowed") | {
        "context_chunks": filtered,
    }


def node_rerank(state: AskState) -> dict:
    chunks = rerank_chunks(state.get("context_chunks") or [])
    return audit(state, "rerank", f"{len(chunks)} ranked") | {"context_chunks": chunks}


def node_generate_answer(state: AskState) -> dict:
    answer = _llm.generate(state)
    citations = _llm.build_citations(state)
    return audit(state, "generate_answer") | {
        "answer": answer,
        "citations": citations,
    }


def node_output_guardrails(state: AskState) -> dict:
    ok, reason = check_output(state.get("answer"), state.get("citations") or [])
    update = audit(state, "output_guardrails", "ok" if ok else reason or "blocked")
    if not ok:
        update.update(
            {
                "blocked": True,
                "block_reason": reason,
                "answer": "Ответ заблокирован: отсутствуют обязательные ссылки на источники.",
                "citations": [],
            }
        )
    return update


def node_blocked_end(state: AskState) -> dict:
    return audit(state, "blocked_end")


def build_workflow():
    graph = StateGraph(AskState)
    graph.add_node("input_guardrails", node_input_guardrails)
    graph.add_node("classify_intent", node_classify_intent)
    graph.add_node("vector_retrieve", node_vector_retrieve)
    graph.add_node("graph_expand", node_graph_expand)
    graph.add_node("rbac_filter", node_rbac_filter)
    graph.add_node("rerank", node_rerank)
    graph.add_node("generate_answer", node_generate_answer)
    graph.add_node("output_guardrails", node_output_guardrails)
    graph.add_node("blocked_end", node_blocked_end)

    graph.set_entry_point("input_guardrails")
    graph.add_conditional_edges(
        "input_guardrails",
        _blocked_route,
        {"blocked": "blocked_end", "ok": "classify_intent"},
    )
    graph.add_edge("blocked_end", END)
    graph.add_edge("classify_intent", "vector_retrieve")
    graph.add_edge("vector_retrieve", "graph_expand")
    graph.add_edge("graph_expand", "rbac_filter")
    graph.add_edge("rbac_filter", "rerank")
    graph.add_edge("rerank", "generate_answer")
    graph.add_edge("generate_answer", "output_guardrails")
    graph.add_edge("output_guardrails", END)

    return graph.compile()


def run_ask(query: str, role: str, *, trace_id: str | None = None) -> AskState:
    workflow = build_workflow()
    initial: AskState = {
        "trace_id": trace_id or str(uuid.uuid4()),
        "query": query,
        "role": role,
        "blocked": False,
        "block_reason": None,
        "retrieved_chunks": [],
        "expanded_nodes": [],
        "context_chunks": [],
        "citations": [],
        "audit_steps": [],
    }
    result = workflow.invoke(initial)
    logger.info(
        "trace_id=%s role=%s blocked=%s steps=%s",
        result.get("trace_id"),
        role,
        result.get("blocked"),
        len(result.get("audit_steps") or []),
    )
    return result
