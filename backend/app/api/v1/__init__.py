from fastapi import APIRouter

from . import auth, health, menu, orders, subscriptions

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])  # type: ignore[arg-type]
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])  # type: ignore[arg-type]
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])  # type: ignore[arg-type]
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])  # type: ignore[arg-type]
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])  # type: ignore[arg-type]
