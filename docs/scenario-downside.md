# OrderPilot scenario downside screening

`orderpilot.scenario_downside.screen_downside` provides a deterministic summary of
**caller-selected hypothetical scenarios**, reusing the same input validation and
unit-economics model as `compare_scenarios`.

```python
from orderpilot.scenario_downside import screen_downside

base = {"monthly_orders": 100, "hourly_lkr": "600",
        "subscription_lkr": "100"}
report = screen_downside([
    {"name": "no measured savings", **base, "seconds_saved_per_order": 0},
    {"name": "optimistic assumption", **base, "seconds_saved_per_order": 60},
])
print(report["nonpositive_scenario_names"])
print(report["displayed_spread_lkr"])
```

The output identifies nonpositive modeled scenarios, their names, displayed
worst/best monthly net values in LKR, and their spread. The screen deliberately
does **not** assign likelihoods or calculate a percentage risk: the scenarios
are neither random samples nor a representative population. The modeled
economic value of labor time is not necessarily a cash saving. All net
figures are rounded to two decimal places by the existing project model;
the summary must not be used to establish precise break-even thresholds.

**Commercial evidence still required (reviewed 2026-11-22):** Verify merchant
workflow timings and consented baseline comparisons; obtain dated Sri Lankan
messaging and support costs, competitor subscription terms, customer
acquisition assumptions, churn estimates and willingness-to-pay evidence.
This module introduces no new external price quotes or demand evidence.
Avoid including private merchant records in repository tests or examples.

To verify: `python -m unittest discover -s tests -v`.
