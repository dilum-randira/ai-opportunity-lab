# SMS prepaid cash exposure — 2026-11-26

Follow-up analysis of [November 25 provider observations](2026-11-25-sms-fallback-pricing.md), not a fresh tariff check or quote. Buyer hypothesis: a small social-commerce merchant paying for transactional order updates. No provider account, purchase, outreach or message delivery.

## Separate cash from consumption

For the previously observed [Text.lk Starter tariff](https://text.lk/pricing/), assume a LKR 500 top-up, 0.84 LKR per billable unit, no opening credit, no expiry, no additional fees, and identical future top-ups. These are conditional modeling assumptions, not confirmed checkout terms. A top-up adds monetary credit in this model; actual provider credit accounting must be confirmed.

| Monthly orders | Segments/order | Consumed LKR | Top-ups needed | Cash paid LKR | Closing credit LKR |
|---:|---:|---:|---:|---:|---:|
| 520 | 1 | 436.80 | 1 | 500 | 63.20 |
| 520 | 2 | 873.60 | 2 | 1000 | 126.40 |
| 520 | 3 | 1310.40 | 3 | 1500 | 189.60 |

Formula: consumption = orders × segments × unit rate; top-ups = ceiling(max(0, consumption − opening credit) / top-up amount); closing credit = opening credit + cash paid − consumption. This is a fixed-tier illustration, not an optimizer: a single larger purchase might qualify for a different rate. Do not assume credits can be carried forward or combined without confirming terms.

At hypothetical labor value 3466.67 and subscription 2500, the first-month cash-adjusted merchant value is 466.67, −33.33 and −533.33 respectively. Consumption-adjusted value is 529.87, 93.07 and −343.73. Neither is vendor profit or observed savings. Registration, retries, expiry, tax differences and support may further reduce value.

## Acceptance criteria for a future offline estimator

- Use decimal currency arithmetic, explicit opening credit, positive top-up amount and nonnegative integer billable units.
- Zero demand and sufficient opening credit require no purchase; exact multiples must not trigger an extra top-up.
- Distinguish cash paid, consumption and closing credit; reject negative inputs and nonfinite amounts.
- Treat segment counts as explicit inputs until provider-specific encoding and concatenation rules are validated.
- Never send messages or select a live paid plan automatically.

## Commercial decision

Do not promise positive merchant value merely because consumed-credit economics are positive: the two-segment example has negative first-month cash-adjusted value. Validate actual top-up rules, expiry, sender fees and willingness to pay before recommending a gateway. Competitor pricing and real buyer demand remain open research items.
