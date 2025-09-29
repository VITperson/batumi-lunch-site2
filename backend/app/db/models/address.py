from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from .delivery import DeliveryZone
    from .user import User


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = (UniqueConstraint("user_id", "label", name="uq_addresses_user_label"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(64), default="Дом", nullable=False)
    address_line: Mapped[str] = mapped_column(String(512), nullable=False)
    entrance: Mapped[str | None] = mapped_column(String(128))
    floor: Mapped[str | None] = mapped_column(String(64))
    apartment: Mapped[str | None] = mapped_column(String(64))
    instructions: Mapped[str | None] = mapped_column(String(512))
    delivery_zone_id: Mapped[int | None] = mapped_column(ForeignKey("delivery_zones.id"))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="addresses", lazy="joined")
    delivery_zone: Mapped["DeliveryZone" | None] = relationship(back_populates="addresses", lazy="selectin")
