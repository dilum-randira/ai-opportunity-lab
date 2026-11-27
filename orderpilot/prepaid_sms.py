"""Offline fixed-tier prepaid SMS cash estimator; no provider calls."""
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass


@dataclass(frozen=True)
class PrepaidEstimate:
    consumed: Decimal
    topups: int
    cash_paid: Decimal
    closing_credit: Decimal


def _cents(value):
    if not isinstance(value, (str, int, Decimal)) or isinstance(value, bool):
        raise ValueError("Use decimal strings, integers or Decimal amounts")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc
    if not amount.is_finite() or amount < 0 or amount > 10**9:
        raise ValueError("Amount must be finite, nonnegative and at most 1 billion")
    # Reject sub-cent values before constructing potentially huge denominators.
    if amount.is_zero():
        return 0
    _, digits, exponent = amount.as_tuple()
    if exponent < -2:
        excess = -2 - exponent
        if excess >= len(digits) or any(digits[-excess:]):
            raise ValueError("Amounts must be exact to cents")
        amount = Decimal((0, digits[:-excess], -2))
    numerator, denominator = amount.as_integer_ratio()
    cents, remainder = divmod(numerator * 100, denominator)
    if remainder:
        raise ValueError("Amounts must be exact to cents")
    return cents


def _money(cents):
    return Decimal(f"{cents // 100}.{cents % 100:02d}")


def estimate_prepaid(units, rate, topup, opening_credit="0"):
    """Model identical top-ups, no expiry or fees; not a provider quote."""
    if type(units) is not int or not 0 <= units <= 10**9:
        raise ValueError("Units must be a nonnegative integer up to 1 billion")
    rate, topup, opening = map(_cents, (rate, topup, opening_credit))
    if not topup:
        raise ValueError("Top-up must be positive")
    consumed = units * rate
    deficit = max(0, consumed - opening)
    count = (deficit + topup - 1) // topup
    cash = count * topup
    return PrepaidEstimate(_money(consumed), count, _money(cash),
                           _money(opening + cash - consumed))
