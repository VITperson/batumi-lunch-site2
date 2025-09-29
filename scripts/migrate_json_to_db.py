#!/usr/bin/env python
"""Placeholder script to migrate legacy JSON files into the database.

TODO: implement JSON → Postgres migration once production data samples become available.
The script should read users.json, orders.json, menu.json and order_window.json,
perform UPSERT operations and keep an audit trail of migrated records.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from backend.app.db.base import Base
from backend.app.db.models.menu import MenuWeek
from backend.app.db.session import engine


async def ensure_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main() -> None:
    await ensure_schema()
    async with engine.begin() as conn:
        result = await conn.execute(select(MenuWeek).limit(1))
        if result.first():
            print("Database already seeded; JSON migration pending implementation.")
        else:
            print("No menu weeks found. TODO: perform migration from JSON files.")


if __name__ == "__main__":
    asyncio.run(main())
