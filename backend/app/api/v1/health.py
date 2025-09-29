from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", summary="Liveness probe")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", summary="Readiness probe")
async def readyz() -> dict[str, str]:
    return {"status": "ready"}
