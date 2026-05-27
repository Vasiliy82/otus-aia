import pytest

from tests.backend.conftest import requires_embeddings

pytestmark = requires_embeddings


def test_analyst_excludes_ch_003():
    from backend.graph.workflow import run_ask

    state = run_ask("Снижение выручки и внутренняя политика банка", "analyst")
    assert state["blocked"] is False
    chunk_refs = [
        c.get("external_id")
        for c in (state.get("citations") or [])
        if c.get("external_id")
    ]
    context_refs = [c.get("external_id") for c in (state.get("context_chunks") or [])]
    assert "ch_003" not in chunk_refs
    assert "ch_003" not in context_refs


def test_risk_manager_includes_ch_003():
    from backend.graph.workflow import run_ask

    state = run_ask("Секретная методика оценки финансового риска", "risk_manager")
    assert state["blocked"] is False
    refs = {c.get("external_id") for c in (state.get("citations") or [])}
    context_refs = {c.get("external_id") for c in (state.get("context_chunks") or [])}
    assert "ch_003" in refs or "ch_003" in context_refs


def test_graph_expansion_adds_related_nodes():
    from backend.graph.workflow import run_ask

    state = run_ask("Политика оценки контрагентов при снижении выручки", "analyst")
    node_ids = {n.get("node_id") for n in (state.get("expanded_nodes") or [])}
    assert any("policy_001" in (nid or "") for nid in node_ids)
