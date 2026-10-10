# AI Opportunity Lab

Private, research-driven experiments in AI-enabled software with credible customer and revenue hypotheses. Every prototype should have a clear problem, an explicit buyer, a safe demo, and a cheap way to validate willingness to pay.

## Experiment 001 — OrderPilot (approval-first social-commerce order drafts)

**Status:** offline deterministic proof of concept, **not an AI agent**, production system, or WhatsApp integration.

A small merchant may receive order messages via social channels and manually transfer line items into a spreadsheet or POS. OrderPilot v0 converts **manually supplied, consented** messages written in a narrow format (for example, 2 x NUT250; NUT500 x 1) into *review-only* structured drafts with catalog-backed LKR totals. It flags unknown SKUs, invalid quantities, duplicate message IDs within one batch, and ambiguous text. No customer messages are sent, no inventory is decremented, and no payment is taken.

### Try the demo (Python 3.10+, standard library only)

Run these commands from the repository root:

    python -m unittest discover -s tests -v
    python -m orderpilot.cli --catalog examples/catalog.json --messages examples/messages.json

Input catalog is a JSON object mapping SKU to decimal-string LKR prices. Messages are a JSON array of objects with id and text. The command prints DRAFT_ONLY_NO_EXTERNAL_ACTIONS and drafts with ready_for_review, needs_review, or duplicate status. Even ready_for_review means **a human must approve**; it does not mean the order is valid, accepted, fulfilled, or paid.

### Explicit limitations and safety boundary

- Narrow, deterministic English/SKU grammar; no free-form language understanding, OCR, Sinhala parsing, LLM, or live messaging API yet.
- Duplicate detection is **batch-local**, not durable across separate runs. Do not use for live order fulfillment without persistent idempotency and transactional validation.
- The CLI reads local files and writes JSON to stdout only. It does not connect to the internet or persist customer data.
- Catalog prices are trusted only as a demo input. No tax, shipping, discounts, payment processing, or stock availability checks.
- Test fixtures are synthetic; do not commit real customer names, phone numbers, addresses, or message histories.
- Human review is required for every draft. Unknown or malformed lines are never silently treated as valid.
- Production use would require authentication, access control, consent, retention/deletion policies, audit logs, input isolation, and official messaging API compliance.

### What would make this commercially useful?

A merchant interview must confirm order volume, manual-entry time, errors, existing workflow, and willingness to pay. Only then add a controlled UI and optional model-assisted extraction behind deterministic validation and explicit human approval. The market and monetization hypotheses are recorded in research/2026-10-10.md.

### Repo policy

Work only inside this repository. Branches are allowed for scoped changes; merge validated work to main when safe. Never add fake commits, secrets, personal data, unapproved deployments, or paid integrations.
