# OrderPilot offline merchant-grid JSON CLI

**Status (2026-11-04):** Local-only prototype. All prices, merchant volumes, time savings and delivered-message counts are **hypothetical**. This command does not fetch provider pricing, contact customers, send messages, or deploy anything.

Run from the repository root with Python 3.10+:

```sh
python -m orderpilot.merchant_grid_cli examples/orderpilot-grid-synthetic.json
python -m unittest discover -s tests -v
```

The CLI accepts one UTF-8 JSON file up to **65,536 bytes**. It rejects duplicate keys, non-finite numbers, unexpected fields, invalid counts and identifiers, and uses Decimal for fractional JSON numbers. It prints aggregate scenario results as JSON on stdout. Invalid input returns exit code 2 without echoing submitted values or the local file path.

## Input contract

Required top-level fields: `workloads`, `subscription_prices_lkr`, `seconds_saved_per_order`, `hourly_lkr`. Optional: `service_rate_lkr`, `utility_rate_lkr`, `marketing_rate_lkr`, `authentication_rate_lkr`, `free_service_messages_per_number`, `hosting_support_lkr`, `setup_lkr`, `setup_amortization_months`.

Each workload requires `monthly_orders` and `service_messages_by_number` (an array of **numeric counts**, not phone numbers). Optional workload fields: `utility_messages`, `marketing_messages`, `authentication_messages`. Other fields are rejected. Up to 20 workloads, 10 distinct subscription prices and 100 cells are allowed; volume counts must be distinct.

**Privacy:** Never place real names, telephone numbers, message bodies, customer IDs, order IDs, credentials, private merchant financials, or consent records in public examples or commits. The parser's schema rejection is defense in depth, not a substitute for checking files before publication. Local input may still contain sensitive information; keep real customer records outside this repository.

**Economic interpretation:** Per-number service allowances are kept separate. Positive/negative flags use exact Decimal arithmetic, even when a small net value displays as `0.00`. The model omits taxes, FX, BSP fees, provider volume tiers, acquisition/churn and exemptions. The free WhatsApp Business app is not the paid Business Platform. Neither a positive ROI cell nor a passed test establishes willingness to pay.

## Next evidence needed

Obtain permission before any merchant study, keep raw records private, verify current official Meta and BSP rate cards and dates, compare manual workflows against assisted workflows, and record adverse task outcomes. No outreach or payments are authorized by this CLI.
