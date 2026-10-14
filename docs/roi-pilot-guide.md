# OrderPilot — merchant ROI pilot guide

This experiment is intended to **disprove an uneconomic product idea early**, not to assert customers will pay for OrderPilot. Do not upload order texts or personal information.

## Reproduce the offline ROI scenario

Run from the repository root (Python 3.10+):

```bash
python -m unittest discover -s tests -p 'test_roi_simple.py' -v
python - <<'PY'
from orderpilot.roi_simple import estimate_roi
print(estimate_roi(orders_per_month=520, seconds_saved_per_order=62,
                   hourly_lkr=400, monthly_subscription_lkr=3500,
                   monthly_operating_lkr=2200))
PY
```

Expected monthly estimated net value: **LKR -2117.78** under those assumptions. A negative result means hypothesized savings are less than modeled subscription and operating costs, not necessarily a negative outcome for all merchants.

## Evidence to collect before a paid pilot

1. Invite five consenting merchants for short interviews, without bulk outreach.
2. Ask about manual order volume, minutes per order, errors, existing alternatives and actual subscription willingness to pay.
3. With permission, time at least 20 paired tasks using synthetic or fully redacted examples. Record numeric timings only.
4. Use local labor rates, independently verified provider messaging rates and support/hosting estimates. Compare the free WhatsApp Business app to paid Business Platform integrations separately.
5. Document where the assisted workflow fails, including corrections and privacy concerns. Do not claim faster processing without a meaningful paired study.
6. Only propose a private demo or paid pilot after an explicit willingness-to-pay discussion.

## Risks and interpretation

- The estimator measures modeled labor value minus declared costs only: it excludes churn, sales uplifts, taxes, support, opportunity cost and training.
- Customer time saved is not necessarily cash saved. It may free the owner's time without reducing payroll.
- The existing prototype has no production security, messaging API integration, merchant authentication or live customer deployment.
- The numerical values are **hypothetical**, not measured merchant demand.
- Related prior research: [October 13](../research/2026-10-13.md).
