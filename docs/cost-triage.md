# Cost evidence manual-review queue — 2026-11-19

OrderPilot's `prioritize_cost_review` builds an offline, deterministic queue from the existing validated cost-source metadata. It helps a researcher decide **what to check next**, not whether a quoted price is authentic.

```python
from orderpilot.cost_triage import prioritize_cost_review

report = prioritize_cost_review([
    {"name": "Synthetic messaging assumption",
     "kind": "internal_assumption", "lkr_per_unit": "3.50",
     "observed_on": "2026-11-01", "source_url": ""}
], as_of="2026-11-19")
assert report["queue"][0]["priority"] == 1
assert not report["ready_for_commercial_pricing_claims"]
```

Review order: (1) replace internal assumptions with credible external evidence; (2) refresh external observations older than the configured threshold; (3) independently inspect recent external observations. Within each tier, older observations appear first, then names sort alphabetically. This is a workflow heuristic, **not a confidence score**.

The returned queue intentionally omits unverified amounts and URLs. The `ready_for_commercial_pricing_claims` field remains `False` even with recent external references: validation checks only metadata and does not inspect provider websites, verify Sri Lankan eligibility, billing units, taxes, exchange rates, negotiated terms, or willingness to pay. A human must verify those facts before publishing prices or margins.

Run `python -m unittest discover -s tests -v` to check regression tests. No customer information, provider outreach, external URL fetching, or paid services are involved.
