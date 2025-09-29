from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:  # pragma: no cover
    from .orders import Order
    from .subscriptions import Subscription
    from .user import User


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    REQUIRES_ACTION = "requires_action"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), index=True)
    subscription_id: Mapped[int | None] = mapped_column(ForeignKey("subscriptions.id", ondelete="SET NULL"), index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_intent_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount_lari: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="GEL", nullable=False)
    client_secret: Mapped[str | None] = mapped_column(String(255))
    return_url: Mapped[str | None] = mapped_column(String(255))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order: Mapped[Optional["Order"]] = relationship(lazy="selectin")
    subscription: Mapped[Optional["Subscription"]] = relationship(lazy="selectin")

class PaymentToken(Base):
    __tablename__ = "payment_tokens"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    last4: Mapped[str | None] = mapped_column(String(4))
    brand: Mapped[str | None] = mapped_column(String(32))
    exp_month: Mapped[int | None] = mapped_column(Integer)
    exp_year: Mapped[int | None] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(lazy="selectin")
