from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import api_router
from .core.config import settings
from .core.logging import configure_logging

configure_logging()

app = FastAPI(title=settings.project_name, docs_url=f"{settings.api_v1_str}/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": settings.project_name, "status": "ok"}
