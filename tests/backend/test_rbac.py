from backend.rbac.filter import chunk_accessible, filter_chunks_by_role


def _chunk(roles: list[str], external_id: str = "ch_x"):
    return {
        "chunk_id": 1,
        "external_id": external_id,
        "allowed_roles": roles,
        "chunk_text": "text",
    }


def test_analyst_cannot_access_secret_chunk():
    chunks = [
        _chunk(["analyst", "risk_manager"], "ch_001"),
        _chunk(["risk_manager"], "ch_003"),
    ]
    filtered = filter_chunks_by_role(chunks, "analyst")
    assert len(filtered) == 1
    assert filtered[0]["external_id"] == "ch_001"
    assert not chunk_accessible(_chunk(["risk_manager"], "ch_003"), "analyst")


def test_risk_manager_sees_secret_chunk():
    chunks = [
        _chunk(["analyst", "risk_manager"], "ch_002"),
        _chunk(["risk_manager"], "ch_003"),
    ]
    filtered = filter_chunks_by_role(chunks, "risk_manager")
    assert len(filtered) == 2
    ids = {c["external_id"] for c in filtered}
    assert "ch_003" in ids
