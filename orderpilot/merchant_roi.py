"""Compose OrderPilot labor ROI and per-number WhatsApp message-cost scenarios.

Offline, standard-library-only; all prices and volumes are hypothetical inputs.
No customer records, network access, message sending, or payments.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .messaging_costs import estimate as estimate_messages, _rate
from .unit_economics import _count, _decimal, _money, project


def _display_money(value: Decimal) -> str:
    """Suppress negative zero in rounded display; flags use exact Decimal."""
    shown = _money(value)
    return "0.00" if shown == "-0.00" else shown


def evaluate(*, monthly_orders: int, seconds_saved_per_order: Any,
             hourly_lkr: Any, subscription_lkr: Any,
             service_messages_by_number: list[int],
             utility_messages: int = 0, marketing_messages: int = 0,
             authentication_messages: int = 0,
             service_rate_lkr: Any = "0", utility_rate_lkr: Any = "0",
             marketing_rate_lkr: Any = "0", authentication_rate_lkr: Any = "0",
             free_service_messages_per_number: int = 1000,
             hosting_support_lkr: Any = "0", setup_lkr: Any = "0",
             setup_amortization_months: int = 12) -> dict[str, Any]:
    """Show the effect of separately counted message fees on assumed labor ROI.

    The before/after values hold labor savings constant and isolate messaging
    cost; they do NOT compare the productivity of different merchant workflows.
    Message counts are explicit delivered counts, not inferred from orders.
    """
    # Reuse the existing project validation, without pretending its older
    # per-order messaging allowance models multiple business phone numbers.
    base = project(monthly_orders=monthly_orders,
                   seconds_saved_per_order=seconds_saved_per_order,
                   hourly_lkr=hourly_lkr, subscription_lkr=subscription_lkr,
                   hosting_support_lkr=hosting_support_lkr,
                   setup_lkr=setup_lkr,
                   setup_amortization_months=setup_amortization_months)
    messages = estimate_messages(
        service_messages_by_number=service_messages_by_number,
        utility_messages=utility_messages,
        marketing_messages=marketing_messages,
        authentication_messages=authentication_messages,
        service_rate_lkr=service_rate_lkr,
        utility_rate_lkr=utility_rate_lkr,
        marketing_rate_lkr=marketing_rate_lkr,
        authentication_rate_lkr=authentication_rate_lkr,
        free_service_messages_per_number=free_service_messages_per_number,
    )
    counts = messages["counts"]
    # Compute exact Decimal costs from validated counts/rates. Do not subtract
    # rounded presentation strings or accumulate a cent of double rounding.
    message_cost = sum((
        Decimal(counts[f"{category}_billable"]) * _rate(rate, f"{category}_rate_lkr")
        for category, rate in (
            ("service", service_rate_lkr), ("utility", utility_rate_lkr),
            ("marketing", marketing_rate_lkr),
            ("authentication", authentication_rate_lkr),
        )
    ), Decimal(0))
    orders = _count(monthly_orders, "monthly_orders", 1)
    months = _count(setup_amortization_months, "setup_amortization_months", 1, 120)
    seconds = _decimal(seconds_saved_per_order, "seconds_saved_per_order", Decimal(36_000))
    hourly = _decimal(hourly_lkr, "hourly_lkr")
    subscription = _decimal(subscription_lkr, "subscription_lkr")
    hosting = _decimal(hosting_support_lkr, "hosting_support_lkr")
    setup = _decimal(setup_lkr, "setup_lkr")
    gross = Decimal(orders) * seconds * hourly / Decimal(3600)
    fixed = subscription + hosting + setup / months
    before = gross - fixed
    after = before - message_cost
    return {
        "mode": "OFFLINE_HYPOTHETICAL_ROI_NOT_BUYER_VALIDATION",
        "monthly_orders": orders,
        "labor_value_lkr": _money(gross),
        "fixed_monthly_cost_lkr": _money(fixed),
        "net_before_platform_messaging_lkr": _display_money(before),
        "platform_messaging_cost_lkr": _money(message_cost),
        "net_after_platform_messaging_lkr": _display_money(after),
        "positive_after_messaging_under_assumptions": after > 0,
        "message_scenario": messages,
        "base_economics_mode": base["mode"],
        "cautions": [
            "All rates, order volumes and labor savings are unverified hypotheses, not Meta quotes or merchant outcomes.",
            "Before/after isolates message fees under identical assumed labor savings; it is not a workflow comparison.",
            "Per-number service allowances are not pooled; the older per-order ROI threshold is not used here.",
            "Taxes, BSP fees, acquisition, churn, tiered rates, and free-entry-point exemptions are not modeled.",
            "Rounded 0.00 may conceal a tiny positive or negative amount; the positivity flag uses exact values.",
            "Positive modeled ROI does not establish willingness to pay or authorize messaging, sales, or deployment.",
        ],
    }
