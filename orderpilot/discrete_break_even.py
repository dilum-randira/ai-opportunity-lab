"""Exact discrete merchant break-even search for hypothetical order economics.

Searches integer monthly volumes using the same rounded message counts and
allowances as project(); does not assume that net value is monotonic.
"""
from __future__ import annotations
from .unit_economics import project, MAX_VOLUME


def first_profitable_volume(*, max_orders: int = 10000, **scenario) -> dict:
    if type(max_orders) is not int or not 1 <= max_orders <= MAX_VOLUME:
        raise ValueError("max_orders must be an integer between 1 and 1000000")
    if "monthly_orders" in scenario:
        raise ValueError("pass max_orders instead of monthly_orders")
    # Reject bad inputs even when the first candidate is profitable.
    result = None
    for n in range(1, max_orders + 1):
        candidate = project(monthly_orders=n, **scenario)
        # project() evaluates exact Decimal net before rounding presentation
        # strings to cents. A positive sub-cent margin must not look like zero.
        if candidate["commercially_positive_under_assumptions"]:
            result = n
            break
    return {
        "mode": "HYPOTHETICAL_DISCRETE_FIRST_POSITIVE",
        "first_positive_monthly_orders": result,
        "searched_through": result if result is not None else max_orders,
        "note": "First strictly positive unrounded net value, not a sustained threshold. Costs are assumptions; displayed currency is rounded to cents.",
    }
