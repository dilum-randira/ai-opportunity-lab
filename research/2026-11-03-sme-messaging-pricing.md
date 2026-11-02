# November 3, 2026 — Sri Lankan merchant messaging economics: competitor and cost gate

**Evidence status:** desk research only, no merchant interviews, provider quotes, payments or outreach. Figures below are public indicative rates, not contract terms or validated OrderPilot prices. Source pages checked November 3, 2026.

## Buyer, pain and proposed offer

**Buyer hypothesis:** Sri Lankan social-commerce merchants processing roughly 100–1,000 monthly orders, particularly those using a WhatsApp Business inbox and manually entering orders into spreadsheets or a POS. **Pain hypothesis:** manual transcription, corrections, missed line items and costly platform integration. OrderPilot's proposed differentiator is a local, deterministic **review-only** order draft and an auditable, conservative offline ROI estimate, not automated messaging or an autonomous AI agent. Demand remains unproven.

## New public cost and competition evidence

1. **Meta-platform fee policy:** 360dialog, an official Meta Solution Partner, documented the October 1, 2026 change: the first 1,000 service messages *per business phone number* are free monthly, and subsequent service messages are chargeable. Utility templates inside the service window are also chargeable. This is relevant to the platform, not the free WhatsApp Business app. Source (published October 2026): https://360dialog.com/blog/whatsapp-service-message-charging-october-2026/
2. **Local provider example:** Bloomwire's Sri Lankan price page, explicitly updated October 20, 2026, lists a **LKR 8,500/month Starter plan**, **LKR 12,500/month Growth plan**, and separate Meta message charges. It is a *competitor's advertised plan*, not a verified quotation or market median. Source: https://www.bloomwire.lk/whatsapp-business-api-pricing
3. **Rate inconsistency warning:** The same Bloomwire page shows marketing at **about USD 0.084** in one section and **about USD 0.073** in another, and one FAQ describes in-window utility templates as free while the pricing table says they are chargeable. Do **not** hardcode this page as an authoritative Meta rate card; use Meta's official current rate card and an actual provider quote before costing a production integration.
4. **Alternative tools:** Chatwoot publicly offers a WhatsApp pricing calculator and shared-inbox tooling, showing that messaging cost calculators alone are not differentiated. Source (checked November 3, 2026): https://www.chatwoot.com/tools/whatsapp-pricing-calculator

## Explicit hypothetical economics

At 520 orders/month, 60 seconds saved/order and LKR 400/hour, modeled labor value is **LKR 3,466.67**. At LKR 2,500 subscription, the modeled pre-messaging net is **LKR 966.67**. With 1,040 service messages on one business number and 520 utility messages, assuming **LKR 3 per chargeable message** and 1,000 free service messages per number, messaging adds **LKR 1,680** and modeled net becomes **−LKR 713.33**. These rates are deliberately hypothetical and **not** Meta's published Sri Lankan rates. A zero paid-messaging, manual-review workflow avoids these modeled outbound API fees but is not proof of a usable production system.

**Cost uncertainty:** BSP subscriptions, per-message markups, Meta recipient-market tiers, FX, taxes, setup and support, customer acquisition, churn, and realization of labor savings are not validated. Model them before making any pricing claim. A plausible *test* range of LKR 1,500–3,500/month is an internal hypothesis, not a willingness-to-pay finding.

## Decision and next experiment

Prioritize an offline workload × subscription grid, **with explicit per-number message counts for every volume** rather than assuming all merchants have the same message routing. Before pursuing any paid pilot, obtain privately retained consented task timing/error evidence, document existing tools and current costs, and check whether at least two merchants report repeated pain and whether any buyer explicitly discusses a specific price. Do not contact anyone under this research task. If most merchants prefer the free Business app and have low order volumes, the honest result may be to stop building paid-platform integrations.
