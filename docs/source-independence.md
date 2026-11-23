# Cost-evidence hostname concentration review

`assess_source_concentration(rows, as_of="YYYY-MM-DD")` in `orderpilot.source_independence` reuses the strict cost-source metadata validator and performs an **offline** hostname-level concentration check. It does not fetch or verify any URL.

The report counts external references, distinct hostnames, reused hostnames, the largest same-host group, and hostnames appearing in both provider-quote and public-price-list categories. Internal assumptions are excluded from hostname counts. Output omits source URLs, hostnames and prices.

A repeated hostname is a **manual-review signal**, not evidence of fraud. Distinct hostnames are **not proof of independent organizations**: multiple domains can share an owner, and separate services may share one host. Manual research must confirm provider identity, publication date, Sri Lankan eligibility, currency, taxes, message units, contractual terms and current pricing. The function always reports zero verified independent providers.

Example:

```python
from orderpilot.source_independence import assess_source_concentration

rows = [
    {"name": "quote", "kind": "provider_quote", "lkr_per_unit": "2.50",
     "observed_on": "2026-11-20", "source_url": "https://vendor.example/quote"},
    {"name": "public", "kind": "public_price_list", "lkr_per_unit": "2.50",
     "observed_on": "2026-11-20", "source_url": "https://vendor.example/pricing"},
]
report = assess_source_concentration(rows, as_of="2026-11-24")
assert report["requires_independence_review"]
```

The example is synthetic, not a verified quotation or real provider.
