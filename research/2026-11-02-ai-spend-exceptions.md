# Opportunity screen — Multi-provider AI spend exception reconciliation
**Research date:** 2026-11-02 (Asia/Colombo)  
**Status:** desk research and falsifiable hypotheses only. No interviews, credentials, spend, deployment, or confirmed demand.

## Buyer, pain and narrow workflow

Potential buyer: owner/operator or finance lead of a 3–20 person Sri Lankan software agency running multiple **billable client AI projects** across more than one provider or organization. The specific job is to reconcile provider-exported *monthly totals* to an internal client-project allocation ledger, identify unattributed spend and produce an approval-ready exception list **without ingesting prompts, API keys or customer identifiers**.

Pain hypothesis: project tags and billing entities are not always aligned with how an agency invoices clients; UTC reporting windows, pooled credits and organization-level charges can complicate reconciliation. This is a hypothesis to test, **not evidence that the problem is widespread**.

## Primary-source capability check (reviewed 2026-11-02)

1. OpenAI, **Exporting monthly usage details from the API Usage Dashboard** (Help Center, updated around 2026-10-29): monthly cost CSV exports and project-level activity exports already exist; enterprise invoices issued from 2026-04-01 no longer include the same detailed API cost lines, making the export workflow important. Source: https://help.openai.com/en/articles/20001072-exporting-monthly-usage-details-from-the-api-usage-dashboard
2. OpenAI, **Reviewing API usage and costs** (Help Center, updated around 2026-10-29): reports use UTC; project filters and organization boundaries matter; separate organizations are not combined automatically. Source: https://help.openai.com/en/articles/10478918-reviewing-api-usage-and-costs
3. Anthropic, **Usage and Cost API** (official documentation, accessed 2026-11-02): organization usage and cost breakdowns already exist; the older Usage and Cost Admin API is marked **legacy** and new integrations should use the Usage and Cost Analytics API. Do not build against a deprecated endpoint. Source: https://platform.claude.com/docs/en/manage-claude/usage-cost-api
4. Langfuse, **Token & Cost Tracking** (official documentation, accessed 2026-11-02): existing cost dashboards, per-model tracking, alerts and metrics API are mature competitors; ingested provider costs take precedence over inferred costs. Source: https://langfuse.com/docs/observability/features/token-and-cost-tracking
5. Stripe/Metronome, **Usage-based billing** (official product page, accessed 2026-11-02): mature metering, revenue recovery, and usage-based billing capabilities. This is an adjacent billing platform, not an agency reconciliation specialist. Source: https://stripe.com/billing/usage-based-billing

**Competitive conclusion:** a generic token-spend dashboard is **not** sufficiently differentiated. Native OpenAI/Anthropic reporting plus Langfuse already cover much of that need. The only plausible narrow gap is **local, offline, cross-export exception reconciliation and client-cost attribution** with an auditable explanation of unmatched amounts. Validate that gap before coding a full product.

## Differentiated offline MVP (not built)

- Import **synthetic-only** OpenAI and Anthropic cost export examples in a sandbox; document exact schemas, timezones, decimal precision and currency units before implementation.
- Require explicit provider, organization alias, period and internal client-project mapping; reject unknown/unmapped columns and ambiguous assignments instead of guessing.
- Reconcile per-provider totals, internal allocation totals and adjustment entries with Decimal arithmetic; surface exceptions with traceable source row counts, not prompt text or secrets.
- Export an exception-only CSV and a human approval checklist. No network access, billing API credentials, automatic invoicing, or payments.
- Preserve original source exports **outside this public repository** if real data is ever used; public fixtures must be synthetic and stripped of personal/contract data.

## Price and unit-cost hypotheses — NOT market quotes

Two possible models for validation: LKR 3,000–7,500 per agency per month for a local-only tool, or LKR 12,000–30,000 one-time onboarding plus optional support. These are **unverified willingness-to-pay hypotheses**, not prices promised to customers.

Illustrative agency month: 8 clients × 2 providers, 3 hours of reconciliation work, labor valued at LKR 1,000/hour = **LKR 3,000 gross labor value**. A LKR 5,000 subscription would be **LKR 2,000 negative** before setup/support, so that scenario **fails**. At 8 hours avoided, the gross labor-value scenario becomes LKR 8,000 and leaves LKR 3,000 before all other costs. This is arithmetic, not measured savings; actual workflow, taxes, error risk, customer acquisition and retention remain unknown.

## Cheap validation gates (future work, not outreach authorization)

- Obtain explicit permission before any real agency research. Test whether **at least three independently consenting** agencies have recurring *cross-provider reconciliation* issues not solved by existing dashboards.
- Compare one month of **synthetic** exports against a spreadsheet baseline; log total mismatch detection and time-to-reconcile, including false alarms.
- Confirm the buyer's minimum security requirements and whether offline local processing is valuable enough to pay for.
- **Kill or narrow** the idea if buyers already solve this in <30 minutes/month, cannot share even redacted data, or will not pay at least their expected support cost.
- Revisit sources and schema changes before coding an importer. Never store keys, prompt payloads, real client financial records or personal data in the public repo.

**Recommendation:** prioritize the proven OrderPilot engineering roadmap; keep this opportunity at desk-research stage until there is authorized, consented evidence of unmet demand.
