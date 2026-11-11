# Merchant-level sensitivity (2026-11-12)

`orderpilot.merchant_sensitivity.leave_one_merchant_out(pairs)` provides a deterministic stress test of the **merchant-level** average time savings used in OrderPilot pilot research. It is not a confidence interval, a statistical significance test, a causal effect estimate, or proof of product-market fit.

Each input row must be one independently grouped, consenting merchant: `(mean_before_seconds, mean_after_seconds, any_error_before, any_error_after)`. For multiple order observations, first use `aggregate_merchants(groups)` from `orderpilot.merchant_aggregation`. Never pass raw order observations as independent merchants. Merchant identity, consent, representativeness, and independence cannot be verified by this offline helper.

For each merchant, the helper removes that merchant and recomputes the mean saving across all remaining merchants. It returns the overall mean, the minimum and maximum leave-one-out mean, and whether **every** leave-one-out mean is strictly positive. All calculations use Decimal; the returned numeric values are strings. The result contains no identifiers or individual merchant rows.

```python
from orderpilot.merchant_aggregation import aggregate_merchants
from orderpilot.merchant_sensitivity import leave_one_merchant_out

pairs = aggregate_merchants([
    [(20, 10, 0, 0), (30, 20, 0, 0)],
    [(10, 8, 0, 0)],
])
report = leave_one_merchant_out(pairs)
assert report["merchant_count"] == 2
assert report["overall_mean_saving_seconds"] == "6"
assert report["leave_one_out_min_mean_saving_seconds"] == "2"
```

**Limits:** 2–1000 merchants, finite durations 0–36000 seconds, integer error flags 0 or 1. For only two merchants, each leave-one-out result is simply the other merchant's saving and should not be overinterpreted. An all-positive result does not establish external validity, eliminate selection bias, or imply commercial willingness to pay. Use only synthetic data in this public repository; do not commit real merchant/customer data, names, contact details, or private grouping keys.

**Commercial next steps:** independently verify current messaging-provider rates, merchant workflow measurements, and buyer pricing discussions before interpreting modeled ROI as evidence of a viable product.
