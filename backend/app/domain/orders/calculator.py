from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable

from fastapi import HTTPException, status

from ...db.models.menu import DayOffer, DayStatus, MenuWeek

DAY_TO_INDEX = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
}


class BasketItem:
    def __init__(self, day_of_week: str, portions: int) -> None:
        if day_of_week not in DAY_TO_INDEX:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown day {day_of_week}")
        self.day_of_week = day_of_week
        self.portions = portions


class OrderCalculator:
    def __init__(self, menu_week: MenuWeek, now: datetime | None = None) -> None:
        self.menu_week = menu_week
        self.now = now or datetime.utcnow()
        self.base_price = float(menu_week.base_price_lari)
        self.offers: dict[str, DayOffer] = {offer.day_of_week: offer for offer in menu_week.day_offers}

    def calc_day(self, basket_item: BasketItem, week_start: date) -> dict:
        offer = self.offers.get(basket_item.day_of_week)
        if not offer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No menu for {basket_item.day_of_week}")
        delivery_date = week_start + timedelta(days=DAY_TO_INDEX[basket_item.day_of_week])
        status_info = self._determine_status(offer, delivery_date)
        price = float(offer.price_lari) if offer.price_lari is not None else self.base_price
        subtotal = price * basket_item.portions
        return {
            "day_of_week": basket_item.day_of_week,
            "date": delivery_date,
            "portions": basket_item.portions,
            "price_lari": price,
            "subtotal_lari": subtotal,
            "sold_out": status_info["sold_out"],
            "closed": status_info["closed"],
            "reason": status_info["reason"],
        }

    def calc_week(self, selections: Iterable[BasketItem], week_start: date) -> dict:
        days = [self.calc_day(item, week_start) for item in selections]
        total = sum(day["subtotal_lari"] for day in days if not day["sold_out"] and not day["closed"])
        has_menu = bool(days)
        return {
            "week_start": week_start,
            "total_lari": total,
            "days": days,
            "has_menu": has_menu,
        }

    def _determine_status(self, offer: DayOffer, delivery_date: date) -> dict:
        sold_out = offer.status == DayStatus.SOLD_OUT or offer.sold_out
        closed = False
        reason: str | None = None
        if offer.status == DayStatus.CLOSED:
            closed = True
            reason = "День закрыт администратором"
        else:
            if delivery_date == self.now.date() and self.now.hour >= self.menu_week.order_deadline_hour:
                closed = True
                reason = "После дедлайна"
            if delivery_date < self.now.date():
                closed = True
                reason = "Дата в прошлом"
        return {"sold_out": sold_out, "closed": closed, "reason": reason}
