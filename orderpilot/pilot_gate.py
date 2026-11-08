"""Offline, conservative screening gate for aggregate OrderPilot pilot evidence.

A positive screen is NOT proof of causality, product-market fit, or permission to
contact customers, charge fees, or deploy. Do not commit actual merchant data.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from .paired_study import summarize

MAX_MERCHANTS = 1000


def _integer(value, label: str, *, maximum: int = MAX_MERCHANTS) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{label} must be an integer from 0 to {maximum}")
    return value


def _money(value, label: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite nonnegative number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{label} must be a finite nonnegative number") from exc
    if not result.is_finite() or result < 0 or result > Decimal("100000000"):
        raise ValueError(f"{label} must be a finite nonnegative number")
    return result


def screen(*, study_kind: str, pairs: list, consenting_merchants: int,
           merchants_reporting_repeated_pain: int,
           merchants_discussing_price: int, modeled_net_lkr) -> dict:
    """Screen aggregate evidence; never accept names, IDs, or message contents.

    `study_kind` must explicitly distinguish consented observations from
    synthetic exercises. A positive result remains an internal review cue only.
    """
    if study_kind not in ("synthetic", "consented_aggregate"):
        raise ValueError("study_kind must be synthetic or consented_aggregate")
    merchants = _integer(consenting_merchants, "consenting_merchants")
    pain = _integer(merchants_reporting_repeated_pain, "merchants_reporting_repeated_pain")
    price = _integer(merchants_discussing_price, "merchants_discussing_price")
    if pain > merchants or price > merchants:
        raise ValueError("merchant outcome counts cannot exceed consenting merchants")
    if not isinstance(pairs, list) or not 1 <= len(pairs) <= 5000:
        raise ValueError("pairs must contain 1..5000 observations")
    cleaned = []
    for row in pairs:
        if not isinstance(row, (tuple, list)) or len(row) != 4:
            raise ValueError("each pair must have four numeric fields")
        before, after, errors_before, errors_after = row
        for value in (before, after):
            if isinstance(value, bool):
                raise ValueError("durations must be finite nonnegative numbers")
            try:
                n = Decimal(str(value))
            except (InvalidOperation, ValueError, TypeError) as exc:
                raise ValueError("durations must be finite nonnegative numbers") from exc
            if not n.is_finite() or not 0 <= n <= 36000:
                raise ValueError("durations must be finite nonnegative numbers")
        a, b = Decimal(str(before)), Decimal(str(after))
        e1 = _integer(errors_before, "baseline_errors", maximum=100)
        e2 = _integer(errors_after, "assisted_errors", maximum=100)
        cleaned.append((a, b, e1, e2))
    net = _money(modeled_net_lkr, "modeled_net_lkr")
    stats = summarize(cleaned)
    mean = sum((a - b for a, b, _, _ in cleaned), Decimal(0)) / len(cleaned)
    interval = stats["bootstrap_95pct_interval_seconds"]
    lower_positive = interval is not None and Decimal(interval[0]) > 0
    checks = {
        "consented_observations": study_kind == "consented_aggregate",
        "screening_sample_target": len(cleaned) >= 20 and merchants >= 5,
        "repeated_buyer_pain": pain >= 1,
        "explicit_price_discussion": price >= 1,
        "no_increase_in_errors": stats["errors_after"] <= stats["errors_before"],
        "positive_unrounded_mean_time_saving": mean > 0,
        "positive_descriptive_interval_lower_bound": lower_positive,
        "positive_modeled_net_value": net > 0,
    }
    return {
        "status": "REVIEW_CANDIDATE_NOT_PILOT_APPROVAL" if all(checks.values()) else "EVIDENCE_INSUFFICIENT",
        "checks": checks,
        "sample_size": len(cleaned),
        "consenting_merchants": merchants,
        "cautions": [
            "Self-reported consent is not verified by this offline function.",
            "Bootstrap bounds are descriptive, not causal or population guarantees.",
            "Modeled profitability is not willingness-to-pay evidence.",
            "No outreach, deployment, payments, or publication of private observations is authorized.",
        ],
    }
