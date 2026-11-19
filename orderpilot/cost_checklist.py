"""Generate safe, offline checklists for human cost-evidence verification.

A checklist is not a verification result. No external URLs are fetched.
"""
from orderpilot.cost_triage import prioritize_cost_review


COMMON_CHECKS = (
    "Confirm the source is authentic and accessible on the review date",
    "Confirm the currency, billing unit, and minimum charges",
    "Check taxes, setup fees, and recurring or volume-based fees",
    "Confirm Sri Lankan merchant eligibility and contractual restrictions",
    "Record reviewer, review date, and supporting evidence outside this report",
)

KIND_CHECKS = {
    "internal_assumption": (
        "Find an independent provider quotation or published price list",
        "Keep the assumption explicitly separate from observed prices",
    ),
    "provider_quote": (
        "Confirm quotation validity period and relevant usage tier",
        "Confirm whether negotiated or customer-specific terms apply",
    ),
    "public_price_list": (
        "Confirm the published rate applies to the required product and region",
        "Check whether published prices exclude messaging or platform surcharges",
    ),
}


def build_cost_review_checklist(rows: list, *, as_of: str,
                                max_age_days: int = 30) -> dict:
    """Prioritize validated entries and attach concrete manual review tasks.

    The output intentionally excludes amounts and URLs; all tasks are pending.
    """
    triage = prioritize_cost_review(rows, as_of=as_of,
                                    max_age_days=max_age_days)
    items = []
    for entry in triage["queue"]:
        tasks = list(KIND_CHECKS[entry["kind"]] + COMMON_CHECKS)
        if entry["priority"] == 2:
            tasks.insert(0, "Obtain a fresh dated quotation or price-list snapshot")
        items.append({
            "name": entry["name"],
            "kind": entry["kind"],
            "priority": entry["priority"],
            "age_days": entry["age_days"],
            "tasks": [{"description": task, "status": "pending"} for task in tasks],
            "verification_status": "unverified",
        })
    return {
        "as_of": triage["as_of"],
        "total": triage["total"],
        "items": items,
        "verified_provider_prices": 0,
        "ready_for_commercial_pricing_claims": False,
        "warning": "Checklist generated, not completed. No source, quote, price or eligibility was verified.",
    }
