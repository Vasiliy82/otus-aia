from __future__ import annotations

import logging

from fastapi import FastAPI

from backend.api.routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

app = FastAPI(
    title="GraphRAG PoC",
    description="Secure on-prem GraphRAG assistant — PoC backend",
    version="0.1.0",
)
app.include_router(router)
