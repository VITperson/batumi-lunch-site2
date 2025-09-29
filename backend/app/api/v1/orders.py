from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.deps import get_session
from ...db.models.menu import MenuWeek
from ...db.models.orders import Order, OrderStatus
from ..v1.schemas import (
    CalcOrderRequest,
    CalcOrderResponse,
    CalcOrderWeekBreakdown,
    CheckoutRequest,
    CheckoutResponse,
)
from ...domain.orders.calculator import BasketItem, OrderCalculator

router = APIRouter()


@router.post("/calc", response_model=CalcOrderResponse)
async def calculate_order(payload: CalcOrderRequest, session: AsyncSession = Depends(get_session)) -> CalcOrderResponse:
    if not payload.selections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No selections provided")

    weeks: list[CalcOrderWeekBreakdown] = []
    total = 0.0
    discount = 0.0
    promo_applied = False

    for idx in range(payload.weeks_ahead):
        week_start = payload.week_start + timedelta(days=7 * idx)
        result = await session.execute(select(MenuWeek).where(MenuWeek.week_start == week_start))
        menu_week = result.scalars().unique().first()
        if not menu_week:
            weeks.append(
                CalcOrderWeekBreakdown(
                    week_start=week_start,
                    total_lari=0.0,
                    days=[],
                    has_menu=False,
                )
            )
            continue
        await session.refresh(menu_week, attribute_names=["day_offers"])
        calc = OrderCalculator(menu_week)
        items = [BasketItem(sel.day_of_week, sel.portions) for sel in payload.selections]
        week_result = calc.calc_week(items, week_start)
        breakdown = CalcOrderWeekBreakdown(
            week_start=week_result["week_start"],
            total_lari=week_result["total_lari"],
            days=week_result["days"],
            has_menu=week_result["has_menu"],
        )
        weeks.append(breakdown)
        total += breakdown.total_lari

    if payload.promo_code:
        promo_applied = True
        discount = min(5.0, total)
        total -= discount

    return CalcOrderResponse(
        total_lari=total,
        discount_lari=discount,
        mode=payload.mode,
        weeks=weeks,
        promo_code_applied=promo_applied,
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout_order(payload: CheckoutRequest, session: AsyncSession = Depends(get_session)) -> CheckoutResponse:
    if payload.mode != "single":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Multiweek and subscription checkout to be implemented",
        )

    result = await session.execute(select(MenuWeek).where(MenuWeek.week_start == payload.week_start))
    menu_week = result.scalars().unique().first()
    if not menu_week:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    await session.refresh(menu_week, attribute_names=["day_offers"])

    calc_response = await calculate_order(
        CalcOrderRequest(
            week_start=payload.week_start,
            selections=payload.selections,
            promo_code=payload.promo_code,
            weeks_ahead=1,
            mode=payload.mode,
        ),
        session,
    )
    if not calc_response.weeks or not calc_response.weeks[0].days:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty order")

    # Create a simple order entry for the first day (placeholder behaviour)
    first_day = next((day for day in calc_response.weeks[0].days if not day.sold_out and not day.closed), None)
    if first_day is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Selected days unavailable")

    day_offer = next((offer for offer in menu_week.day_offers if offer.day_of_week == first_day.day_of_week), None)
    order = Order(
        order_code="WEB-PLACEHOLDER",
        user_id=None,
        address_id=payload.address.address_id,
        menu_week_id=menu_week.id,
        delivery_date=first_day.date,
        day_of_week=first_day.day_of_week,
        count=first_day.portions,
        items=day_offer.items if day_offer else [],
        status=OrderStatus.NEW,
        price_lari=first_day.price_lari,
        total_lari=calc_response.total_lari,
        promo_code=payload.promo_code,
        delivery_slot_id=payload.address.delivery_slot_id,
        notes=None,
        is_next_week=menu_week.week_start > payload.week_start,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)

    return CheckoutResponse(order_id=order.id, payment_intent_client_secret=None, next_action="complete")
