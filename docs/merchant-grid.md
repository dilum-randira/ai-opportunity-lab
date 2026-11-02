# OrderPilot explicit workload × price grid (offline)

The grid compares up to **20 distinct monthly order volumes** against up to **10 hypothetical monthly subscriptions**, capped at **100 cells**. Each workload supplies *explicit* delivered-message counts by business phone number; it does **not** infer a message multiplier or routing policy from order volume. The service allowance remains per business phone number. No customer IDs, phone numbers, addresses, API keys, network requests, messaging or payments are involved.

From the repository root (Python 3.10+, standard library only):

```python
from orderpilot.merchant_grid import compare

report = compare(
    workloads=[
        {"monthly_orders": 100, "service_messages_by_number": [200], "utility_messages": 100},
        {"monthly_orders": 520, "service_messages_by_number": [1040], "utility_messages": 520},
    ],
    subscription_prices_lkr=["2000", "2500", "3000"],
    seconds_saved_per_order="60", hourly_lkr="400",
    service_rate_lkr="3", utility_rate_lkr="3",
)
assert report["scenario_count"] == 6
assert report["rows"][1]["prices"][1]["net_after_messaging_lkr"] == "-713.33"
```

**Schema:** `workloads` is a list of objects requiring `monthly_orders` (positive integer) and `service_messages_by_number` (a list of *aggregate counts*, not phone numbers). Optional per-workload fields: `utility_messages`, `marketing_messages`, `authentication_messages` (nonnegative integer delivered-message counts). Unknown fields are rejected, so raw customer data cannot be passed through the grid. Volumes and price options must be distinct. The grid preserves caller order. All fees are caller-supplied LKR assumptions; no provider rates are downloaded.

Each row returns the volume, number of business phone numbers, aggregated message counts, monthly messaging fee, and a price-by-price before/after messaging net and **exact Decimal positivity** flag. Displayed `0.00` can still be positive or negative at sub-cent precision; do not infer break-even from the rounded string. A single workload may represent any message routing assumption, but each assumption must be entered explicitly and should be documented separately.

**Comparison limitations:** This is scenario arithmetic, not a measured merchant workflow, market validation, pricing recommendation, or willingness-to-pay result. It excludes BSP fees, taxes, FX, message-tier discounts, free-entry-point exemptions, customer acquisition, churn and labor realization. The free WhatsApp Business app is not the paid Business Platform. Rates and service-message rules can change. Verify official Meta rate cards, recipient-market classification, actual BSP quotes and private consented merchant timing data before proposing a pilot. The script never contacts customers or deploys anything.

**Checks:** `python -m unittest discover -s tests -v` and `python -m compileall -q orderpilot tests`. Grid regression tests cover 2×3 scenarios, per-number allowance isolation, sub-cent flag semantics, invalid prices, identifiers/unknown fields, malformed counts, duplicates and bounded grid sizes.
