"""Audited, review-only correction of parsed order drafts (offline SQLite).

No raw messages, outbound requests, inventory updates, or payments.
The existing source message fingerprint is deliberately never changed.
"""
from __future__ import annotations

import json
import re
from typing import Any

from .core import SKU, draft_orders
from .queue import OrderQueue

MAX_ITEMS = 30
MAX_NOTE = 240


def _replacement(source_id: str, items: Any, catalog: Any) -> dict[str, Any]:
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise ValueError("replacement must have 1..30 items")
    lines = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {"sku", "quantity"}:
            raise ValueError("each item needs exactly sku and quantity")
        sku, qty = item["sku"], item["quantity"]
        if not isinstance(sku, str) or not re.fullmatch(SKU, sku, re.ASCII):
            raise ValueError("invalid SKU")
        if type(qty) is not int or not 1 <= qty <= 1000:
            raise ValueError("quantity must be a whole number from 1 to 1000")
        lines.append(f"{qty} x {sku}")
    draft = draft_orders([{"id": source_id, "text": "; ".join(lines)}], catalog)[0]
    if draft["status"] != "ready_for_review":
        raise ValueError("replacement failed catalog, quantity or total validation")
    return draft


def _ensure_schema(q: OrderQueue) -> None:
    q.connection.execute("""
        CREATE TABLE IF NOT EXISTS correction_events (
            source_id TEXT NOT NULL REFERENCES order_drafts(source_id),
            version INTEGER NOT NULL CHECK(version > 0),
            previous_draft_json TEXT NOT NULL,
            corrected_draft_json TEXT NOT NULL,
            note TEXT NOT NULL,
            corrected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(source_id, version)
        )
    """)


def replace_items(q: OrderQueue, source_id: str, items: Any, catalog: Any,
                  *, expected_version: int, note: str) -> dict[str, Any]:
    """Replace all items on a pending draft, preserving each prior version.

    Optimistic version check prevents accidental overwrites. This function
    never approves an order: the reviewer must call OrderQueue.review later.
    """
    if not isinstance(source_id, str) or not 1 <= len(source_id) <= 128:
        raise ValueError("invalid source id")
    if type(expected_version) is not int or not 0 <= expected_version <= 1_000_000:
        raise ValueError("expected_version must be a nonnegative integer")
    if not isinstance(note, str) or not 1 <= len(note.strip()) <= MAX_NOTE:
        raise ValueError("a short correction reason is required")
    corrected = _replacement(source_id, items, catalog)
    conn = q.connection
    conn.execute("BEGIN IMMEDIATE")
    try:
        _ensure_schema(q)
        existing = conn.execute(
            "SELECT draft_json, review_state FROM order_drafts WHERE source_id = ?",
            (source_id,)).fetchone()
        if existing is None:
            raise ValueError("unknown source id")
        if existing["review_state"] != "pending":
            raise ValueError("only pending drafts can be corrected")
        version = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM correction_events WHERE source_id = ?",
            (source_id,)).fetchone()[0]
        if version != expected_version:
            raise ValueError(f"stale version: current version is {version}")
        before = existing["draft_json"]
        after = json.dumps(corrected, ensure_ascii=False, sort_keys=True)
        if json.loads(before)["items"] == corrected["items"] and json.loads(before)["issues"] == []:
            raise ValueError("no actual item correction")
        conn.execute(
            "UPDATE order_drafts SET draft_json = ?, parse_status = 'ready_for_review' "
            "WHERE source_id = ? AND review_state = 'pending'", (after, source_id))
        conn.execute(
            "INSERT INTO correction_events(source_id, version, previous_draft_json, "
            "corrected_draft_json, note) VALUES (?, ?, ?, ?, ?)",
            (source_id, version + 1, before, after, note.strip()))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {"source_id": source_id, "version": version + 1,
            "review_state": "pending", "draft": corrected,
            "action": "corrected_not_approved"}


def history(q: OrderQueue, source_id: str) -> list[dict[str, Any]]:
    if not isinstance(source_id, str) or not 1 <= len(source_id) <= 128:
        raise ValueError("invalid source id")
    _ensure_schema(q)
    rows = q.connection.execute(
        "SELECT version, previous_draft_json, corrected_draft_json, note, corrected_at "
        "FROM correction_events WHERE source_id = ? ORDER BY version", (source_id,)).fetchall()
    return [{"version": row["version"], "before": json.loads(row["previous_draft_json"]),
             "after": json.loads(row["corrected_draft_json"]), "note": row["note"],
             "corrected_at": row["corrected_at"]} for row in rows]
