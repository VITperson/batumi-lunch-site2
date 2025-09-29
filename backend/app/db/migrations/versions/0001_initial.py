"""Initial schema"""

from __future__ import annotations

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = sa.Enum("customer", "admin", name="userrole")
order_status_enum = sa.Enum(
    "new",
    "confirmed",
    "preparing",
    "delivered",
    "cancelled",
    "cancelled_by_user",
    "failed",
    name="orderstatus",
)
day_status_enum = sa.Enum("available", "sold_out", "closed", name="daystatus")
payment_status_enum = sa.Enum("pending", "requires_action", "succeeded", "failed", "cancelled", name="paymentstatus")
subscription_status_enum = sa.Enum("active", "paused", "cancelled", "past_due", name="subscriptionstatus")


def upgrade() -> None:
    user_role_enum.create(op.get_bind(), checkfirst=True)
    order_status_enum.create(op.get_bind(), checkfirst=True)
    day_status_enum.create(op.get_bind(), checkfirst=True)
    payment_status_enum.create(op.get_bind(), checkfirst=True)
    subscription_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "allergy_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("slug", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.String(length=512)),
    )

    op.create_table(
        "delivery_zones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512)),
        sa.Column("minimum_order_total", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("slug", name="uq_delivery_zones_slug"),
    )

    op.create_table(
        "delivery_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("delivery_zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("window_start", sa.String(length=16), nullable=False),
        sa.Column("window_end", sa.String(length=16), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weekdays", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("zone_id", "label", name="uq_delivery_slots_zone_label"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("external_id", sa.String(length=64), unique=True),
        sa.Column("telegram_id", sa.BigInteger(), unique=True),
        sa.Column("email", sa.String(length=255), unique=True),
        sa.Column("phone", sa.String(length=32)),
        sa.Column("first_name", sa.String(length=128)),
        sa.Column("last_name", sa.String(length=128)),
        sa.Column("role", user_role_enum, nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_guest", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_users_phone", "users", ["phone"])

    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False, server_default="Дом"),
        sa.Column("address_line", sa.String(length=512), nullable=False),
        sa.Column("entrance", sa.String(length=128)),
        sa.Column("floor", sa.String(length=64)),
        sa.Column("apartment", sa.String(length=64)),
        sa.Column("instructions", sa.String(length=512)),
        sa.Column("delivery_zone_id", sa.Integer(), sa.ForeignKey("delivery_zones.id")),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("user_id", "label", name="uq_addresses_user_label"),
    )

    op.create_table(
        "menu_weeks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=128)),
        sa.Column("description", sa.String(length=512)),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_deadline_hour", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("base_price_lari", sa.Numeric(10, 2), nullable=False, server_default="15.0"),
        sa.UniqueConstraint("week_start", name="uq_menu_weeks_week_start"),
    )

    op.create_table(
        "day_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("menu_week_id", sa.Integer(), sa.ForeignKey("menu_weeks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.String(length=16), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("calories", sa.Integer()),
        sa.Column("allergy_tag_ids", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("price_lari", sa.Numeric(10, 2)),
        sa.Column("status", day_status_enum, nullable=False, server_default="available"),
        sa.Column("portion_limit", sa.Integer()),
        sa.Column("sold_out", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("photo_url", sa.String(length=512)),
        sa.UniqueConstraint("menu_week_id", "day_of_week", name="uq_day_offers_week_day"),
    )

    op.create_table(
        "presets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("menu_week_id", sa.Integer(), sa.ForeignKey("menu_weeks.id", ondelete="SET NULL")),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512)),
        sa.Column("default_portions", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("day_selection", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("discount_percent", sa.Integer()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("menu_week_id", "slug", name="uq_presets_week_slug"),
    )

    op.create_table(
        "order_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("repeat_weeks", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("repeat_days", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("default_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "payment_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("last4", sa.String(length=4)),
        sa.Column("brand", sa.String(length=32)),
        sa.Column("exp_month", sa.Integer()),
        sa.Column("exp_year", sa.Integer()),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("order_templates.id", ondelete="SET NULL")),
        sa.Column("payment_token_id", sa.Integer(), sa.ForeignKey("payment_tokens.id", ondelete="SET NULL")),
        sa.Column("status", subscription_status_enum, nullable=False, server_default="active"),
        sa.Column("current_week_start", sa.Date()),
        sa.Column("next_charge_at", sa.DateTime(timezone=True)),
        sa.Column("pause_until", sa.Date()),
        sa.Column("settings", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("order_code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("address_id", sa.Integer(), sa.ForeignKey("addresses.id", ondelete="SET NULL")),
        sa.Column("menu_week_id", sa.Integer(), sa.ForeignKey("menu_weeks.id", ondelete="SET NULL")),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("order_templates.id", ondelete="SET NULL")),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("day_of_week", sa.String(length=16), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("items", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("status", order_status_enum, nullable=False, server_default="new"),
        sa.Column("price_lari", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_lari", sa.Numeric(10, 2), nullable=False),
        sa.Column("promo_code", sa.String(length=64)),
        sa.Column("delivery_slot_id", sa.Integer(), sa.ForeignKey("delivery_slots.id", ondelete="SET NULL")),
        sa.Column("notes", sa.String(length=512)),
        sa.Column("is_next_week", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("checkout_started_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "week_selections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("subtotal_lari", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )

    op.create_table(
        "payment_intents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="SET NULL")),
        sa.Column("subscription_id", sa.Integer(), sa.ForeignKey("subscriptions.id", ondelete="SET NULL")),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_intent_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("status", payment_status_enum, nullable=False, server_default="pending"),
        sa.Column("amount_lari", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="GEL"),
        sa.Column("client_secret", sa.String(length=255)),
        sa.Column("return_url", sa.String(length=255)),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "subscription_weeks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("subscription_id", sa.Integer(), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="scheduled"),
        sa.Column("subtotal_lari", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="SET NULL")),
    )


def downgrade() -> None:
    op.drop_table("subscription_weeks")
    op.drop_table("payment_intents")
    op.drop_table("week_selections")
    op.drop_table("orders")
    op.drop_table("subscriptions")
    op.drop_table("payment_tokens")
    op.drop_table("order_templates")
    op.drop_table("presets")
    op.drop_table("day_offers")
    op.drop_table("menu_weeks")
    op.drop_table("addresses")
    op.drop_table("users")
    op.drop_table("delivery_slots")
    op.drop_table("delivery_zones")
    op.drop_table("allergy_tags")

    subscription_status_enum.drop(op.get_bind(), checkfirst=True)
    payment_status_enum.drop(op.get_bind(), checkfirst=True)
    day_status_enum.drop(op.get_bind(), checkfirst=True)
    order_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
