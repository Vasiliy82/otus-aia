from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.config import JSON_LOGS
from backend.observability.logging import configure_logging
from backend.observability.tracing import setup_tracing
from backend.startup import initialize_backend


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_backend()
    yield


app = FastAPI(
    title="GraphRAG PoC",
    description="Secure on-prem GraphRAG assistant — PoC backend",
    version="0.1.0",
    lifespan=lifespan,
)

configure_logging(json_logs=JSON_LOGS)
setup_tracing(app)
app.include_router(router)
