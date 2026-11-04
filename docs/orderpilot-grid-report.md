# OrderPilot reproducible scenario decision report (2026-11-05)

**Prototype status:** All data is hypothetical, numeric and aggregate. This report is not a pricing recommendation, merchant validation, sales authorization or statistical break-even estimate. It makes no network requests.

Run from the repository root with Python 3.10+:

```sh
python -m orderpilot.grid_report_cli examples/orderpilot-grid-synthetic.json
python -m unittest discover -s tests -v
```

The CLI accepts the same strict, at-most-65,536-byte JSON schema as `orderpilot.merchant_grid_cli`, including rejection of duplicate keys, unknown customer-identifying fields, nonfinite numbers and excessive scenario counts. On invalid input, exit code 2 is returned without echoing input values or file paths.

The output contains `input_sha256` (SHA-256 of the exact input bytes), `grid` (the original modeled result), and `summary` (per-subscription counts of positive sampled workloads, the lowest **sampled** positive order volume and highest **sampled** negative volume). The JSON output has deterministic key order, indentation and trailing newline for repeatable comparisons. The hash is for local reproducibility, not proof of authenticity or consent; do not publish hashes derived from private data.

**Critical interpretation:** `lowest_sampled_positive_volume` is *not* a mathematically calculated break-even threshold. The real threshold might lie between sampled volumes or be non-monotonic when messaging charges and free allowances change. Profitability flags use the grid's exact Decimal calculation, not its rounded two-decimal display value. A zero displayed net can therefore still be classified as positive if the underlying exact amount is above zero.

The model excludes taxes, FX, BSP fees, provider volume tiers, churn, acquisition and messaging exemptions. Verify official Meta/BSP rate cards and dates before customer quotations. Neither modeled ROI nor a synthetic workload proves willingness to pay. No outreach, deployment, messaging, or payment collection is authorized.
