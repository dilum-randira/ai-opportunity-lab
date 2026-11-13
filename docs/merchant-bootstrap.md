# Merchant bootstrap sensitivity — 2026-11-13

`orderpilot.merchant_bootstrap.merchant_bootstrap(pairs, replicates=2000, seed=0)` estimates **descriptive uncertainty** in the mean seconds saved across independently grouped merchants. It uses reproducible seeded resampling *with replacement* of whole merchants, never individual orders. It reports empirical nearest-rank 2.5% and 97.5% percentiles, the fraction of resampled means strictly positive, the original merchant mean, observed positive/nonpositive merchant counts, a small-sample caution flag, and configuration. It returns no merchant identifiers or rows.

```python
from orderpilot.merchant_aggregation import aggregate_merchants
from orderpilot.merchant_bootstrap import merchant_bootstrap

pairs = aggregate_merchants([
    [(20, 10, 0, 0), (30, 20, 0, 0)],
    [(10, 8, 0, 0)],
    [(12, 13, 0, 1)],
])
report = merchant_bootstrap(pairs, replicates=2000, seed=42)
print(report["bootstrap_p025_seconds"], report["bootstrap_p975_seconds"])
```

**Inputs:** 2–1000 already-distinct merchant rows of `(mean_before_seconds, mean_after_seconds, any_error_before, any_error_after)`; finite durations 0–36000 seconds and integer 0/1 error flags. For repeated orders, aggregate per merchant first. Repetitions must be 100–5000, and seed an unsigned 32-bit integer. No raw customer/merchant data should be committed to this public repository.

**Sample-size disclosure:** `small_sample_caution` is true for fewer than 20 independently grouped merchants. This is an explicitly conservative product-review heuristic, **not** a statistically calibrated threshold. `observed_nonpositive_merchant_count` includes zero and negative savings. A positive bootstrap interval from a tiny or unrepresentative sample must not be presented as validated commercial impact.

**Interpretation limits:** Percentile bootstrap intervals are exploratory, not guaranteed coverage intervals, especially for tiny, biased, dependent or unrepresentative merchant samples. A positive interval does not establish causality, product-market fit, willingness to pay, or a financially viable subscription. Merchant identity, consent and sampling independence must be verified outside this code. The standard-library pseudorandom generator is for reproducibility, not security or cryptography. Do not publish identifiable merchant data or private grouping keys.

**Next commercial validation:** Obtain independently dated provider quotes, actual consented merchant time/cost observations, and buyer pricing discussions before using modeled ROI in sales decisions.
