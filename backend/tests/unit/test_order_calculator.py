from datetime import date, datetime

import pytest

from app.db.models.menu import DayOffer, DayStatus, MenuWeek
from app.domain.orders.calculator import BasketItem, OrderCalculator


@pytest.fixture
def menu_week() -> MenuWeek:
    week = MenuWeek(
        id=1,
        week_start=date(2024, 3, 18),
        title="Тестовая неделя",
        description=None,
        is_published=True,
        order_deadline_hour=10,
        base_price_lari=15,
    )
    week.day_offers = [
        DayOffer(day_of_week="Понедельник", items=["Суп"], status=DayStatus.AVAILABLE, price_lari=15, sold_out=False, menu_week=week),
        DayOffer(day_of_week="Вторник", items=["Салат"], status=DayStatus.SOLD_OUT, price_lari=15, sold_out=True, menu_week=week),
    ]
    return week


def test_calc_day_respects_cutoff(menu_week: MenuWeek) -> None:
    calc = OrderCalculator(menu_week, now=datetime(2024, 3, 18, 11, 0))
    basket = BasketItem("Понедельник", 2)
    result = calc.calc_day(basket, menu_week.week_start)
    assert result["closed"] is True
    assert result["reason"] == "После дедлайна"


def test_calc_day_sold_out(menu_week: MenuWeek) -> None:
    calc = OrderCalculator(menu_week, now=datetime(2024, 3, 17, 9, 0))
    basket = BasketItem("Вторник", 1)
    result = calc.calc_day(basket, menu_week.week_start)
    assert result["sold_out"] is True


def test_calc_week_sums(menu_week: MenuWeek) -> None:
    calc = OrderCalculator(menu_week, now=datetime(2024, 3, 17, 9, 0))
    selections = [BasketItem("Понедельник", 2)]
    result = calc.calc_week(selections, menu_week.week_start)
    assert result["total_lari"] == pytest.approx(30)
