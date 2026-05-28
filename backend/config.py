from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://otus:otus@localhost:5432/graphrag_poc",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "paraphrase-multilingual-MiniLM-L12-v2",
)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

TOP_K = int(os.getenv("VECTOR_TOP_K", "3"))
EXPAND_HOPS = int(os.getenv("GRAPH_EXPAND_HOPS", "1"))
EXPAND_EDGE_TYPES = tuple(
    t.strip()
    for t in os.getenv(
        "GRAPH_EXPAND_EDGE_TYPES",
        "BELONGS_TO,MENTIONS,LINKED_TO",
    ).split(",")
    if t.strip()
)

DEMO_INN = os.getenv("DEMO_INN", "")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

OTEL_TRACES_ENABLED = os.getenv("OTEL_TRACES_ENABLED", "true").lower() in (
    "1",
    "true",
    "yes",
)
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4317",
)
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "graphrag-poc")
JSON_LOGS = os.getenv("JSON_LOGS", "true").lower() in ("1", "true", "yes")
