"""Offline merchant-level aggregation of repeated paired timing observations.

Input is already grouped by distinct consenting merchants outside this module.
No identifiers are accepted; grouping and consent cannot be verified here.
"""
from decimal import Decimal, InvalidOperation

MAX_GROUPS = 1000
MAX_ROWS_PER_GROUP = 100


def _duration(value):
    if isinstance(value, bool):
        raise ValueError("duration must be a finite number between 0 and 36000")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("duration must be a finite number between 0 and 36000") from exc
    if not number.is_finite() or not 0 <= number <= 36000:
        raise ValueError("duration must be a finite number between 0 and 36000")
    return number


def aggregate_merchants(groups: list) -> list:
    """Return one (mean_before, mean_after, any_error_before, any_error_after)
    tuple per merchant. Never pass individual order rows directly to pilot_gate.
    The any-error flags are conservative merchant-level outcomes, not error rates.
    """
    if not isinstance(groups, list) or not 1 <= len(groups) <= MAX_GROUPS:
        raise ValueError("groups must contain 1..1000 merchants")
    output = []
    for group in groups:
        if not isinstance(group, list) or not 1 <= len(group) <= MAX_ROWS_PER_GROUP:
            raise ValueError("each merchant requires 1..100 paired observations")
        before_sum = Decimal(0)
        after_sum = Decimal(0)
        before_error = 0
        after_error = 0
        for row in group:
            if not isinstance(row, (list, tuple)) or len(row) != 4:
                raise ValueError("each observation requires four numeric fields")
            before, after, e1, e2 = row
            a, b = _duration(before), _duration(after)
            if type(e1) is not int or type(e2) is not int or e1 not in (0, 1) or e2 not in (0, 1):
                raise ValueError("error flags must be integers 0 or 1")
            before_sum += a
            after_sum += b
            before_error |= e1
            after_error |= e2
        n = len(group)
        output.append((before_sum / n, after_sum / n, before_error, after_error))
    return output
