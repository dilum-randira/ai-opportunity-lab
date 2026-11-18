"""Deterministic review queue for unverified OrderPilot cost evidence.

No URL fetching or claim of price verification. Priority is for manual research,
not a numerical assessment of provider reliability.
"""
from orderpilot.cost_review import review_cost_evidence


def prioritize_cost_review(rows: list, *, as_of: str, max_age_days: int = 30) -> dict:
    """Return an actionable, stable review queue without leaking price or URL fields.

    Internal assumptions are highest priority, followed by stale external
    evidence and then recent external evidence. All entries need manual checks.
    """
    report = review_cost_evidence(rows, as_of=as_of, max_age_days=max_age_days)
    queue = []
    for item in report["items"]:
        if item["kind"] == "internal_assumption":
            priority = 0
            reason = "replace internal assumption with independently checked evidence"
        elif item["stale"]:
            priority = 1
            reason = "refresh outdated external evidence and independently check pricing"
        else:
            priority = 2
            reason = "independently check source, pricing unit, taxes, and applicability"
        queue.append({
            "name": item["name"],
            "kind": item["kind"],
            "age_days": item["age_days"],
            "priority": priority + 1,
            "reason": reason,
            "requires_manual_verification": True,
        })
    queue.sort(key=lambda item: (item["priority"], -item["age_days"], item["name"]))
    return {
        "as_of": report["as_of"],
        "total": report["total"],
        "stale_count": report["stale_count"],
        "missing_external_evidence": report["missing_external_evidence"],
        "verified_provider_prices": 0,
        "ready_for_commercial_pricing_claims": False,
        "queue": queue,
        "warning": "Review order is heuristic. No source or price has been independently verified.",
    }
