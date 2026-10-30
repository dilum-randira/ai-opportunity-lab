"""Privacy-minimal, offline WhatsApp Business Platform cost scenarios.

This is a hypothesis calculator, not a Meta quotation. Rates are supplied by
callers, in LKR, for one destination market. Only aggregate counts are used.
The service-message allowance applies separately to each business phone number.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")
MAX_PHONE_NUMBERS = 20
MAX_MESSAGES = 1_000_000
MAX_RATE_LKR = Decimal("1000000")


def _count(value: Any, name: str, maximum: int = MAX_MESSAGES) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer between 0 and {maximum}")
    return value


def _rate(value: Any, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite nonnegative LKR rate")
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{name} must be a finite nonnegative LKR rate") from exc
    if not rate.is_finite() or not 0 <= rate <= MAX_RATE_LKR:
        raise ValueError(f"{name} must be a finite nonnegative LKR rate")
    return rate


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def estimate(*, service_messages_by_number: list[int],
             utility_messages: int = 0, marketing_messages: int = 0,
             authentication_messages: int = 0,
             service_rate_lkr: Any = "0", utility_rate_lkr: Any = "0",
             marketing_rate_lkr: Any = "0", authentication_rate_lkr: Any = "0",
             free_service_messages_per_number: int = 1000) -> dict:
    """Estimate delivered-message charges from explicit, hypothetical rates.

    Counts exclude free-entry-point messages, inbound messages, and reactions.
    The caller must classify each eligible delivered message exactly once.
    Does not model volume-tier discounts, taxes, exchange rates, or BSP fees.
    """
    if (type(service_messages_by_number) is not list or
            not 1 <= len(service_messages_by_number) <= MAX_PHONE_NUMBERS):
        raise ValueError(f"service_messages_by_number must have 1..{MAX_PHONE_NUMBERS} entries")
    service = [_count(value, f"service_messages_by_number[{index}]")
               for index, value in enumerate(service_messages_by_number)]
    allowance = _count(free_service_messages_per_number, "free_service_messages_per_number")
    utility = _count(utility_messages, "utility_messages")
    marketing = _count(marketing_messages, "marketing_messages")
    authentication = _count(authentication_messages, "authentication_messages")
    rates = {
        "service": _rate(service_rate_lkr, "service_rate_lkr"),
        "utility": _rate(utility_rate_lkr, "utility_rate_lkr"),
        "marketing": _rate(marketing_rate_lkr, "marketing_rate_lkr"),
        "authentication": _rate(authentication_rate_lkr, "authentication_rate_lkr"),
    }
    free_service = sum(min(count, allowance) for count in service)
    billable_service = sum(max(0, count - allowance) for count in service)
    counts = {
        "service_delivered": sum(service),
        "service_free": free_service,
        "service_billable": billable_service,
        "utility_billable": utility,
        "marketing_billable": marketing,
        "authentication_billable": authentication,
    }
    charges = {
        "service": Decimal(billable_service) * rates["service"],
        "utility": Decimal(utility) * rates["utility"],
        "marketing": Decimal(marketing) * rates["marketing"],
        "authentication": Decimal(authentication) * rates["authentication"],
    }
    return {
        "mode": "OFFLINE_HYPOTHETICAL_RATES_NOT_A_PROVIDER_QUOTE",
        "business_phone_number_count": len(service),
        "free_service_messages_per_number_assumed": allowance,
        "counts": counts,
        "cost_lkr": {**{name: _money(amount) for name, amount in charges.items()},
                     "total": _money(sum(charges.values(), Decimal(0)))},
        "cautions": [
            "From 2026-10-01, the modeled service allowance is per business phone number and resets monthly.",
            "Utility templates are billable even inside an open 24-hour customer service window.",
            "This calculator excludes free-entry-point deliveries, inbound messages, reactions, taxes, FX and BSP fees.",
            "Utility/authentication volume tiers and recipient-market differences are not modeled.",
            "Use current official Meta rate cards and actual delivery classifications before quoting customers.",
            "The free WhatsApp Business app is not the paid WhatsApp Business Platform.",
        ],
    }
