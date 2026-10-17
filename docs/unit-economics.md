# OrderPilot merchant unit economics (October 2026)

**Purpose:** help a Sri Lankan social-commerce merchant decide whether the software might be worth paying for. The output is a *hypothesis*, not a quotation, validated cost saving, or buyer commitment. Python 3.10+ and the standard library are sufficient. Nothing is sent to a network service.

## One monthly scenario

Run from the repository root:

```bash
python -m orderpilot.economics_cli --orders 520 --seconds-saved 62 --hourly-lkr 400 --subscription-lkr 3500 --service-messages-per-order 2 --service-rate-lkr 3 --free-service-messages 1000 --utility-messages-per-order 1 --utility-rate-lkr 4
```

Illustrative results: 1,040 service messages, 40 chargeable after the *assumed* 1,000-message allowance, 520 utility messages, **LKR 2,200** in message fees, **LKR 3,582.22** of labor-time value, and **negative LKR 2,117.78 monthly net value** after the assumed subscription. The LKR 3/LKR 4 per-message figures are invented for comparison—not official Meta Sri Lanka prices.

To explore an offline workflow, omit all message parameters; then the hypothetical result becomes **positive LKR 82.22** net value. This is an assumption that the same seconds can be saved without paid outbound messaging, which real merchant testing must verify.

## Compare different monthly volumes

```bash
python -m orderpilot.scenario_compare --volumes 100 300 520 1000 --seconds-saved 62 --hourly-lkr 400 --subscription-lkr 3500 --service-rate-lkr 3 --utility-rate-lkr 4 --free-messages 1000
```

The comparison shows *no-paid-messaging workflow* and *hypothetical paid Business Platform workflow* side by side. No paid messaging means manual steps or the free Business app, **not** a free WhatsApp Business Platform API. The same labor benefit is assumed on each pathway solely to isolate messaging expense.

### Assumptions you must check

- Labor value (LKR/hour) is a planning number, not necessarily reduced payroll cost.
- Message fees depend on destination, category, provider, allowances, rate-card updates and currency. Enter locally verified current numbers; no Meta API or live price lookup is performed.
- The optional free service allowance applies only to eligible **Business Platform** service messages; utility templates remain separately priced. The tool defaults to *zero* free allowance to avoid silently underestimating costs.
- An optional setup fee may be amortized across 1–120 months. Hosting and support expenses must be entered separately. Other missing expenses include tax, backups, customer acquisition and training.
- Order volumes above 1 million/month, unrealistic times or nonfinite numbers are rejected.
- Conservative break-even ignores free service allowances and message rounding; it is a planning approximation, **not exact**, and can be undefined if per-order variable costs consume the entire labor benefit.
- Pricing willingness must be **asked directly**. No actual merchants were contacted or billed.

## Validation before building paid integrations

1. Obtain informed consent for five merchant interviews; record pain, approximate monthly volume, tools currently in use, and a specific willingness-to-pay price.
2. Time at least 20 comparable tasks using synthetic or appropriately redacted orders, and measure quantity mistakes as well as speed.
3. Run the existing `orderpilot.paired_study` to calculate mean time saved. Use the estimated savings in the scenarios above.
4. Compare the cheapest possible offline-only process with paid Business Platform options.
5. Demand evidence from a prospective merchant before adding an autonomous AI agent or a live messaging integration.

References: [ODI Global (2026-10-07)](https://odi.org/en/publications/e-commerce-and-international-trade-in-sri-lanka-findings-from-a-survey-of-953-exporters-and-importers/); [Meta Business Platform Terms](https://www.whatsapp.com/legal/meta-terms-whatsapp-business); [Meta pricing overview](https://business.whatsapp.com/products/platform-pricing).
