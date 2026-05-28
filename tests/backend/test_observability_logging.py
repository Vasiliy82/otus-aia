from __future__ import annotations

import json
import logging

from backend.observability.logging import JsonFormatter, log_rag_step


def test_log_rag_step_json_format(caplog):
    caplog.set_level(logging.INFO, logger="backend.rag")
    log_rag_step("abc123", "vector_retrieve", chunks=3, chunk_ids=[1, 2, 3])
    assert len(caplog.records) == 1
    record = caplog.records[0]
    payload = json.loads(JsonFormatter().format(record))
    assert payload["event"] == "rag_step"
    assert payload["trace_id"] == "abc123"
    assert payload["step"] == "vector_retrieve"
    assert payload["chunks"] == 3
    assert payload["chunk_ids"] == [1, 2, 3]
