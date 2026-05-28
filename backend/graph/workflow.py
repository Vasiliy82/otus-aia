from __future__ import annotations

import logging
import time
import uuid
from functools import lru_cache
from typing import Literal

from langgraph.graph import END, StateGraph

from backend.config import DEMO_INN
from backend.guardrails.input import check_input
from backend.guardrails.output import check_output
from backend.llm.mock import MockLLMClient
from backend.observability.logging import log_rag_step
from backend.observability.tracing import current_trace_id_hex, get_tracer, traced_span
from backend.rbac.filter import filter_chunks_by_role
from backend.rerank.score import dedupe_chunks, rerank_chunks
from backend.retrieval.graph_expand import expand_from_chunks
from backend.retrieval.vector import vector_search
from backend.state import AskState, audit

logger = logging.getLogger(__name__)

_llm = MockLLMClient()


def _blocked_route(state: AskState) -> Literal["blocked", "ok"]:
    return "blocked" if state.get("blocked") else "ok"


def _trace_id(state: AskState) -> str:
    return state.get("trace_id") or ""


def node_input_guardrails(state: AskState) -> dict:
    trace_id = _trace_id(state)
    with traced_span("rag.input_guardrails", attributes={"rag.trace_id": trace_id}):
        ok, reason = check_input(state.get("query", ""))
        log_rag_step(
            trace_id,
            "input_guardrails",
            ok=ok,
            blocked=not ok,
            reason=reason,
        )
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
    trace_id = _trace_id(state)
    with traced_span("rag.classify_intent", attributes={"rag.trace_id": trace_id}):
        q = (state.get("query") or "").lower()
        intent = "general"
        if any(w in q for w in ("риск", "risk", "выручк", "revenue", "ромашк")):
            intent = "risk_analysis"
        elif any(w in q for w in ("закон", "норм", "политик", "policy")):
            intent = "compliance"
        demo_inn = DEMO_INN or None
        log_rag_step(trace_id, "classify_intent", intent=intent, demo_inn=demo_inn)
        return audit(
            state,
            "classify_intent",
            intent,
        ) | {"intent": intent, "demo_inn": demo_inn}


def node_vector_retrieve(state: AskState) -> dict:
    trace_id = _trace_id(state)
    started = time.perf_counter()
    with traced_span("rag.vector_retrieve", attributes={"rag.trace_id": trace_id}):
        chunks = vector_search(state.get("query", ""), trace_id=trace_id)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_rag_step(
            trace_id,
            "vector_retrieve",
            chunks=len(chunks),
            chunk_ids=[c.get("chunk_id") for c in chunks],
            scores=[c.get("vector_score") for c in chunks],
            duration_ms=duration_ms,
        )
        return audit(state, "vector_retrieve", f"{len(chunks)} chunks") | {
            "retrieved_chunks": chunks,
        }


def node_graph_expand(state: AskState) -> dict:
    trace_id = _trace_id(state)
    seeds = state.get("retrieved_chunks") or []
    started = time.perf_counter()
    with traced_span(
        "rag.graph_expand",
        attributes={"rag.trace_id": trace_id, "rag.seed_count": len(seeds)},
    ):
        nodes, extra_chunks = expand_from_chunks(seeds, trace_id=trace_id)
        merged = dedupe_chunks(list(seeds) + extra_chunks)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_rag_step(
            trace_id,
            "graph_expand",
            seed_count=len(seeds),
            node_ids=[n.get("node_id") for n in nodes],
            extra_chunks=len(extra_chunks),
            merged_chunks=len(merged),
            duration_ms=duration_ms,
        )
        return audit(
            state,
            "graph_expand",
            f"{len(nodes)} nodes, {len(extra_chunks)} graph chunks",
        ) | {
            "expanded_nodes": nodes,
            "context_chunks": merged,
        }


def node_rbac_filter(state: AskState) -> dict:
    trace_id = _trace_id(state)
    role = state.get("role", "analyst")
    chunks = state.get("context_chunks") or state.get("retrieved_chunks") or []
    with traced_span(
        "rag.rbac_filter",
        attributes={"rag.trace_id": trace_id, "rag.role": role},
    ):
        filtered = filter_chunks_by_role(chunks, role)
        log_rag_step(
            trace_id,
            "rbac_filter",
            role=role,
            before=len(chunks),
            after=len(filtered),
        )
        return audit(state, "rbac_filter", f"{len(filtered)}/{len(chunks)} allowed") | {
            "context_chunks": filtered,
        }


def node_rerank(state: AskState) -> dict:
    trace_id = _trace_id(state)
    with traced_span("rag.rerank", attributes={"rag.trace_id": trace_id}):
        chunks = rerank_chunks(state.get("context_chunks") or [])
        log_rag_step(
            trace_id,
            "rerank",
            ranked=len(chunks),
            top=[
                {
                    "chunk_id": c.get("chunk_id"),
                    "final_score": round(
                        float(c.get("vector_score") or 0) + 0.5 * float(c.get("graph_score") or 0),
                        4,
                    ),
                }
                for c in chunks[:5]
            ],
        )
        return audit(state, "rerank", f"{len(chunks)} ranked") | {"context_chunks": chunks}


def node_generate_answer(state: AskState) -> dict:
    trace_id = _trace_id(state)
    with traced_span("rag.generate_answer", attributes={"rag.trace_id": trace_id}):
        answer = _llm.generate(state)
        citations = _llm.build_citations(state)
        log_rag_step(
            trace_id,
            "generate_answer",
            answer_len=len(answer),
            citations_count=len(citations),
        )
        return audit(state, "generate_answer") | {
            "answer": answer,
            "citations": citations,
        }


def node_output_guardrails(state: AskState) -> dict:
    trace_id = _trace_id(state)
    with traced_span("rag.output_guardrails", attributes={"rag.trace_id": trace_id}):
        ok, reason = check_output(state.get("answer"), state.get("citations") or [])
        log_rag_step(
            trace_id,
            "output_guardrails",
            ok=ok,
            blocked=not ok,
            reason=reason,
        )
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
    trace_id = _trace_id(state)
    with traced_span("rag.blocked_end", attributes={"rag.trace_id": trace_id}):
        log_rag_step(
            trace_id,
            "blocked_end",
            block_reason=state.get("block_reason"),
        )
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


@lru_cache(maxsize=1)
def get_workflow():
    return build_workflow()


def warmup_workflow() -> None:
    get_workflow()


def run_ask(query: str, role: str, *, trace_id: str | None = None) -> AskState:
    workflow = get_workflow()
    tracer = get_tracer()
    initial_trace_id = trace_id or str(uuid.uuid4())

    with tracer.start_as_current_span(
        "rag.ask",
        attributes={"rag.role": role, "rag.query_len": len(query)},
    ) as root_span:
        otel_trace_id = current_trace_id_hex()
        effective_trace_id = otel_trace_id or initial_trace_id
        root_span.set_attribute("rag.trace_id", effective_trace_id)

        initial: AskState = {
            "trace_id": effective_trace_id,
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

    log_rag_step(
        effective_trace_id,
        "ask_complete",
        role=role,
        blocked=result.get("blocked"),
        steps=len(result.get("audit_steps") or []),
    )
    logger.info(
        "ask_complete trace_id=%s role=%s blocked=%s steps=%s",
        result.get("trace_id"),
        role,
        result.get("blocked"),
        len(result.get("audit_steps") or []),
    )
    return result
