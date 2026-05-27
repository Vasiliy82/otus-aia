from backend.rerank.score import dedupe_chunks, rerank_chunks


def test_dedupe_and_rerank():
    chunks = [
        {"chunk_id": 1, "vector_score": 0.5, "graph_score": 0.0},
        {"chunk_id": 1, "vector_score": 0.9, "graph_score": 0.0},
        {"chunk_id": 2, "vector_score": 0.3, "graph_score": 1.0},
    ]
    ranked = rerank_chunks(chunks)
    assert len(ranked) == 2
    assert ranked[0]["chunk_id"] == 2
    assert ranked[0]["final_score"] == 0.3 + 0.5 * 1.0


def test_dedupe_only():
    chunks = [{"chunk_id": 1}, {"chunk_id": 1}, {"chunk_id": 2}]
    assert len(dedupe_chunks(chunks)) == 2
