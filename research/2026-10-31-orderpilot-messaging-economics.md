# OrderPilot — October 2026 messaging cost and buyer hypothesis

**Researched:** 2026-10-31. **Status:** desk research and synthetic cost scenarios only; no merchant contact, confirmed willingness to pay, provider quote, or production integration.

## New cost risk

On **2026-10-01**, WhatsApp Business Platform service replies became billable after **1,000 delivered service messages per business phone number per calendar month**; utility templates delivered inside an open customer-service window became chargeable. The free service allowance is *per phone number*, not pooled across a business account. Sources: [Meta's developer pricing documentation](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) (login may be required), [360dialog analysis, September 2026](https://360dialog.com/blog/whatsapp-service-message-charging-october-2026/), and [Voltade, updated 2026-10-16](https://voltade.com/global/blog/whatsapp-replies-stop-being-free-1-october-2026). Service pricing depends on recipient market and billing currency; Sri Lanka has its own rate grouping in the October card, so do not use old Rest-of-Asia-Pacific rates without verification.

The **free WhatsApp Business mobile app** is not the paid Business Platform; this change must not be represented as a fee for manually replying in the app. Exclude exempt free-entry-point messages, inbound messages and reactions from this simplified model. Utility/authentication volume tiers, taxes, currency conversion and Business Solution Provider (BSP) markups require separate review.

## Competitive baseline and buyer

- **Likely buyer hypothesis:** Sri Lankan small social-commerce merchant receiving repetitive order messages and manually re-entering orders into a spreadsheet or POS. Pain: transcription time, wrong SKUs, duplicated orders, unclear approval. None of these pains has been independently validated with a consenting merchant.
- **No-purchase alternative:** WhatsApp Business app plus spreadsheet; familiar and no new OrderPilot subscription. It is the default comparator.
- **Established competitor:** [respond.io's published pricing page](https://respond.io/pricing), checked 2026-10-31, shows displayed USD Starter **$79/month**, Growth **$159/month**, Advanced **$279/month**; plan billing, active-contact tiers and extra fees vary. Its page explicitly says WhatsApp usage fees are *not* included. OrderPilot should not claim feature parity with a multichannel customer platform.
- **Differentiation to test:** offline, human-approved order drafts, SKU validation, idempotent review, low training overhead, and transparent cost scenarios rather than a full messaging platform. These are hypotheses, not proven advantages.

## Synthetic economics: why message billing matters

Assumptions for illustration, **not market prices**: 520 orders/month, 60 seconds of manual entry saved per order, LKR 400/hour labor value, hypothetical OrderPilot subscription LKR 2,500/month, one Business Platform phone number, 2 delivered service replies per order, 1 utility template per order, and caller-supplied hypothetical service/utility rates of LKR 3 per delivered message. No other costs are included.

- Labor value: 520 × 60 / 3600 × 400 = **LKR 3,466.67** per month.
- Without paid messaging: labor value minus subscription = **LKR +966.67** (before support, taxes, setup, etc.).
- With Business Platform messaging: 1,040 service replies minus 1,000 free = **40 billable service messages**; 520 utility templates are billable. Hypothetical message cost = (40 + 520) × LKR 3 = **LKR 1,680**.
- Under *these hypothetical assumptions*, net value = 3,466.67 − 2,500 − 1,680 = **LKR −713.33**. This reverses the sign of the modeled benefit. It does **not** prove an actual merchant loses money or that LKR 3 is the real market rate.

Run the new `orderpilot.messaging_costs.estimate` with only aggregate counts and caller-supplied rates; never put phone numbers, customer data, merchant identities or message text in this public repository.

## Pilot decision / validation gaps

1. Validate the buyer's actual workflow and order volume with **explicit consent** before using any non-synthetic data. No outreach is authorized in this run.
2. Obtain current Meta **Sri Lanka destination-market** rate cards and the merchant's BSP fee schedule; model scenarios both **with** and **without** paid messaging. Never present these sample rates as quotes.
3. Compare 100, 300 and 520 monthly orders and several hypothetical subscription prices, including support, setup amortization and training costs. Test if a purely offline approval-first tool is preferable to an API integration.
4. Measure paired task times, error rates and willingness-to-pay discussions privately; aggregate only non-identifying counts for public artifacts. A positive modeled ROI is not buyer validation.
5. **Go/no-go:** no live messaging, payments, public deployment or sales activity without separate approval.

## Evidence quality

The date and billing-rule changes above are corroborated by multiple provider explanations referring to Meta's documentation; Meta's developer page may require login. The respond.io amounts are directly visible on its official pricing page but can change and are not comparable one-for-one with a narrow offline tool. All LKR prices, labor rates and volumes in the worked example are *invented scenario inputs*, not collected market observations.
