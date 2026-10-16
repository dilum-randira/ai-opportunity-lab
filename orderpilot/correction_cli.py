"""Local correction CLI. JSON-only input, never sends messages or fulfills orders."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .corrections import history, replace_items
from .queue import OrderQueue

MAX_FILE_BYTES = 1024 * 1024


def _read(path: str) -> object:
    file = Path(path)
    if file.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("input file exceeds 1 MiB")
    return json.loads(file.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline, audited order corrections")
    parser.add_argument("--db", required=True, help="existing private SQLite queue")
    commands = parser.add_subparsers(dest="command", required=True)
    edit = commands.add_parser("correct", help="replace all items on a pending draft")
    edit.add_argument("--id", required=True)
    edit.add_argument("--items", required=True, help="JSON array of sku/quantity objects")
    edit.add_argument("--catalog", required=True, help="existing catalog JSON")
    edit.add_argument("--expected-version", type=int, required=True)
    edit.add_argument("--note", required=True, help="non-identifying correction reason")
    audit = commands.add_parser("history", help="view full correction history")
    audit.add_argument("--id", required=True)
    args = parser.parse_args()
    try:
        with OrderQueue(args.db) as queue:
            if args.command == "correct":
                result = replace_items(queue, args.id, _read(args.items), _read(args.catalog),
                                       expected_version=args.expected_version, note=args.note)
            else:
                result = history(queue, args.id)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Invalid correction: {exc}\n")
    print(json.dumps({"mode": "OFFLINE_CORRECTION_ONLY", "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
