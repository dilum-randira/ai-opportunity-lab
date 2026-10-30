# Offline messaging cost scenarios (October 2026)

`orderpilot.messaging_costs.estimate` models hypothetical monthly WhatsApp **Business Platform** charges using aggregate message counts and user-entered LKR rates. It does not connect to Meta, send messages, collect contacts, or quote provider prices. Python standard library only.

    from orderpilot.messaging_costs import estimate

    result = estimate(
        service_messages_by_number=[1040],
        utility_messages=520,
        service_rate_lkr="3",   # illustrative, NOT a Meta rate
        utility_rate_lkr="3",   # illustrative, NOT a Meta rate
    )
    assert result["counts"]["service_billable"] == 40
    assert result["cost_lkr"]["total"] == "1680.00"

**Data contract:** `service_messages_by_number` contains 1–20 nonnegative integer *delivered* service-message counts, one count per business phone number (no phone numbers or identifiers). Other categories accept nonnegative integer delivered counts. Rates are finite nonnegative decimal-compatible LKR values, supplied by the caller. The default free service allowance is 1,000 per business phone number, reset each calendar month. No unused allowance transfers between phone numbers or months. All currency values are strings rounded to two decimals using `ROUND_HALF_UP`; arithmetic uses unrounded Decimal values.

**Exclusions:** The caller must exclude inbound, reactions, and free-entry-point-exempt deliveries; no actual API classifications are fetched. The model does not handle different recipient-country rates within one category, utility/authentication volume discounts, taxes, BSP charges, FX conversion, or Meta Business Agent token charges. A service reply and a utility template are different categories; utility templates do **not** consume the service free tier. The free WhatsApp Business mobile app is not the paid Business Platform.

**Verification:** `python -m unittest discover -s tests -v` and `python -m compileall -q orderpilot tests`. This tool is for planning only, not automatic messaging or production billing.

For sources, buyer/competitor assumptions and a synthetic sensitivity case, see `research/2026-10-31-orderpilot-messaging-economics.md`.
