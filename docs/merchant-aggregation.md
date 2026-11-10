# Merchant-level aggregation for repeated pilot observations (2026-11-11)

The offline `orderpilot.merchant_aggregation.aggregate_merchants(groups)` helper accepts **nested lists**, with exactly one group per distinct consenting merchant. Each group contains 1–100 paired order observations `(seconds_before, seconds_after, error_before, error_after)`. Error fields must be integer **0/1 flags** for each order, not counts. It returns one four-field observation per merchant, suitable for `pilot_gate.screen`.

For each merchant, before and after durations are separately averaged with Decimal arithmetic; error flags use **any error observed** within the group. These are merchant-level incidence indicators, **not** error rates, and varying numbers of observations per merchant can make comparisons biased. Do not interpret them as the original per-order error totals. The pilot gate compares the number of merchants with any errors before versus after; this is a deliberately different descriptive metric.

Synthetic usage:

```python
from orderpilot.merchant_aggregation import aggregate_merchants
pairs = aggregate_merchants([
    [(120, 60, 1, 0), (100, 55, 0, 0)],
    [(80, 70, 0, 0)],
])
assert len(pairs) == 2  # two merchants, not three independent observations
```

Limits: 1–1000 groups, 1–100 rows per group, durations 0–36000 seconds, binary error flags. Inputs with extra fields, IDs, messages, names, or phone numbers are rejected by the row schema. This helper does not verify that groups represent different merchants, consent, sampling quality, or that observations are truly paired. **Do not commit actual customer or merchant observations to this public repository.** Keep any identifying grouping key outside the repository and feed only appropriately consented, aggregated data into an approved private workflow. A positive pilot screen is not permission to contact customers, deploy, or charge fees.

Commercial validation remains pending: current messaging rates, merchant workflow observations, and explicit buyer willingness to pay are not established by this synthetic feature.
