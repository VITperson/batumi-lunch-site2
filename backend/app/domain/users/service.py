from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta
from typing import Dict

from fastapi import HTTPException, status

from ...core.logging import get_logger

logger = get_logger(__name__)


class GuestAuthService:
    """Temporary in-memory guest auth store. Replace with Redis/SMS provider integration."""

    def __init__(self) -> None:
        self._requests: Dict[str, dict] = {}

    def start(self, phone: str) -> dict:
        if not phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone is required")
        request_id = secrets.token_urlsafe(8)
        code = "".join(secrets.choice(string.digits) for _ in range(4))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        self._requests[request_id] = {"phone": phone, "code": code, "expires_at": expires_at}
        logger.info("guest_auth_request_created", extra={"phone": phone, "request_id": request_id})
        # TODO: integrate real SMS provider
        return {"request_id": request_id, "expires_at": expires_at, "debug_code": code}

    def confirm(self, request_id: str, code: str) -> dict:
        payload = self._requests.get(request_id)
        if not payload:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        if datetime.utcnow() > payload["expires_at"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code expired")
        if payload["code"] != code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
        token = secrets.token_urlsafe(24)
        refresh = secrets.token_urlsafe(32)
        logger.info("guest_auth_confirmed", extra={"phone": payload['phone'], "request_id": request_id})
        return {
            "access_token": token,
            "refresh_token": refresh,
            "expires_in": 60 * 60,
        }


guest_auth_service = GuestAuthService()
