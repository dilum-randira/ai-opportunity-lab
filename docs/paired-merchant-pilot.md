# OrderPilot paired timing study — reproducible merchant pilot

This is an **offline** instrument to determine whether a proposed order-review workflow is economically worthwhile. It does not read WhatsApp, identify customers, send messages, approve orders, charge payments, or claim actual sales growth.

## Run a fully synthetic example

From the repository root, with Python 3.10+:

```bash
python -m unittest discover -s tests -v
python -m orderpilot.paired_study \
  --study examples/synthetic-paired-study.csv \
  --monthly-orders 520 \
  --hourly-lkr 400 \
  --subscription-lkr 3500 \
  --operating-lkr 2200
```

The example has three **invented** before/after observations (120→60 seconds, 150→80 seconds, 90→85 seconds). Mean time saved = **45 seconds**; median = **60 seconds**. Modeled gross labor time value is **LKR 2,600** per month, with **LKR 5,700** assumed monthly costs, producing **LKR -3,100** estimated net value. These are not verified local labor or messaging rates.

## Input schema

The CSV must contain exactly these columns, in order:

| Column | Type | Meaning |
|---|---|---|
| `baseline_seconds` | nonnegative number ≤36,000 | Time to complete the task manually |
| `assisted_seconds` | nonnegative number ≤36,000 | Time to complete a comparable assisted task |
| `baseline_errors` | integer 0–100 | Errors in manual task |
| `assisted_errors` | integer 0–100 | Errors in assisted task |

The importer rejects extra columns, duplicate headers, NaN/Infinity, negative numbers, fractional errors, files >256 KB, and studies >5,000 rows. Never add customer names, phone numbers, order content, locations, or other identifiers; use **only consented numeric measurements** or synthetic examples. Keep actual merchant records outside this public repository.

## Interpreting results

- Mean and median seconds saved may be negative: this is informative, not a software error.
- A deterministic 500-resample paired bootstrap provides an approximate descriptive interval when at least two observations are present. It does **not** establish causality or statistically representative merchant demand.
- When the mean is negative, the illustrative ROI scenario floors time savings at zero; inspect the `assistance_slowed_average` flag and raw timing statistics.
- `hourly-lkr` is an assumed value of time; freeing owner time does not necessarily save payroll.
- `operating-lkr` must be supplied after estimating real hosting, support, official messaging and provider costs. Distinguish free WhatsApp Business from paid Business Platform charges.
- A positive model output does not prove buyers will subscribe. Ask about willingness to pay directly.

## Decision gate

Invite five merchants to participate voluntarily; measure at least 20 paired redacted/synthetic tasks, identify obvious error-reduction opportunities, and privately demonstrate audited manual corrections. Require at least one explicit paid-pilot pricing discussion before committing to expensive AI or messaging integrations. Do not perform outreach, billing, or production deployment without separate approval.
