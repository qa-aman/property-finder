"""FastAPI entry point (presentation layer)."""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request

from property_finder.application.container import build_orchestrator
from property_finder.config import load_settings
from property_finder.domain.models import Shortlist, UserBrief

settings = load_settings()  # fail-fast: crashes here if config is bad


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Build the orchestrator once (also fail-fast for real adapters with missing keys).
    app.state.orchestrator = build_orchestrator(settings)
    yield


app = FastAPI(title="Property Finder POC", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str | None]:
    return {"status": "ok", "default_city": settings.default_city}


@app.post("/shortlist", response_model=Shortlist)
def shortlist(brief: UserBrief, request: Request) -> Shortlist:
    return request.app.state.orchestrator.run(brief)
