from __future__ import annotations

import logging

from backend.embeddings.model import get_embedding_model
from backend.graph.workflow import warmup_workflow

logger = logging.getLogger(__name__)

model_loaded = False
workflow_ready = False
startup_error: str | None = None


def initialize_backend() -> None:
    global model_loaded, workflow_ready, startup_error

    model_loaded = False
    workflow_ready = False
    startup_error = None

    try:
        logger.info("Initializing embedding model")
        model = get_embedding_model()
        logger.info("Loading SentenceTransformer model from %s", model.model_name)
        model.encode_one("warmup")
        model_loaded = True
        logger.info("Embedding model ready dim=%s", model.dimension)
    except Exception as exc:
        startup_error = f"embedding model: {exc}"
        logger.error("Failed to initialize embedding model: %s", exc)

    try:
        warmup_workflow()
        workflow_ready = True
        logger.info("LangGraph workflow compiled")
    except Exception as exc:
        if startup_error:
            startup_error = f"{startup_error}; workflow: {exc}"
        else:
            startup_error = f"workflow: {exc}"
        logger.error("Failed to compile LangGraph workflow: %s", exc)
