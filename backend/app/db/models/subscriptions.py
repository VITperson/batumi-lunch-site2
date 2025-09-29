from __future__ import annotations

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, DateTime, Enum, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:  # pragma: no cover
    from .orders import Order
    from .payments import PaymentIntent
    from .payments import PaymentToken
    from .user import User


class SubscriptionStatus(str, PyEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("order_templates.id", ondelete="SET NULL"))
    payment_token_id: Mapped[int | None] = mapped_column(ForeignKey("payment_tokens.id", ondelete="SET NULL"))
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    current_week_start: Mapped[date | None] = mapped_column(Date)
    next_charge_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pause_until: Mapped[date | None] = mapped_column(Date)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped["User"] = relationship(back_populates="subscriptions", lazy="selectin")
    template: Mapped["OrderTemplate" | None] = relationship(lazy="selectin")
    payment_token: Mapped["PaymentToken" | None] = relationship(lazy="selectin")
    weeks: Mapped[List["SubscriptionWeek"]] = relationship(back_populates="subscription", cascade="all, delete-orphan", lazy="selectin")
    payment_intents: Mapped[List["PaymentIntent"]] = relationship(lazy="selectin")


class SubscriptionWeek(Base):
    __tablename__ = "subscription_weeks"

    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="scheduled", nullable=False)
    subtotal_lari: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))

    subscription: Mapped[Subscription] = relationship(back_populates="weeks")
    order: Mapped["Order" | None] = relationship(lazy="selectin")
