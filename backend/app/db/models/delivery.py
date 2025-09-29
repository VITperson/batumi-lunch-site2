from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:  # pragma: no cover
    from .address import Address


class DeliveryZone(Base):
    __tablename__ = "delivery_zones"
    __table_args__ = (UniqueConstraint("slug", name="uq_delivery_zones_slug"),)

    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    minimum_order_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    addresses: Mapped[list["Address"]] = relationship(back_populates="delivery_zone", lazy="selectin")
    slots: Mapped[list["DeliverySlot"]] = relationship(back_populates="zone", cascade="all, delete-orphan", lazy="selectin")


class DeliverySlot(Base):
    __tablename__ = "delivery_slots"
    __table_args__ = (UniqueConstraint("zone_id", "label", name="uq_delivery_slots_zone_label"),)

    zone_id: Mapped[int] = mapped_column(ForeignKey("delivery_zones.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    window_start: Mapped[str] = mapped_column(String(16), nullable=False)
    window_end: Mapped[str] = mapped_column(String(16), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekdays: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    zone: Mapped["DeliveryZone"] = relationship(back_populates="slots")
