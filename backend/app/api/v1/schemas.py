from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class DayOfferOut(BaseModel):
    id: int
    day_of_week: str
    items: list[str]
    calories: int | None = None
    allergy_tag_ids: list[int] = Field(default_factory=list)
    price_lari: float | None = None
    status: Literal['available', 'sold_out', 'closed']
    portion_limit: int | None = None
    sold_out: bool
    photo_url: str | None = None


class MenuWeekOut(BaseModel):
    id: int
    week_start: date
    title: str | None = None
    description: str | None = None
    is_published: bool
    order_deadline_hour: int
    base_price_lari: float
    day_offers: list[DayOfferOut]


class PresetOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    default_portions: int
    day_selection: list[str]
    discount_percent: int | None = None


class MenuWeeksResponse(BaseModel):
    weeks: list[MenuWeekOut]


class BasketSelection(BaseModel):
    day_of_week: str
    portions: int = Field(ge=1, le=8)


class CalcOrderRequest(BaseModel):
    week_start: date
    selections: list[BasketSelection]
    promo_code: str | None = None
    weeks_ahead: int = Field(default=1, ge=1, le=8)
    mode: Literal['single', 'multiweek', 'subscription'] = 'single'


class CalcOrderDayBreakdown(BaseModel):
    day_of_week: str
    date: date
    portions: int
    price_lari: float
    subtotal_lari: float
    sold_out: bool = False
    closed: bool = False
    reason: str | None = None


class CalcOrderWeekBreakdown(BaseModel):
    week_start: date
    total_lari: float
    days: list[CalcOrderDayBreakdown]
    has_menu: bool


class CalcOrderResponse(BaseModel):
    total_lari: float
    discount_lari: float
    mode: Literal['single', 'multiweek', 'subscription']
    weeks: list[CalcOrderWeekBreakdown]
    promo_code_applied: bool


class CheckoutAddress(BaseModel):
    address_id: int | None = None
    address_line: str | None = None
    delivery_zone_slug: str | None = None
    delivery_slot_id: int | None = None
    phone: str | None = None
    contact_name: str | None = None


class CheckoutRequest(BaseModel):
    week_start: date
    selections: list[BasketSelection]
    promo_code: str | None = None
    weeks_ahead: int = Field(default=1, ge=1, le=8)
    mode: Literal['single', 'multiweek', 'subscription'] = 'single'
    address: CheckoutAddress
    guest_token: str | None = None
    payment_token_id: int | None = None


class CheckoutResponse(BaseModel):
    order_id: int | None = None
    subscription_id: int | None = None
    payment_intent_client_secret: str | None = None
    next_action: Literal['pay_now', 'confirm_sms', 'complete'] = 'complete'


class GuestAuthStartRequest(BaseModel):
    phone: str


class GuestAuthStartResponse(BaseModel):
    request_id: str
    expires_at: datetime


class GuestAuthConfirmRequest(BaseModel):
    request_id: str
    code: str


class GuestAuthConfirmResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class SubscriptionOut(BaseModel):
    id: int
    status: str
    next_charge_at: datetime | None
    pause_until: date | None
    settings: dict


class AddressOut(BaseModel):
    id: int
    label: str
    address_line: str
    is_default: bool
    delivery_zone_slug: str | None
    delivery_slot_id: int | None


class AddressCreateRequest(BaseModel):
    label: str
    address_line: str
    delivery_zone_slug: str | None = None
    delivery_slot_id: int | None = None
    entrance: str | None = None
    floor: str | None = None
    apartment: str | None = None
    instructions: str | None = None


class DeliverySlotOut(BaseModel):
    id: int
    label: str
    window_start: str
    window_end: str
    capacity: int
    weekdays: list[str]


class DeliveryZoneOut(BaseModel):
    id: int
    slug: str
    name: str
    minimum_order_total: float
    slots: list[DeliverySlotOut]
