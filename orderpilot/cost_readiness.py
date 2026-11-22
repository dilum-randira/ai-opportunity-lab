"""Conservative offline readiness gate for manual cost-evidence research."""
from orderpilot.cost_review import review_cost_evidence


def assess_cost_research_readiness(rows: list, *, as_of: str, max_age_days: int = 30) -> dict:
    """Report research gaps; external references are not verified prices."""
    report = review_cost_evidence(rows, as_of=as_of, max_age_days=max_age_days)
    counts = report["counts_by_kind"]
    external = counts["provider_quote"] + counts["public_price_list"]
    fresh = sum(item["kind"] != "internal_assumption" and not item["stale"]
                for item in report["items"])
    gaps = []
    if counts["internal_assumption"]:
        gaps.append("replace or independently corroborate internal assumptions")
    if not external:
        gaps.append("collect at least one dated external pricing reference")
    if external and not fresh:
        gaps.append("refresh external pricing references older than the review threshold")
    if not counts["provider_quote"]:
        gaps.append("seek a provider quote for the intended usage and region")
    if not counts["public_price_list"]:
        gaps.append("seek a public price list for independent comparison")
    return {
        "as_of": report["as_of"],
        "total": report["total"],
        "external_reference_count": external,
        "fresh_external_reference_count": fresh,
        "internal_assumption_count": counts["internal_assumption"],
        "stale_count": report["stale_count"],
        "research_gaps": gaps,
        "has_minimum_reference_mix": bool(
            fresh and counts["provider_quote"] and counts["public_price_list"]
            and not counts["internal_assumption"]
        ),
        "verified_provider_prices": 0,
        "ready_for_commercial_pricing_claims": False,
        "warning": "Reference mix is not verification. Check authenticity, currency, billing units, taxes, eligibility and quote terms manually.",
    }
