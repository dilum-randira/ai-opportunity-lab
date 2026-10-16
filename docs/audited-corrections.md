# OrderPilot audited corrections — offline guide

OrderPilot can now correct a parsed *pending* order draft, preserving the original message fingerprint and an immutable sequence of corrected versions. A correction does **not** approve, fulfill, send, or charge an order.

## Safe local usage

Python 3.10+ (standard library only). Start from the repo root:

```bash
python -m unittest discover -s tests -v
python -m orderpilot.queue_cli --db ./demo.sqlite3 ingest --catalog examples/catalog.json --messages examples/messages.json
python -m orderpilot.correction_cli --db ./demo.sqlite3 correct --id sample-002 --items examples/correction-items.json --catalog examples/catalog.json --expected-version 0 --note "validated items against catalogue"
python -m orderpilot.correction_cli --db ./demo.sqlite3 history --id sample-002
```

The `--db` argument points to a **local** SQLite file. The queue's original ingestion must already have occurred. Corrections require an exact `expected-version` (starting at 0) and a reason; if another edit advanced the version, the operation fails rather than overwriting it. A second correction uses version 1. Only pending orders can be corrected. Approval remains a separate explicit `orderpilot.queue_cli` command.

## What is guaranteed by this prototype

- Every corrected item is validated against a trusted local catalog; the user cannot inject their own price.
- Corrected and previous drafts are stored with a version and reason in local SQLite.
- SQL parameters and a single transaction protect database updates.
- Source ID and original SHA-256 message fingerprint stay unchanged.
- Duplicate message IDs remain blocked by the original queue.
- Corrections cannot bypass a prior approve/reject decision.
- Raw customer chat content is neither required nor included in the sample files.
- No outbound network calls, external databases, AI inference or billing.

## Limitations

- **Local demo, not production.** SQLite is for a single trusted device. No authentication, accounts, audit-log tamper resistance, encryption at rest, user permissions, backups or hosted multi-user workflow.
- The history function exposes structured draft data, so protect the SQLite file. Never check a live database or customer data into a public repository.
- Manual correction does not prove an AI feature or a paying market. Interview merchants and time real consented/redacted tasks first.
- Tests cover normal and adversarial cases but are not a security certification. See [OWASP AI Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) for action-approval safeguards.
