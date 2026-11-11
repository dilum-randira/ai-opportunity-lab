"""Deterministic leave-one-merchant-out sensitivity for aggregated paired timings.

Each input row represents one distinct consenting merchant, not one order.
This is descriptive sensitivity, not a confidence interval or causal estimate.
"""
from decimal import Decimal, InvalidOperation

MAX_MERCHANTS = 1000


def _seconds(value):
    if isinstance(value, bool):
        raise ValueError("duration must be finite and between 0 and 36000")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("duration must be finite and between 0 and 36000") from exc
    if not number.is_finite() or not Decimal(0) <= number <= Decimal(36000):
        raise ValueError("duration must be finite and between 0 and 36000")
    return number


def leave_one_merchant_out(pairs: list) -> dict:
    """Return exact overall and leave-one-out mean savings in seconds.

    Requires 2..1000 independently grouped merchant observations. Each row
    is (mean_before, mean_after, error_before, error_after), where error flags
    are strictly integer 0/1. No merchant identifiers or raw rows are returned.
    """
    if not isinstance(pairs, list) or not 2 <= len(pairs) <= MAX_MERCHANTS:
        raise ValueError("pairs must contain 2..1000 distinct merchants")
    savings = []
    for row in pairs:
        if not isinstance(row, (tuple, list)) or len(row) != 4:
            raise ValueError("each merchant requires four fields")
        before, after, e1, e2 = row
        a, b = _seconds(before), _seconds(after)
        if type(e1) is not int or type(e2) is not int or e1 not in (0, 1) or e2 not in (0, 1):
            raise ValueError("error flags must be integers 0 or 1")
        savings.append(a - b)
    total = sum(savings, Decimal(0))
    n = len(savings)
    leave_one_out = [(total - saving) / (n - 1) for saving in savings]
    return {
        "merchant_count": n,
        "overall_mean_saving_seconds": str(total / n),
        "leave_one_out_min_mean_saving_seconds": str(min(leave_one_out)),
        "leave_one_out_max_mean_saving_seconds": str(max(leave_one_out)),
        "all_leave_one_out_means_positive": all(value > 0 for value in leave_one_out),
        "interpretation": "descriptive sensitivity only; not a confidence interval or causal estimate",
    }
