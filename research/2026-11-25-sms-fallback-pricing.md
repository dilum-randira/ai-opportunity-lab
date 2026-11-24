# Sri Lankan transactional SMS fallback — 2026-11-25

Desk research, public provider pages checked 2026-11-25. No quotes, accounts, purchases, outreach or delivery tests. Advertised rates are not contract terms.

## Provider comparison

- [Text.lk](https://text.lk/pricing/): Starter top-ups LKR 500–999 at 0.84 per unit, 1,000–2,499 at 0.79, 2,500–4,999 at 0.74, 5,000–9,999 at 0.69 and 10,000+ at 0.64. Business plan advertises 549/month plus 0.64/unit. Page says taxes included; confirm minimum purchase and segmentation.
- [e-SMS](https://e-sms.lk/pricing): advertised tax-inclusive rates 0.80, 0.72, 0.65, 0.58 and 0.53 per segment at increasing top-up thresholds. No monthly fee advertised. The same page lists a one-time 1,000 sender-name registration charge despite mentioning a free sender ID; confirm applicability. Provider describes English segments of 120 characters and Unicode limits of 70 initially and 67 thereafter; do not assume generic SMS limits apply.
- [Notify.lk](https://www.notify.lk/pricing/): Lite advertises 690/month including 450 transactional units, with additional units at 1.10 before applicable top-up tax. Pay&Go advertises 7,500 setup and 0.60/unit before tax. Page explicitly dates its rate update 2024-01-01; treat as stale until confirmed.
- [SMSWay](https://smsway.lk/): Silver advertises 1,500 setup and 1.00/unit; Gold 2,500 setup and 0.85/unit. Tax treatment and segment rules require confirmation.

## Illustrative consumption, not cash-flow or quotes

At 520 orders/month, one SMS per order, and a fixed hypothetical 0.84 LKR/unit, consumed credit costs 436.80/month for one segment or 873.60 for two. At 0.80 the corresponding amounts are 416 and 832. These are sensitivity inputs, not executable top-up baskets; actual tier depends on purchase size, unused credits, expiry, taxes and registration. Do not combine the lowest advertised rate with a small top-up without checking eligibility.

Using the earlier hypothetical 3,466.67 LKR labor value and 2,500 subscription, remaining modeled value is 529.87 or 93.07 at 0.84 for one or two segments respectively. This excludes hosting, support, retries, sender registration and all other costs. It is merchant-side modeled value, not OrderPilot profit.

## Decision

Keep review-only offline workflow as default. SMS fallback is a candidate only when a merchant has consent and a genuine transactional notification need. Do not send messages or integrate a paid gateway under this research task. Before implementation, validate provider-specific segment estimates, sender approval, delivery/refund policy, credit expiry, tax invoice and opt-out handling. Test Sinhala/Tamil templates with synthetic data only. Competitor subscription evidence and buyer willingness to pay remain unvalidated; see the November 3 research note for existing WhatsApp competitor observations.
