# Integrated merchant ROI and messaging fees (offline)

OrderPilot now offers a **planning-only** calculation that composes the existing `orderpilot.unit_economics.project` input validation with the October 2026 per-business-number allowance model in `orderpilot.messaging_costs.estimate`. No live provider API, customer records, payments, outreach or deployment.

Run from the repository root (Python 3.10+, standard library only):

```python
from orderpilot.merchant_roi import evaluate

result = evaluate(
    monthly_orders=520,
    seconds_saved_per_order="60",
    hourly_lkr="400",
    subscription_lkr="2500",
    service_messages_by_number=[1040],  # count, NOT an actual phone number
    utility_messages=520,
    service_rate_lkr="3",                 # hypothetical LKR, NOT Meta pricing
    utility_rate_lkr="3",                 # hypothetical LKR, NOT Meta pricing
)
assert result["net_before_platform_messaging_lkr"] == "966.67"
assert result["platform_messaging_cost_lkr"] == "1680.00"
assert result["net_after_platform_messaging_lkr"] == "-713.33"
```

The before/after comparison **holds the same assumed labor savings constant** and isolates the impact of messaging charges. It is **not** a comparison of two functioning workflows, a quote, a measured ROI, or evidence of willingness to pay. The `service_messages_by_number` list is one aggregate monthly delivered-message count per business phone number; no identifiers are accepted or returned. Other message categories are explicit monthly delivered counts, not derived from order volume. A per-number allowance cannot be pooled across numbers.

## Calculation and precision

The integration validates the labor, subscription, setup and hosting inputs through the existing economics engine, then obtains validated message counts from the messaging estimator. It computes exact Decimal labor value, fixed monthly costs and messaging costs **before** rounding displayed LKR amounts. `positive_after_messaging_under_assumptions` uses the exact unrounded net, so a displayed `0.00` is not necessarily break-even. Negative zero is normalized to `0.00` for display.

The old single-allowance per-order break-even threshold is **not** reused for the multi-number case. A correct threshold for multiple numbers would need an explicit allocation policy and discrete message-count assumptions.

## Exclusions and validation

Rates and assumptions are caller supplied, not fetched from Meta. No currency conversion, recipient-market segmentation, utility/authentication volume tiers, BSP markup, taxes, refunds, churn, acquisition cost, or free-entry-point exemptions are modeled. Count only delivered, non-exempt messages. The free WhatsApp Business app is distinct from the paid Business Platform.

Run `python -m unittest discover -s tests -v` and `python -m compileall -q orderpilot tests`. Regression cases cover the 520-order sign reversal, zero messaging, per-number allowance isolation, all four categories, setup amortization, exact-cent boundary and invalid inputs. Synthetic cases are public-safe.

**Commercial gate:** obtain consented, privately retained merchant timing/error evidence and verified provider rate cards before making any pilot or pricing claim. No sales contact, sending, collection or deployment is authorized.
