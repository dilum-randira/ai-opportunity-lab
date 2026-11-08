# OrderPilot aggregate pilot evidence gate — 2026-11-09

This is an **offline internal screening heuristic**, not pilot approval or proof of product-market fit. It extends the [2026-10-27 protocol](../research/2026-10-27-orderpilot-pilot-protocol.md). Do not publish private study data, names, order IDs, phone numbers, messages, addresses, merchant financial records, or consent records.

## Use

```python
from orderpilot.pilot_gate import screen

example = screen(
    study_kind="synthetic",
    pairs=[(120, 60, 1, 0)] * 24,
    consenting_merchants=5,
    merchants_reporting_repeated_pain=3,
    merchants_discussing_price=2,
    modeled_net_lkr="1200",
)
assert example["status"] == "EVIDENCE_INSUFFICIENT"
```

The example is **synthetic**: it can never pass the consented-observation check. In private, with actual informed consent and appropriate retention/deletion controls, an analyst may separately evaluate non-identifying aggregate counts. The function cannot verify consent, merchant independence, price discussion authenticity, or whether the modeled net value reflects actual costs.

The gate requires all eight conditions: explicitly consented aggregates; at least 20 paired tasks from at least five merchants; at least one merchant reporting repeated pain; at least one price discussion; no increase in recorded errors; positive **unrounded** average seconds saved; positive lower bound of the **descriptive** bootstrap interval; and positive hypothetical modeled net value. Passing only means **human review candidate**, not permission to contact customers, deploy, charge, or declare pilot readiness. The bootstrap interval is descriptive and may be unreliable for nonrandom, clustered, or very small studies. The sample targets are heuristics, not a statistical power calculation.

## Verification

Run `python -m unittest discover -s tests -v` and `python -m compileall -q orderpilot tests` locally or in CI. Do not claim tests pass without execution. This module is standard-library-only, does not read files, and makes no network requests. Keep consent and raw observations outside this public repository.
