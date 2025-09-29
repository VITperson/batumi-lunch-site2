from __future__ import annotations

from enum import Enum as PyEnum
from typing import List

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRole(str, PyEnum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    external_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    telegram_id: Mapped[int | None] = mapped_column(index=True, unique=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True, unique=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_guest: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    orders: Mapped[List["Order"]] = relationship(back_populates="user", lazy="selectin")
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", lazy="selectin")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="user", lazy="selectin")


from .orders import Order  # noqa: E402
from .address import Address  # noqa: E402
from .subscriptions import Subscription  # noqa: E402
