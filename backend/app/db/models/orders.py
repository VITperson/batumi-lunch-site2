from __future__ import annotations

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:  # pragma: no cover
    from .payments import PaymentIntent
    from .user import User


class OrderStatus(str, PyEnum):
    NEW = "new"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    CANCELLED_BY_USER = "cancelled_by_user"
    FAILED = "failed"


class Order(Base):
    __tablename__ = "orders"

    order_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"))
    menu_week_id: Mapped[int | None] = mapped_column(ForeignKey("menu_weeks.id", ondelete="SET NULL"))
    template_id: Mapped[int | None] = mapped_column(ForeignKey("order_templates.id", ondelete="SET NULL"))
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(16), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    items: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.NEW, nullable=False)
    price_lari: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_lari: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    promo_code: Mapped[str | None] = mapped_column(String(64))
    delivery_slot_id: Mapped[int | None] = mapped_column(ForeignKey("delivery_slots.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(String(512))
    is_next_week: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checkout_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[Optional["User"]] = relationship(back_populates="orders", lazy="selectin")
    template: Mapped[Optional["OrderTemplate"]] = relationship(back_populates="orders", lazy="selectin")
    week_selections: Mapped[List["WeekSelection"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    payment_intents: Mapped[List["PaymentIntent"]] = relationship(back_populates="order", lazy="selectin")


class OrderTemplate(Base):
    __tablename__ = "order_templates"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    repeat_weeks: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    repeat_days: Mapped[list[str]] = mapped_column(JSON, default=list)
    default_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    orders: Mapped[List[Order]] = relationship(back_populates="template", lazy="selectin")
    user: Mapped["User"] = relationship(lazy="selectin")


class WeekSelection(Base):
    __tablename__ = "week_selections"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    subtotal_lari: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    order: Mapped[Order] = relationship(back_populates="week_selection")
