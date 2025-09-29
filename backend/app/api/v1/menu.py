from __future__ import annotations

from datetime import date

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.deps import get_session
from ...db.models.menu import MenuWeek, Preset
from ..v1.schemas import MenuWeekOut, MenuWeeksResponse, PresetOut

router = APIRouter()


def _serialize_menu_week(menu: MenuWeek) -> MenuWeekOut:
    return MenuWeekOut(
        id=menu.id,
        week_start=menu.week_start,
        title=menu.title,
        description=menu.description,
        is_published=menu.is_published,
        order_deadline_hour=menu.order_deadline_hour,
        base_price_lari=float(menu.base_price_lari),
        day_offers=[
            {
                "id": offer.id,
                "day_of_week": offer.day_of_week,
                "items": offer.items or [],
                "calories": offer.calories,
                "allergy_tag_ids": offer.allergy_tag_ids or [],
                "price_lari": float(offer.price_lari) if offer.price_lari is not None else None,
                "status": offer.status.value,
                "portion_limit": offer.portion_limit,
                "sold_out": offer.sold_out,
                "photo_url": offer.photo_url,
            }
            for offer in sorted(menu.day_offers, key=lambda o: o.day_of_week)
        ],
    )


@router.get("/week", response_model=MenuWeekOut)
async def get_week_menu(
    session: AsyncSession = Depends(get_session),
    week_start: date | None = Query(default=None, description="ISO date of week start"),
) -> MenuWeekOut:
    stmt = select(MenuWeek).order_by(MenuWeek.week_start.desc())
    if week_start:
        stmt = select(MenuWeek).where(MenuWeek.week_start == week_start)
    result = await session.execute(stmt)
    menu_week = result.scalars().unique().first()
    if not menu_week:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    await session.refresh(menu_week, attribute_names=["day_offers"])
    return _serialize_menu_week(menu_week)


@router.get("/weeks", response_model=MenuWeeksResponse)
async def list_weeks(session: AsyncSession = Depends(get_session), limit: int = Query(default=8, ge=1, le=16)) -> MenuWeeksResponse:
    stmt = select(MenuWeek).order_by(MenuWeek.week_start.desc()).limit(limit)
    result = await session.execute(stmt)
    weeks = result.scalars().unique().all()
    for week in weeks:
        await session.refresh(week, attribute_names=["day_offers"])
    return MenuWeeksResponse(weeks=[_serialize_menu_week(week) for week in weeks])


@router.get("/presets", response_model=list[PresetOut])
async def list_presets(session: AsyncSession = Depends(get_session)) -> list[PresetOut]:
    stmt = select(Preset).where(Preset.is_active.is_(True))
    result = await session.execute(stmt)
    presets = result.scalars().all()
    return [
        PresetOut(
            id=preset.id,
            slug=preset.slug,
            name=preset.name,
            description=preset.description,
            default_portions=preset.default_portions,
            day_selection=preset.day_selection or [],
            discount_percent=preset.discount_percent,
        )
        for preset in presets
    ]
