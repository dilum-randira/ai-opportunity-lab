# Pilot evidence: independent merchant sampling (2026-11-10)

OrderPilot's offline `pilot_gate.screen` is a **conservative internal review heuristic**, not a production launch, research ethics, or sales approval. A prior version could count 24 paired order timings from only five merchants as 24 independent observations, even though repeated measurements from one merchant can bias the descriptive bootstrap interval.

## Required data contract

- Provide **at most one paired before/after observation per distinct consenting merchant**. `consenting_merchants` must be at least the number of pairs. The caller must verify uniqueness *outside this repository*; do not send or commit merchant identifiers, raw messages, contact details, or identifying metadata.
- Do not relabel repeated observations as distinct merchants. If a study records multiple orders per merchant, aggregate each merchant's timing and error outcomes before using this gate, or use a separately reviewed cluster-aware design. Do not treat per-order observations as independent.
- Consent and merchant distinctness are **self-reported and not verified** by the function. The existing minimum of 20 observations and five merchants is an internal heuristic, not a statistical power calculation; the one-pair-per-merchant rule effectively requires 20 distinct merchants for that check.
- A positive descriptive bootstrap interval does not establish causality, representative sampling, real-world savings, or willingness to pay. Modeled LKR profit is an assumption, not a verified buyer quote.

This safety restriction intentionally rejects previously accepted datasets with repeated observations. No customer outreach, spending, public deployment, or private-data publication is authorized by the screening result.
