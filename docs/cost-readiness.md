# Cost research readiness gate — 2026-11-23

`orderpilot.cost_readiness.assess_cost_research_readiness` summarizes **manually entered** cost-source metadata before commercial research review. It distinguishes internal assumptions, dated external references, and fresh external references. It identifies gaps in source-type coverage without making network requests or exposing unverified amounts and URLs.

```python
from orderpilot.cost_readiness import assess_cost_research_readiness

report = assess_cost_research_readiness([
    {"name": "Synthetic internal estimate", "kind": "internal_assumption",
     "lkr_per_unit": "2.50", "observed_on": "2026-11-01", "source_url": ""}
], as_of="2026-11-23")
assert report["research_gaps"]
assert not report["ready_for_commercial_pricing_claims"]
```

The `has_minimum_reference_mix` indicator only means at least one non-stale provider quotation and one non-stale public price list are present **as metadata**, with no remaining internal assumptions. It does **not** establish that the URLs are authentic, independent, applicable in Sri Lanka, or correctly priced. Even when the reference mix is present, `ready_for_commercial_pricing_claims` remains `False` and `verified_provider_prices` remains zero. The 30-day freshness cutoff is a configurable review heuristic, not a standard of validity.

A reviewer must check dated official provider documents, billing units, currency and exchange assumptions, taxes, usage tiers, regional availability, contract restrictions, and actual merchant demand before relying on any commercial model. No provider quotations, merchant interviews, or price authenticity were independently verified in this change.

Run `python -m unittest discover -s tests -v` for the repository regression suite.
