"""Offline triage of cost-source metadata; not a provider price verification."""

from orderpilot.cost_sources import validate_cost_sources


def review_cost_evidence(rows: list, *, as_of: str, max_age_days: int = 30) -> dict:
    """Flag stale observations and missing external evidence without network access.

    The age threshold is a review heuristic, not a guarantee of price validity.
    All sources require manual verification regardless of age.
    """
    if type(max_age_days) is not int or not 1 <= max_age_days <= 365:
        raise ValueError("max_age_days must be an integer from 1 to 365")
    validated = validate_cost_sources(rows, as_of=as_of)
    items = []
    counts = {"internal_assumption": 0, "public_price_list": 0, "provider_quote": 0}
    stale = 0
    for entry in validated["entries"]:
        counts[entry["kind"]] += 1
        is_stale = entry["age_days"] > max_age_days
        stale += int(is_stale)
        items.append({
            "name": entry["name"], "kind": entry["kind"],
            "age_days": entry["age_days"], "stale": is_stale,
            "requires_manual_verification": True,
        })
    return {
        "as_of": validated["as_of"], "max_age_days": max_age_days,
        "total": len(items), "counts_by_kind": counts,
        "stale_count": stale,
        "missing_external_evidence": counts["internal_assumption"] == len(items),
        "verified_provider_prices": 0,
        "items": items,
        "warning": "Recency is not authenticity. Verify official rates, billing units, currency, taxes, and applicability manually.",
    }
