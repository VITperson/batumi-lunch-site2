from fastapi import APIRouter

from .schemas import (
    GuestAuthConfirmRequest,
    GuestAuthConfirmResponse,
    GuestAuthStartRequest,
    GuestAuthStartResponse,
)
from ...domain.users.service import guest_auth_service

router = APIRouter()


@router.post("/guest/start", response_model=GuestAuthStartResponse)
async def start_guest_auth(payload: GuestAuthStartRequest) -> GuestAuthStartResponse:
    data = guest_auth_service.start(payload.phone)
    return GuestAuthStartResponse(**{k: v for k, v in data.items() if k in {"request_id", "expires_at"}})


@router.post("/guest/confirm", response_model=GuestAuthConfirmResponse)
async def confirm_guest_auth(payload: GuestAuthConfirmRequest) -> GuestAuthConfirmResponse:
    tokens = guest_auth_service.confirm(payload.request_id, payload.code)
    # TODO: persist user + tokens
    return GuestAuthConfirmResponse(**tokens)
