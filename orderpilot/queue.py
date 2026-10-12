"""Local offline order-review queue with durable message idempotency.

Only parsed drafts and SHA-256 message fingerprints are persisted. There are
no outbound integrations, payments, inventory updates, or order fulfillment.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from .core import draft_orders

MAX_NOTE_LENGTH = 240
MAX_LIST_LIMIT = 200


class OrderQueue:
    """Single-device SQLite review queue; not a multi-user production service."""

    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        if self.path.is_symlink():
            raise ValueError("database path cannot be a symlink")
        if not self.path.parent.is_dir():
            raise ValueError("database parent directory must already exist")
        if not self.path.exists():
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                if self.path.is_symlink():
                    raise ValueError("database path cannot be a symlink") from None
            else:
                os.close(fd)
        self.connection = sqlite3.connect(str(self.path), timeout=5.0)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS order_drafts (
                source_id TEXT PRIMARY KEY,
                message_digest TEXT NOT NULL,
                draft_json TEXT NOT NULL,
                parse_status TEXT NOT NULL CHECK(parse_status IN ('ready_for_review', 'needs_review')),
                review_state TEXT NOT NULL DEFAULT 'pending'
                    CHECK(review_state IN ('pending', 'approved', 'rejected')),
                reviewer_note TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL REFERENCES order_drafts(source_id),
                action TEXT NOT NULL CHECK(action IN ('ingested', 'approved', 'rejected')),
                note TEXT,
                at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

    def __enter__(self) -> "OrderQueue":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    def ingest(self, messages: Any, catalog: Any) -> list[dict[str, Any]]:
        """Atomically ingest a batch; duplicate IDs never overwrite earlier data.

        Reusing an ID with the same message yields 'duplicate'; reusing it with
        different text yields 'id_conflict'. Neither is inserted or approved.
        """
        drafts = draft_orders(messages, catalog)
        results: list[dict[str, Any]] = []
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            for message, draft in zip(messages, drafts):
                source_id = message["id"]
                digest = hashlib.sha256(message["text"].encode("utf-8")).hexdigest()
                existing = self.connection.execute(
                    "SELECT message_digest FROM order_drafts WHERE source_id = ?", (source_id,)
                ).fetchone()
                if existing is not None:
                    results.append({"source_id": source_id, "result":
                                    "duplicate" if existing["message_digest"] == digest else "id_conflict"})
                    continue
                if draft["status"] == "duplicate":
                    raise ValueError("unexpected batch duplicate before first insert")
                self.connection.execute(
                    "INSERT INTO order_drafts(source_id, message_digest, draft_json, parse_status) "
                    "VALUES (?, ?, ?, ?)",
                    (source_id, digest, json.dumps(draft, ensure_ascii=False), draft["status"]),
                )
                self.connection.execute(
                    "INSERT INTO audit_events(source_id, action) VALUES (?, 'ingested')", (source_id,)
                )
                results.append({"source_id": source_id, "result": "created", "parse_status": draft["status"]})
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return results

    def list_orders(self, state: str = "pending", limit: int = 50) -> list[dict[str, Any]]:
        if state not in {"pending", "approved", "rejected", "all"}:
            raise ValueError("invalid state filter")
        if type(limit) is not int or not 1 <= limit <= MAX_LIST_LIMIT:
            raise ValueError("limit must be an integer from 1 to 200")
        if state == "all":
            rows = self.connection.execute(
                "SELECT * FROM order_drafts ORDER BY created_at, rowid LIMIT ?", (limit,)
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT * FROM order_drafts WHERE review_state = ? "
                "ORDER BY created_at, rowid LIMIT ?", (state, limit)
            ).fetchall()
        return [self._to_public(row) for row in rows]

    @staticmethod
    def _to_public(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "source_id": row["source_id"],
            "parse_status": row["parse_status"],
            "review_state": row["review_state"],
            "draft": json.loads(row["draft_json"]),
            "reviewer_note": row["reviewer_note"],
            "created_at": row["created_at"],
            "reviewed_at": row["reviewed_at"],
        }

    def review(self, source_id: str, decision: str, note: str = "") -> dict[str, Any]:
        """Record an explicit local decision; does NOT send or fulfill anything."""
        if not isinstance(source_id, str) or not 1 <= len(source_id) <= 128:
            raise ValueError("invalid source id")
        if decision not in {"approve", "reject"}:
            raise ValueError("decision must be approve or reject")
        if not isinstance(note, str) or len(note) > MAX_NOTE_LENGTH:
            raise ValueError("note must be text up to 240 characters")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT * FROM order_drafts WHERE source_id = ?", (source_id,)
            ).fetchone()
            if row is None:
                raise ValueError("unknown source id")
            if row["review_state"] != "pending":
                raise ValueError("order has already been reviewed")
            if decision == "approve" and row["parse_status"] != "ready_for_review":
                raise ValueError("cannot approve draft with parsing issues")
            state = "approved" if decision == "approve" else "rejected"
            self.connection.execute(
                "UPDATE order_drafts SET review_state = ?, reviewer_note = ?, "
                "reviewed_at = CURRENT_TIMESTAMP WHERE source_id = ?",
                (state, note, source_id),
            )
            self.connection.execute(
                "INSERT INTO audit_events(source_id, action, note) VALUES (?, ?, ?)",
                (source_id, state, note),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        row = self.connection.execute(
            "SELECT * FROM order_drafts WHERE source_id = ?", (source_id,)
        ).fetchone()
        return self._to_public(row)

    def audit(self, source_id: str) -> list[dict[str, Any]]:
        """Read the local action history for one source ID."""
        rows = self.connection.execute(
            "SELECT action, note, at FROM audit_events WHERE source_id = ? ORDER BY id", (source_id,)
        ).fetchall()
        return [dict(row) for row in rows]
