# Opportunity 004 — local-first multi-provider AI spend reconciliation

**Desk research date:** 2026-11-01 (Asia/Colombo). **Status:** unvalidated opportunity hypothesis. No customer contact, spend, API access, production integration, or sales.

## Buyer and expensive pain hypothesis

Target: small Sri Lankan software/AI agencies that maintain several client-facing AI features using more than one model provider. Hypothesized job: reconcile monthly provider spend against internal client/project budgets without exposing prompts, personal data, or API keys to a third-party dashboard. Potential pain: unexplained usage spikes, difficulty allocating shared provider accounts to clients, and delayed invoice reconciliation. **No buyer has confirmed this pain or willingness to pay.**

## Verified capability and competition — not a greenfield category

- [OpenAI Help Center: reviewing API usage and costs](https://help.openai.com/en/articles/10478918-reviewing-api-usage-and-costs), checked 2026-11-01, says the native Usage Dashboard supports project filters, token counts, exports and UTC-based reporting. **Native tools are a strong free/no-extra-product baseline.**
- [OpenAI Help Center: managing API projects](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform), checked 2026-11-01, documents project-level spending limits and alerts. The current guide distinguishes monitoring-only limits from enforced limits, and warns enforcement may not be instantaneous. Do not claim a new tool provides a guaranteed spend cap.
- [Claude Platform: Usage and Cost Analytics API](https://platform.claude.com/docs/en/manage-claude/usage-cost-analytics-api), checked 2026-11-01, supports grouping by model, workspace, API key and actor. Its beta reporting can lag up to 24 hours and be revised until roughly seven days after month-end. Anomaly alerts based on provider exports therefore cannot promise real-time detection or final invoices immediately.
- [Langfuse: token and cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking), checked 2026-11-01, already supports model cost tracking, dashboards and alerts. It is a serious established competitor; a generic dashboard would be undifferentiated.

## Differentiation hypothesis to test

A **local CSV-only, no-credentials** reconciliation workflow: import user-exported monthly aggregates from multiple providers, normalize UTC billing dates, map *explicit non-identifying* project labels to internal cost centers, flag unexplained variance against an offline budget, and generate a human-reviewed client-cost summary. Avoid raw prompts, API keys, personal user IDs and individual request traces. Do not invent a model's price from token counts if actual billed cost is available. Preserve provenance, provider name, currency and export timestamp; never silently mix USD and LKR.

The initial deliverable should be a standard-library CLI with strict allowlisted CSV columns, 256 KB file cap, duplicate-row checks, nonnegative finite Decimal amounts, immutable source labels, explicit FX input (no live rates), and deterministic reports. No autonomous alerts, billing or customer outreach.

## Commercial hypothesis and cost sensitivity (illustrative LKR only)

**Hypothetical** setup fee: LKR 12,000–25,000; **hypothetical** monthly reconciliation subscription: LKR 4,900–9,900. These are *price-test candidates*, not market prices. A local-only prototype has no necessary cloud hosting expense. A later hosted service could incur assumed LKR 2,000–8,000/month infrastructure plus 1–2 support hours at an assumed LKR 1,000–3,000/hour, giving **LKR 3,000–14,000/month** direct costs before taxes, customer acquisition, payment processing and development amortization. At one LKR 4,900 customer, the high-cost case loses money; at five customers, LKR 24,500 gross monthly revenue still needs retention, access controls and support economics. Do not treat any of these values as quotations.

## Disqualifiers and test plan

1. **Native alternative wins:** if a buyer can already export and allocate costs from provider dashboards in under 15 minutes/month, do not build a paid clone.
2. **Security:** never request provider admin credentials or upload sensitive billing exports into this public repository; synthetic fixtures only. Any hosted product requires separately approved security review.
3. **Accounting:** actual provider cost may differ from token-rate estimates due to discounts, committed capacity, credits and delayed corrections. Explicitly mark provisional periods and currency conversion assumptions.
4. **Evidence:** validate with at least five *consenting* agencies privately (outside this run, and only with separate authorization for outreach). Ask for current reconciliation time, error costs, provider count, existing tools and a concrete willingness-to-pay test. A synthetic demo is not buyer validation.
5. **Go/no-go:** prioritize only if multiple buyers report a measurable cross-provider attribution gap not covered by their existing tools and at least one discusses a specific paid price. Otherwise keep this as a research note.

## Priority relative to OrderPilot

**OrderPilot remains the implementation priority.** This is a distinct candidate for future evaluation, not a pivot or a claim that a market exists. No new public deployment, third-party contact, spending, or repository change outside this lab is authorized.
