# Cost-source provenance checks — 2026-11-16

OrderPilot's scenario rates remain **hypotheses**, not verified Sri Lankan provider quotations. The new `orderpilot.cost_sources.validate_cost_sources` function checks only the **shape and freshness metadata** of manually supplied cost evidence.

Each entry must provide a unique non-identifying name, a kind (`internal_assumption`, `public_price_list`, or `provider_quote`), a nonnegative decimal-string `lkr_per_unit`, a YYYY-MM-DD observation date, and a source URL. Public evidence requires an HTTPS URL; internal assumptions must have no URL. Future dates, duplicate names, unknown fields, malformed amounts, and oversized collections are rejected.

Example (synthetic assumption, **not a market quote**):

```python
from orderpilot.cost_sources import validate_cost_sources

report = validate_cost_sources([
    {"name": "Illustrative outbound message", "kind": "internal_assumption",
     "lkr_per_unit": "3.50", "observed_on": "2026-11-16", "source_url": ""}
], as_of="2026-11-16")
assert report["verified_provider_prices"] == 0
```

**Manual evidence gate:** Open each official provider pricing page; record the retrieval date, currency, applicable country, category, volume tier, included allowances, taxes, and billing unit. Confirm whether any exchange-rate conversion is needed. Compare competitors only on equivalent features and volumes. Do not label any figure as a current provider quote merely because its URL passes validation. A URL can be inaccurate, stale, or unrelated. No URL is fetched, no provider is contacted, and no customer information is collected.

**Buyer validation still missing:** interviews with consenting Sri Lankan social-commerce merchants, baseline order volumes, actual manual entry times, measured errors, willingness-to-pay responses, and consented pilot results. Keep such records private; publish only non-identifying aggregates. No demand, ROI, or pricing claim is established by this validator.

Run `python -m unittest discover -s tests -v` before merging changes. This module is intentionally offline and standard-library-only.

## Public reference URL hardening — 2026-11-17

Public price-list and provider-quote references must use an HTTPS URL with a
DNS-style hostname. The validator rejects bare hostnames such as `localhost`,
IP literals (including loopback and private addresses), userinfo credentials,
nonstandard ports, URL fragments, invalid DNS labels, and embedded whitespace or
control characters. Standard HTTPS port 443 and query strings remain supported.

This is a **reference hygiene** check, not a network security boundary: the
validator never fetches a URL, cannot confirm DNS resolution or redirects, and
does not establish that a domain is owned by a provider. Do not reuse these
checks as an SSRF defense for any future URL-fetching feature. Human review of
official sources, country applicability, taxes, currency, billing units, and
retrieval date remains mandatory.
