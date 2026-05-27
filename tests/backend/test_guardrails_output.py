from backend.guardrails.output import check_output


def test_accepts_answer_with_citations():
    ok, reason = check_output(
        "Answer text",
        [{"chunk_id": 1, "external_id": "ch_001"}],
    )
    assert ok is True
    assert reason is None


def test_blocks_without_citations():
    ok, reason = check_output("Answer without sources", [])
    assert ok is False
    assert reason == "no_citations"


def test_accepts_graph_node_citation():
    ok, reason = check_output(
        "Answer",
        [{"node_id": "document:policy_001", "node_type": "Document"}],
    )
    assert ok is True
