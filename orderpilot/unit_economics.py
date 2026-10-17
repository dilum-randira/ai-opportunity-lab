"""Pure offline merchant cost analysis. All prices are caller-supplied LKR hypotheses.

No provider prices are fetched; no customer data, network, messages, or payments.
Service free allowance applies only to modeled Business Platform service messages.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")
MAX_VOLUME = 1_000_000
MAX_PRICE = Decimal("100000000")


def _decimal(value: Any, name: str, maximum: Decimal = MAX_PRICE) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a nonnegative finite number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{name} must be a nonnegative finite number") from exc
    if not result.is_finite() or not 0 <= result <= maximum:
        raise ValueError(f"{name} must be between 0 and {maximum}")
    return result


def _count(value: Any, name: str, minimum: int = 0, maximum: int = MAX_VOLUME) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in {minimum}..{maximum}")
    return value


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def _ceil(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def project(*, monthly_orders: int, seconds_saved_per_order: Any,
            hourly_lkr: Any, subscription_lkr: Any, setup_lkr: Any = "0",
            setup_amortization_months: int = 12, hosting_support_lkr: Any = "0",
            service_messages_per_order: Any = "0", service_rate_lkr: Any = "0",
            free_service_messages: int = 0,
            utility_messages_per_order: Any = "0", utility_rate_lkr: Any = "0") -> dict[str, Any]:
    """Hypothetical unit economics, not causal proof or a provider quotation.

    Time saved is validated nonnegative; use 0 if assistance slows tasks and
    report that loss separately. Message quantities round *up* per month.
    """
    volume = _count(monthly_orders, "monthly_orders", 1)
    months = _count(setup_amortization_months, "setup_amortization_months", 1, 120)
    allowance = _count(free_service_messages, "free_service_messages", 0, 10_000_000)
    seconds = _decimal(seconds_saved_per_order, "seconds_saved_per_order", Decimal(36_000))
    hourly = _decimal(hourly_lkr, "hourly_lkr")
    subscription = _decimal(subscription_lkr, "subscription_lkr")
    setup = _decimal(setup_lkr, "setup_lkr")
    hosting = _decimal(hosting_support_lkr, "hosting_support_lkr")
    svc_count_per_order = _decimal(service_messages_per_order, "service_messages_per_order", Decimal(100))
    util_count_per_order = _decimal(utility_messages_per_order, "utility_messages_per_order", Decimal(100))
    svc_rate = _decimal(service_rate_lkr, "service_rate_lkr")
    util_rate = _decimal(utility_rate_lkr, "utility_rate_lkr")

    volume_decimal = Decimal(volume)
    service_messages = _ceil(volume_decimal * svc_count_per_order)
    utility_messages = _ceil(volume_decimal * util_count_per_order)
    chargeable_service = max(0, service_messages - allowance)
    messaging = Decimal(chargeable_service) * svc_rate + Decimal(utility_messages) * util_rate
    fixed = subscription + setup / months + hosting
    total = fixed + messaging
    labor_value = volume_decimal * seconds / Decimal(3600) * hourly
    net = labor_value - total
    per_order_labor = seconds / Decimal(3600) * hourly
    marginal_messaging = svc_count_per_order * svc_rate + util_count_per_order * util_rate
    contribution = per_order_labor - marginal_messaging
    # Safe conservative *planning approximation*, excludes free tier and ceiling
    # effects. Never present as exact break-even with nonlinear billing.
    conservative_break_even = _ceil(fixed / contribution) if contribution > 0 else None
    if conservative_break_even is not None and conservative_break_even > MAX_VOLUME:
        conservative_break_even = None

    return {
        "mode": "HYPOTHETICAL_OFFLINE_PRICES_NOT_VERIFIED",
        "monthly_orders": volume,
        "messages": {"service_total": service_messages,
                     "service_billable": chargeable_service,
                     "utility_total": utility_messages,
                     "free_service_allowance_assumed": allowance},
        "monthly_lkr": {"gross_labor_value": _money(labor_value),
                        "subscription": _money(subscription),
                        "amortized_setup": _money(setup / months),
                        "hosting_support": _money(hosting),
                        "messaging": _money(messaging),
                        "total_cost": _money(total),
                        "net_value": _money(net),
                        "net_roi_percent": _money(net / total * 100) if total else None},
        "conservative_break_even_orders_excluding_allowance": conservative_break_even,
        "commercially_positive_under_assumptions": net > 0,
        "cautions": [
            "These are user-entered hypotheses, not verified Sri Lankan provider prices or merchant outcomes.",
            "Free-service allowance only applies to the paid WhatsApp Business Platform when relevant; it never describes the free WhatsApp Business app.",
            "Time saved may not reduce payroll. Does not include tax, churn, support beyond entered costs, or acquisition.",
            "Break-even is a conservative continuous-rate approximation, not exact after free allowances and whole-message rounding.",
            "No customer records or communication are involved in this calculator.",
        ],
    }
