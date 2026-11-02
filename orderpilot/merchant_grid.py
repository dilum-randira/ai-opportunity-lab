"""Compare explicit, privacy-minimal merchant workloads across subscription prices.

All counts and prices are caller-supplied hypothetical scenarios. This module
never derives messages from orders or contacts providers, merchants, or buyers.
"""
from __future__ import annotations

from typing import Any

from .merchant_roi import evaluate
from .unit_economics import _count, _decimal, _money

MAX_WORKLOADS = 20
MAX_PRICES = 10
MAX_CELLS = 100
_REQUIRED = frozenset({"monthly_orders", "service_messages_by_number"})
_OPTIONAL = frozenset({"utility_messages", "marketing_messages", "authentication_messages"})


def compare(*, workloads: list[dict[str, Any]], subscription_prices_lkr: list[Any],
            seconds_saved_per_order: Any, hourly_lkr: Any,
            service_rate_lkr: Any = "0", utility_rate_lkr: Any = "0",
            marketing_rate_lkr: Any = "0", authentication_rate_lkr: Any = "0",
            free_service_messages_per_number: int = 1000,
            hosting_support_lkr: Any = "0", setup_lkr: Any = "0",
            setup_amortization_months: int = 12) -> dict[str, Any]:
    """Return an offline grid; every workload declares actual *assumed* counts.

    There is intentionally no per-order message multiplier: message routing,
    rounding, and per-number allowances must be specified explicitly rather
    than silently guessed. The schema rejects unknown fields and identifiers.
    """
    if type(workloads) is not list or not 1 <= len(workloads) <= MAX_WORKLOADS:
        raise ValueError("workloads must contain 1..20 explicit scenarios")
    if type(subscription_prices_lkr) is not list or not 1 <= len(subscription_prices_lkr) <= MAX_PRICES:
        raise ValueError("subscription_prices_lkr must contain 1..10 prices")
    if len(workloads) * len(subscription_prices_lkr) > MAX_CELLS:
        raise ValueError("comparison exceeds 100 scenario cells")
    prices = [_decimal(price, "subscription_price_lkr") for price in subscription_prices_lkr]
    if len(set(prices)) != len(prices):
        raise ValueError("subscription prices must be distinct")

    seen_volumes: set[int] = set()
    validated = []
    for index, workload in enumerate(workloads):
        if type(workload) is not dict:
            raise ValueError(f"workload {index}: expected an object")
        keys = set(workload)
        if not _REQUIRED <= keys or keys - (_REQUIRED | _OPTIONAL):
            raise ValueError(f"workload {index}: missing or unsupported fields")
        orders = _count(workload["monthly_orders"], "monthly_orders", 1)
        if orders in seen_volumes:
            raise ValueError("monthly order volumes must be distinct")
        seen_volumes.add(orders)
        validated.append(dict(workload))

    rows = []
    for workload in validated:
        price_rows = []
        message_counts = None
        message_cost = None
        for price in prices:
            result = evaluate(
                **workload, subscription_lkr=price,
                seconds_saved_per_order=seconds_saved_per_order,
                hourly_lkr=hourly_lkr,
                service_rate_lkr=service_rate_lkr,
                utility_rate_lkr=utility_rate_lkr,
                marketing_rate_lkr=marketing_rate_lkr,
                authentication_rate_lkr=authentication_rate_lkr,
                free_service_messages_per_number=free_service_messages_per_number,
                hosting_support_lkr=hosting_support_lkr,
                setup_lkr=setup_lkr,
                setup_amortization_months=setup_amortization_months,
            )
            message_counts = result["message_scenario"]["counts"]
            message_cost = result["platform_messaging_cost_lkr"]
            price_rows.append({
                "subscription_lkr": _money(price),
                "net_before_messaging_lkr": result["net_before_platform_messaging_lkr"],
                "net_after_messaging_lkr": result["net_after_platform_messaging_lkr"],
                "positive_after_messaging_under_assumptions": result[
                    "positive_after_messaging_under_assumptions"],
            })
        rows.append({
            "monthly_orders": workload["monthly_orders"],
            "business_phone_number_count": len(workload["service_messages_by_number"]),
            "message_counts": message_counts,
            "platform_messaging_cost_lkr": message_cost,
            "prices": price_rows,
        })

    return {
        "mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
        "scenario_count": len(workloads) * len(prices),
        "rows": rows,
        "cautions": [
            "All labor, price and delivered-message inputs are hypothetical, not observed customer outcomes or provider quotes.",
            "Message counts are explicit per workload; no messages-per-order or per-number routing is inferred.",
            "The same assumed labor savings are applied across workloads; this is not a controlled experiment.",
            "Per-number service allowances are not pooled; price flags use exact unrounded Decimal values.",
            "Excludes taxes, FX, BSP fees, volume tiers, free-entry-point exemptions, churn and acquisition costs.",
            "Positive modeled ROI is not evidence of willingness to pay or permission to contact or deploy.",
        ],
    }
