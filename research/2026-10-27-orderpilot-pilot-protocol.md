# OrderPilot pilot evidence protocol — 2026-10-27

**Status:** proposed offline validation plan, not completed customer research. No customer interviews, willingness-to-pay measurements, production deployments, or live WhatsApp integrations are claimed.

## Decision to test

For a Sri Lankan social-commerce merchant, does a **human-approved**, local order-draft workflow reduce repeated manual entry without increasing mistakes enough to justify a modest monthly subscription? The competing baseline is the merchant's current WhatsApp Business app plus spreadsheet/POS workflow; do not assume merchants need a paid messaging API.

## Eligible data and privacy

Obtain voluntary, informed permission before observing tasks. Do not put customer names, phone numbers, message bodies, addresses, order IDs, invoices, screenshots, or merchant-specific financial records into this public repository. Use a private study workspace for consent and any sensitive evidence, with a retention/deletion plan. The public repo may contain only synthetic examples and aggregate, non-identifying metrics. Participants may withdraw; do not imply consent from a public social-media post.

## Paired measurement procedure

1. Define a task as transcribing one order into a draft with identical SKU catalog and price rules. Record baseline and assisted task durations in seconds, plus mistakes, using the existing four-column numeric schema in `orderpilot/paired_study.py`.
2. Counterbalance the task order when possible, use comparable synthetic orders, and note that learning effects and convenience sampling still limit causal claims.
3. Aim for at least 20 paired tasks across at least five independently consenting merchants; this is a **screening target**, not a statistical power calculation.
4. Report mean and median seconds saved, number of tasks made slower, errors before/after, and the descriptive bootstrap interval. Report adverse outcomes; never discard them to make the result look positive.
5. Independently ask about current pain and discuss a specific hypothetical subscription price. A positive ROI scenario is **not** willingness-to-pay evidence; no contact or sales activity is authorized by this document.

## Economics and go/no-go rules

Run `python -m unittest discover -s tests -v` before publishing any implementation changes. Model at least three monthly order volumes (for example 100, 300, 520) and three **hypothetical** subscription prices. Include merchant labor assumptions, setup amortization, hosting/support, service/utility messaging charges and applicable free allowances. Treat provider rates as unknown until independently checked. Use `orderpilot.unit_economics.project` for scenario arithmetic and distinguish its conservative sustained break-even bound from the earliest profitable order count; do not confuse rounded display values with exact arithmetic.

Do **not** label the product pilot-ready merely because simulated ROI is positive. A discussion-stage screen should require consented measurements, evidence of repeated buyer pain, at least one explicit price discussion, non-increasing errors, positive mean time saving with a positive descriptive interval lower bound, and at least one positive *modeled* price option. These are internal heuristics, not verified market demand or authorization to sell, message customers, charge, or deploy.

## Competitive differentiation hypothesis

- **Current manual process:** no new subscription, familiar workflow; manual re-entry and errors may be costly.
- **Generic messaging automation:** may support broader channels and workflows, but introduces setup, provider pricing, and integration complexity.
- **OrderPilot hypothesis:** low-friction local drafts, deterministic validation, durable idempotency, explicit human approval, and a clear audit trail. Verify whether merchants value these differences rather than assuming they do.

## Implementation acceptance criteria

Before integrating a pilot readiness calculator, add tests for invalid `study_kind`, nonfinite/negative durations, malformed pair tuples, noninteger error counts, merchant outcome counts exceeding consenting merchants, duplicate or out-of-range prices, negative observed time savings, increased error counts, synthetic data always failing the evidence gate, and correct handling of rounded ROI scenarios. Keep all code offline, standard-library-only and free of identifiers.

**Next decision:** only after consented, privately retained evidence exists should a human review whether to pursue a private pilot. No outreach, public deployment, or payment collection is approved.
