#!/usr/bin/env python
from __future__ import annotations

import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from backend.app.db.base import Base
from backend.app.db.models.menu import DayOffer, MenuWeek
from backend.app.db.session import engine, SessionLocal


async def seed_menu() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        exists = await session.execute(select(MenuWeek).where(MenuWeek.week_start == week_start))
        if exists.scalars().first():
            print("Menu already seeded")
            return
        menu = MenuWeek(week_start=week_start, title="Автогенерация", is_published=True)
        menu.day_offers = [
            DayOffer(day_of_week=day, items=[f"Блюдо {idx+1}"]) for idx, day in enumerate(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"])
        ]
        session.add(menu)
        await session.commit()
        print("Seeded default menu")


if __name__ == "__main__":
    asyncio.run(seed_menu())
