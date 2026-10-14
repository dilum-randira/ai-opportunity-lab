# OrderPilot paid-pilot validation protocol (offline)

**Purpose:** Find out whether merchant time savings justify a recurring fee *before* building an expensive AI or messaging integration.

## Who to study

Ask five consenting merchants with repetitive manual order processing. Do not use unsolicited messages, publish identifying details, or collect actual customer chat content. Record their approximate daily order volume, present tools, current order-entry pain, and willingness to test a private pilot. Keep identifiable interview notes outside this repository.

## Paired task experiment

For each participating merchant, time at least 20 comparable tasks: first the manual baseline, then the assisted workflow, using synthetic or properly redacted orders. Counterbalance task order when feasible and record mistakes in each mode. Use the four numeric fields in `examples/synthetic-time-study.csv`: baseline_seconds, assisted_seconds, baseline_errors, assisted_errors. **Do not add IDs, phone numbers, addresses, or message text.** These columns can be copied into any local spreadsheet for analysis.

## Monthly scenario formulas

Let n be paired observations, D_i = baseline_seconds_i - assisted_seconds_i, Q = monthly orders, W = assumed LKR hourly labor cost, S = subscription, U = setup amortized per month, H = hosting/support allowance, M_s = service messages/order, M_u = utility templates/order, R_s and R_u = verified LKR per-message rates.

- Mean time saved/order = SUM(D_i)/n. Report negative values too.
- Estimated labor value/month = mean(D_i) * Q * W / 3600.
- Billable service messages = MAX(0, CEILING(Q*M_s, 1) - free_service_allowance).
- Utility templates = CEILING(Q*M_u, 1). No service-message free allowance applies to utility templates.
- Total monthly cost = S + U + H + billable_service_messages*R_s + utility_templates*R_u.
- Net estimated value = labor value - total monthly cost.

Use current official country-specific WhatsApp Business Platform rates if API messages are involved; do not charge free-app merchants for hypothetical Platform messages. Avoid pretending that a 10-order synthetic sample predicts a population outcome. Error reduction is a separate metric; do not monetize it without evidence.

## Go/no-go hypothesis

Continue toward a paid pilot if at least two merchants express specific interest, one agrees to discuss a concrete price, and the measured scenario is positive under conservative costs. These thresholds are proposed decision rules, not achieved milestones. No customers have yet been contacted or paid.
