# OrderPilot hypothetical scenario sensitivity

Use `orderpilot.sensitivity.compare_scenarios` to compare two to twelve **caller-defined** scenarios at the **same monthly order volume**. This is an offline planning aid, not a claim that merchants save time or will buy OrderPilot.

```python
from orderpilot.sensitivity import compare_scenarios

report = compare_scenarios([
    {"name": "conservative", "monthly_orders": 100,
     "seconds_saved_per_order": 0, "hourly_lkr": "600",
     "subscription_lkr": "1000"},
    {"name": "optimistic", "monthly_orders": 100,
     "seconds_saved_per_order": 60, "hourly_lkr": "600",
     "subscription_lkr": "1000"},
])
print(report["displayed_net_range_lkr"])
```

The model reuses the existing `unit_economics.project` calculations, including monthly message ceilings, any explicitly assumed service-message allowance, setup amortization, and caller-supplied rates. The result includes each scenario's cost breakdown, an illustrative net range rounded to cents, and whether **every** scenario is positive under its own assumptions.

**Interpretation:** Changing seconds saved, wage value, or messaging costs illustrates sensitivity, not probability. The endpoints are not statistical confidence bounds. Rounded net amounts can conceal sub-cent differences; the positive flags come from the underlying project calculation. Do not describe these outputs as observed pilot savings, causal effects, validated demand, verified provider prices, or a profitability forecast. In particular, modeled labor value is not necessarily realized cash savings.

**Commercial validation required:** Obtain consented merchant workflow measurements and comparable manual baselines; validate the actual buyer, willingness to pay and sales process; check current dated provider rates, taxes, regional eligibility, support workload, acquisition cost and churn before pricing decisions. Never put customer or private data in repository fixtures.

**Verification:** Run `python -m unittest discover -s tests -v` and the repository's CI before merging. No external services are contacted by the comparison function.
