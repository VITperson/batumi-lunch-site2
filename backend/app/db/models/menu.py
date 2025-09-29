from __future__ import annotations

from datetime import date
from enum import Enum as PyEnum
from typing import List

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DayStatus(str, PyEnum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    CLOSED = "closed"


class MenuWeek(Base):
    __tablename__ = "menu_weeks"
    __table_args__ = (UniqueConstraint("week_start", name="uq_menu_weeks_week_start"),)

    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(512))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_deadline_hour: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    base_price_lari: Mapped[float] = mapped_column(Numeric(10, 2), default=15.0, nullable=False)

    day_offers: Mapped[List["DayOffer"]] = relationship(back_populates="menu_week", cascade="all, delete-orphan", lazy="selectin")
    presets: Mapped[List["Preset"]] = relationship(back_populates="menu_week", cascade="all, delete-orphan", lazy="selectin")


class DayOffer(Base):
    __tablename__ = "day_offers"
    __table_args__ = (UniqueConstraint("menu_week_id", "day_of_week", name="uq_day_offers_week_day"),)

    menu_week_id: Mapped[int] = mapped_column(ForeignKey("menu_weeks.id", ondelete="CASCADE"), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(16), nullable=False)
    items: Mapped[list[str]] = mapped_column(JSON, default=list)
    calories: Mapped[int | None] = mapped_column(Integer)
    allergy_tag_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    price_lari: Mapped[float | None] = mapped_column(Numeric(10, 2))
    status: Mapped[DayStatus] = mapped_column(Enum(DayStatus), default=DayStatus.AVAILABLE, nullable=False)
    portion_limit: Mapped[int | None] = mapped_column(Integer)
    sold_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(512))

    menu_week: Mapped[MenuWeek] = relationship(back_populates="day_offers")


class Preset(Base):
    __tablename__ = "presets"
    __table_args__ = (UniqueConstraint("menu_week_id", "slug", name="uq_presets_week_slug"),)

    menu_week_id: Mapped[int | None] = mapped_column(ForeignKey("menu_weeks.id", ondelete="SET NULL"))
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    default_portions: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    day_selection: Mapped[list[str]] = mapped_column(JSON, default=list)
    discount_percent: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    menu_week: Mapped[MenuWeek | None] = relationship(back_populates="presets")
