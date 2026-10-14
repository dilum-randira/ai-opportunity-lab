"""Offline merchant time-savings estimator: no network, customer data, or payments."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def _positive(value, name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid {name}") from error
    if not number.is_finite() or number < 0 or number > 100_000_000:
        raise ValueError(f"Invalid {name}")
    return number


def estimate_roi(*, orders_per_month, seconds_saved_per_order, hourly_lkr,
                 monthly_subscription_lkr, monthly_operating_lkr=0):
    """Model hypothetical net value; negative savings or invalid inputs are rejected."""
    if type(orders_per_month) is not int or not 1 <= orders_per_month <= 1_000_000:
        raise ValueError("orders_per_month must be an integer from 1 to 1000000")
    seconds = _positive(seconds_saved_per_order, "seconds_saved_per_order")
    if seconds > 36000:
        raise ValueError("Unrealistic order-processing time")
    hourly = _positive(hourly_lkr, "hourly_lkr")
    subscription = _positive(monthly_subscription_lkr, "monthly_subscription_lkr")
    operating = _positive(monthly_operating_lkr, "monthly_operating_lkr")
    gross = Decimal(orders_per_month) * seconds * hourly / Decimal(3600)
    total = subscription + operating
    net = gross - total
    quantize = lambda value: str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return {"mode": "HYPOTHETICAL_NO_CUSTOMER_DATA", "monthly_orders": orders_per_month,
            "gross_labor_value_lkr": quantize(gross),
            "total_monthly_cost_lkr": quantize(total),
            "net_monthly_value_lkr": quantize(net),
            "potentially_positive": net > 0}
