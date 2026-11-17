# Cost evidence review — 2026-11-18

OrderPilot now provides `orderpilot.cost_review.review_cost_evidence` to triage **manually entered, hypothetical** cost evidence. It calls the existing strict provenance validator and adds a review-oriented summary: counts by source kind, observation ages, stale count, and whether all entries remain internal assumptions.

```python
from orderpilot.cost_review import review_cost_evidence

result = review_cost_evidence([
    {"name": "Synthetic message cost", "kind": "internal_assumption",
     "lkr_per_unit": "3.50", "observed_on": "2026-11-01",
     "source_url": ""}
], as_of="2026-11-18", max_age_days=30)
assert result["missing_external_evidence"]
assert result["verified_provider_prices"] == 0
```

The default 30-day threshold is an **internal review heuristic** (configurable from 1 to 365 days), not a claim that a recent quote is accurate. An observation becomes stale only when its age **exceeds** the threshold. Even non-stale public price lists and provider quotes remain unverified. Source URLs are never fetched. The summary deliberately omits price values and URLs to reduce accidental downstream presentation of unverified rates as validated facts.

Before any commercial use, independently check official current pricing, the retrieval date, Sri Lanka applicability, currency conversion, per-conversation versus per-message billing, included volume, taxes, and provider restrictions. This module cannot establish buyer willingness to pay or margins. It uses synthetic examples only, with no outreach, paid services, or private customer data.

Run `python -m unittest discover -s tests -v` for regression coverage.
