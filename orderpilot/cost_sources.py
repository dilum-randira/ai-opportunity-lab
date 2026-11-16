"""Validate provenance metadata for hypothetical LKR cost assumptions.

No network calls are made. Validation never establishes that a price is real.
"""
from datetime import date
from ipaddress import ip_address
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

KINDS = {"provider_quote", "public_price_list", "internal_assumption"}


def validate_cost_sources(rows: list, *, as_of: str) -> dict:
    """Validate bounded, non-personal cost evidence; require manual source checks."""
    try:
        today = date.fromisoformat(as_of)
        if today.isoformat() != as_of:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("as_of must be YYYY-MM-DD") from None
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
        raise ValueError("rows must contain 1..100 entries")
    seen, entries = set(), []
    for row in rows:
        keys = {"name", "kind", "lkr_per_unit", "observed_on", "source_url"}
        if not isinstance(row, dict) or set(row) != keys:
            raise ValueError("each row requires exactly five fields")
        name, kind, price, observed, url = (row[k] for k in
            ("name", "kind", "lkr_per_unit", "observed_on", "source_url"))
        if (not isinstance(name, str) or not 1 <= len(name) <= 80
                or name != name.strip() or not name or name in seen):
            raise ValueError("names must be unique nonblank strings")
        seen.add(name)
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError("unsupported source kind")
        if (not isinstance(price, str) or not price or len(price) > 30
                or any(c not in "0123456789." for c in price)
                or price.count(".") > 1):
            raise ValueError("price must be a nonnegative decimal string")
        try:
            amount = Decimal(price)
        except InvalidOperation:
            raise ValueError("invalid price") from None
        if not amount.is_finite() or amount < 0 or amount > Decimal("1000000000"):
            raise ValueError("price outside allowed range")
        try:
            day = date.fromisoformat(observed)
            if day.isoformat() != observed or day > today:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError("observed_on must be a valid past date") from None
        if not isinstance(url, str) or len(url) > 2048:
            raise ValueError("invalid source URL")
        if kind == "internal_assumption":
            if url:
                raise ValueError("internal assumptions cannot claim a source")
        else:
            try:
                parsed = urlsplit(url)
                host = parsed.hostname
                try:
                    ip_address(host or "")
                    is_ip = True
                except ValueError:
                    is_ip = False
                labels = (host or "").split(".")
                public_dns_name = (
                    len(labels) >= 2 and all(
                        label and len(label) <= 63
                        and label[0].isascii() and label[-1].isascii()
                        and label[0].isalnum() and label[-1].isalnum()
                        and all(c.isascii() and (c.isalnum() or c == "-") for c in label)
                        for label in labels
                    )
                )
                valid = bool(
                    parsed.scheme == "https" and public_dns_name and not is_ip
                    and not parsed.username and not parsed.password
                    and parsed.port in (None, 443)
                    and not parsed.fragment
                    and not any(ord(c) < 33 or ord(c) == 127 for c in url)
                )
            except ValueError:
                valid = False
            if not valid:
                raise ValueError("public sources require a safe HTTPS URL")
        entries.append({"name": name, "kind": kind, "lkr_per_unit": str(amount),
                        "observed_on": observed, "source_url": url,
                        "age_days": (today - day).days,
                        "requires_manual_verification": True})
    return {"as_of": as_of, "entries": entries, "verified_provider_prices": 0,
            "warning": "Metadata checked only; no source, unit, currency, tax, or price independently verified."}
