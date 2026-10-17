# AI Opportunity Lab

Public, research-driven experiments in AI-enabled software with credible customer and revenue hypotheses. Every prototype should have a clear problem, an explicit buyer, a safe demo, and a cheap way to validate willingness to pay.

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


## Iteration 002 — Durable local review queue

The stateless parser remains available. The new SQLite-backed queue remembers processed message IDs across runs, flags changed-text ID conflicts, and records explicit local approve/reject decisions with an audit trail. It never sends messages, processes payments, or fulfills orders.

Run from the repository root (Python 3.10+, standard library only):

    python -m unittest discover -s tests -v
    python -m orderpilot.queue_cli --db demo.sqlite3 ingest --catalog examples/catalog.json --messages examples/messages.json
    python -m orderpilot.queue_cli --db demo.sqlite3 list --state pending
    python -m orderpilot.queue_cli --db demo.sqlite3 review --id sample-001 --decision approve
    python -m orderpilot.queue_cli --db demo.sqlite3 audit --id sample-001

The first ingest creates two drafts and flags the third sample message as `id_conflict` (same ID, different text). Repeated ingests do not overwrite earlier records. Only drafts with no parse issues may be locally marked approved. Approval is bookkeeping, **not** authorization to ship, charge, or message a customer. The database retains parsed line items, source IDs, message hashes, timestamps, and notes but **not raw message text**; this is data minimization, not anonymization. Keep database files private, do not commit them, and use synthetic or consented/redacted inputs only. No authentication, encryption at rest, retention policy, or multi-user isolation is implemented. See `research/2026-10-12.md` for commercial hypotheses and next validation gate.


## Iteration 004 — Merchant unit-economics and volume comparison (October 18, 2026)

OrderPilot now provides **offline LKR financial experiments** to help test *whether* a proposed workflow is worth paying for before building costly live integrations. These are NOT real merchant results or verified Meta Sri Lanka rates.

Run from the repository root:

```bash
python -m unittest discover -s tests -v
python -m orderpilot.economics_cli --orders 520 --seconds-saved 62 --hourly-lkr 400 --subscription-lkr 3500
python -m orderpilot.scenario_compare --volumes 100 300 520 1000 --seconds-saved 62 --hourly-lkr 400 --subscription-lkr 3500 --service-rate-lkr 3 --utility-rate-lkr 4 --free-messages 1000
```

Every user-supplied per-message LKR rate is an **assumed scenario input**, not a current provider quote. The zero-cost messaging workflow means no paid *outbound* API messages, not that the Meta Business Platform API is free. Read [full usage and pricing cautions](docs/unit-economics.md) and the [October 18 evidence review](research/2026-10-18.md).

**Public repository safety:** This repository contains synthetic test data only; never push API keys, tokens, customer messages, phone numbers, addresses, invoices, local SQLite databases or private business files. There is no public web deployment or customer-facing order system.
