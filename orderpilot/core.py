"""Deterministic social-commerce order draft parser; never executes actions.

Input is a list of synthetic or consented messages, not a live WhatsApp feed.
Every result is a *draft* that requires a human before fulfillment.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

SKU = r"[A-Za-z][A-Za-z0-9_-]{0,31}"
QTY_FIRST = re.compile(rf"(?P<qty>\d+)\s*[xX×]\s*(?P<sku>{SKU})", re.ASCII)
SKU_FIRST = re.compile(rf"(?P<sku>{SKU})\s*[xX×]\s*(?P<qty>\d+)", re.ASCII)
MAX_MESSAGES = 100
MAX_MESSAGE_CHARS = 2000
MAX_LINES = 30
MAX_QUANTITY = 1000
MAX_TOTAL = Decimal("100000000.00")


def _money(value: Any) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("catalog prices must be decimal strings")
    try:
        price = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid catalog price") from exc
    if not price.is_finite() or price < 0 or price > MAX_TOTAL or price.as_tuple().exponent < -2:
        raise ValueError("catalog prices must be finite, nonnegative, and have <=2 decimals")
    return price.quantize(Decimal("0.01"))


def _catalog(raw: Any) -> dict[str, Decimal]:
    if not isinstance(raw, dict) or not raw or len(raw) > 1000:
        raise ValueError("catalog must be a nonempty object of <=1000 SKUs")
    result: dict[str, Decimal] = {}
    for key, price in raw.items():
        if not isinstance(key, str) or not re.fullmatch(SKU, key, re.ASCII):
            raise ValueError("catalog contains an invalid SKU")
        normalized = key.upper()
        if normalized in result:
            raise ValueError("catalog has case-insensitive duplicate SKUs")
        result[normalized] = _money(price)
    return result


def _parse_line(line: str) -> tuple[str, int] | None:
    for pattern in (QTY_FIRST, SKU_FIRST):
        match = pattern.fullmatch(line.strip())
        if match:
            qty = int(match.group("qty"))
            if 1 <= qty <= MAX_QUANTITY:
                return match.group("sku").upper(), qty
    return None


def draft_orders(messages: Any, catalog: Any) -> list[dict[str, Any]]:
    """Return review-only drafts; no network, persistence, sending, or payments.

    Duplicate detection is batch-local only. An external persistent idempotency
    store is required before any real-world integration.
    """
    prices = _catalog(catalog)
    if not isinstance(messages, list) or len(messages) > MAX_MESSAGES:
        raise ValueError("messages must be a list of at most 100 entries")
    seen_ids: set[str] = set()
    drafts: list[dict[str, Any]] = []

    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValueError(f"message at index {index} must be an object")
        source_id, text = message.get("id"), message.get("text")
        if not isinstance(source_id, str) or not (1 <= len(source_id) <= 128):
            raise ValueError(f"message at index {index} has invalid id")
        if not isinstance(text, str) or len(text) > MAX_MESSAGE_CHARS:
            raise ValueError(f"message {source_id!r} has invalid text")
        if source_id in seen_ids:
            drafts.append({"source_id": source_id, "status": "duplicate", "items": [],
                           "currency": "LKR", "total": "0.00", "issues": ["duplicate message id in this batch"]})
            continue
        seen_ids.add(source_id)
        lines = [part.strip() for part in re.split(r"[\n;,]", text) if part.strip()]
        issues: list[str] = []
        quantities: dict[str, int] = {}
        if len(lines) > MAX_LINES:
            issues.append("too many order lines; human review required")
        else:
            for number, line in enumerate(lines, start=1):
                parsed = _parse_line(line)
                if parsed is None:
                    issues.append(f"line {number}: unrecognized or invalid quantity")
                    continue
                sku, qty = parsed
                if sku not in prices:
                    issues.append(f"line {number}: unknown SKU {sku}")
                    continue
                if quantities.get(sku, 0) + qty > MAX_QUANTITY:
                    issues.append(f"line {number}: combined quantity exceeds limit for {sku}")
                    continue
                quantities[sku] = quantities.get(sku, 0) + qty
        if not lines:
            issues.append("empty order message")
        items: list[dict[str, Any]] = []
        total = Decimal("0.00")
        for sku in sorted(quantities):
            quantity = quantities[sku]
            subtotal = prices[sku] * quantity
            total += subtotal
            items.append({"sku": sku, "quantity": quantity, "unit_price": str(prices[sku]),
                          "subtotal": str(subtotal)})
        if total > MAX_TOTAL:
            issues.append("total exceeds allowed draft limit")
        drafts.append({"source_id": source_id,
                       "status": "ready_for_review" if items and not issues else "needs_review",
                       "items": items, "currency": "LKR", "total": str(total), "issues": issues})
    return drafts
