# Manual cost-evidence verification checklist — 2026-11-20

OrderPilot can turn the existing validated, offline cost-review queue into a
**pending** task checklist. This helps researchers consistently investigate
pricing assumptions before using them in commercial projections.

```python
from orderpilot.cost_checklist import build_cost_review_checklist

report = build_cost_review_checklist([{
    "name": "Illustrative messaging cost",
    "kind": "internal_assumption",
    "lkr_per_unit": "3.50",
    "observed_on": "2026-11-01",
    "source_url": "",
}], as_of="2026-11-20")
assert report["items"][0]["verification_status"] == "unverified"
assert all(t["status"] == "pending" for t in report["items"][0]["tasks"])
```

Each item includes source-kind-specific checks and shared checks for source
authenticity, currency and billing units, taxes and fees, Sri Lankan eligibility,
and a dated human review record. Stale external sources receive an additional
refresh task. Items retain the same priority order as `prioritize_cost_review`.

**Evidence limitations:** The checklist does not fetch provider websites,
contact vendors, independently verify quotations, or establish merchant
willingness to pay. Its output deliberately omits unverified amounts and URLs,
and never reports a verified price or commercial readiness. A human reviewer
must collect credible dated sources, validate applicable terms, and document
decisions before any external pricing or profitability claim. The example price
is synthetic, not a market quotation.

Run `python -m unittest discover -s tests -v` to check regression tests.
