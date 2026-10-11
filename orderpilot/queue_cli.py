"""Local review queue CLI: no messaging, payments, or fulfillment actions."""

import argparse
import json
from .cli import _load
from .queue import OrderQueue


def main() -> int:
    parser = argparse.ArgumentParser(description="OrderPilot local review queue (offline only)")
    parser.add_argument("--db", required=True, help="local SQLite database path; keep private")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="parse and persist local review drafts")
    ingest.add_argument("--catalog", required=True)
    ingest.add_argument("--messages", required=True)
    listing = commands.add_parser("list", help="list stored review drafts")
    listing.add_argument("--state", choices=["pending", "approved", "rejected", "all"], default="pending")
    listing.add_argument("--limit", type=int, default=50)
    review = commands.add_parser("review", help="record local human decision, no external action")
    review.add_argument("--id", required=True)
    review.add_argument("--decision", choices=["approve", "reject"], required=True)
    review.add_argument("--note", default="")
    audit = commands.add_parser("audit", help="view local review history")
    audit.add_argument("--id", required=True)
    args = parser.parse_args()
    try:
        with OrderQueue(args.db) as queue:
            if args.command == "ingest":
                result = queue.ingest(_load(args.messages), _load(args.catalog))
            elif args.command == "list":
                result = queue.list_orders(args.state, args.limit)
            elif args.command == "review":
                result = queue.review(args.id, args.decision, args.note)
            else:
                result = queue.audit(args.id)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"OrderPilot error: {exc}\n")
    print(json.dumps({"mode": "LOCAL_ONLY_NO_EXTERNAL_ACTIONS", "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
