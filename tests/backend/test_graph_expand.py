from __future__ import annotations

import pytest

from backend.config import DEMO_INN
from backend.retrieval.graph_expand import expand_from_chunks
from backend.state import ChunkContext
from tests.backend.conftest import requires_db


def _seed_chunk(external_id: str = "ch_002") -> ChunkContext:
    return ChunkContext(
        chunk_id=1,
        external_id=external_id,
        chunk_text="seed",
        document_title="Policy",
        allowed_roles=["analyst", "risk_manager"],
        vector_score=0.9,
        graph_score=0.0,
        source="vector",
    )


def test_expand_empty_without_external_id():
    nodes, chunks = expand_from_chunks([ChunkContext(chunk_id=1, chunk_text="no ext")])
    assert nodes == []
    assert chunks == []


@requires_db
def test_expand_seed_only_hops_zero():
    from backend.db import get_connection

    with get_connection() as conn:
        nodes, chunks = expand_from_chunks([_seed_chunk()], hops=0, conn=conn)

    node_ids = {n["node_id"] for n in nodes}
    assert node_ids == {"chunk:ch_002"}
    assert len(chunks) == 1
    assert chunks[0].get("external_id") == "ch_002"


@requires_db
def test_expand_one_hop_from_ch_002():
    from backend.db import get_connection

    with get_connection() as conn:
        nodes, _ = expand_from_chunks([_seed_chunk()], hops=1, conn=conn)

    node_ids = {n["node_id"] for n in nodes}
    assert "chunk:ch_002" in node_ids
    assert any("policy_001" in nid for nid in node_ids)
    assert any("revenue_drop" in nid for nid in node_ids)
    if DEMO_INN:
        assert any(DEMO_INN in nid for nid in node_ids)
    assert not any("law_001" in nid for nid in node_ids)


@requires_db
def test_expand_two_hops_reaches_linked_document():
    from backend.db import get_connection

    with get_connection() as conn:
        nodes, _ = expand_from_chunks([_seed_chunk()], hops=2, conn=conn)

    node_ids = {n["node_id"] for n in nodes}
    assert any("law_001" in nid for nid in node_ids)


@requires_db
def test_expand_respects_edge_types(monkeypatch):
    import backend.retrieval.graph_expand as graph_expand_mod

    monkeypatch.setattr(graph_expand_mod, "EXPAND_EDGE_TYPES", ("BELONGS_TO",))

    from backend.db import get_connection

    with get_connection() as conn:
        nodes, _ = expand_from_chunks([_seed_chunk()], hops=1, conn=conn)

    node_ids = {n["node_id"] for n in nodes}
    assert "chunk:ch_002" in node_ids
    assert any("policy_001" in nid for nid in node_ids)
    assert not any("revenue_drop" in nid for nid in node_ids)
    if DEMO_INN:
        assert not any(DEMO_INN in nid for nid in node_ids)
