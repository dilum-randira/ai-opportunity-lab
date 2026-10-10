"""Read local JSON input, print review-only JSON drafts to stdout."""

import argparse
import json
from pathlib import Path
from .core import draft_orders

MAX_INPUT_BYTES = 1024 * 1024


def _load(path: str):
    file = Path(path)
    if file.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"input too large: {file.name}")
    return json.loads(file.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline, human-approval-only order drafting")
    parser.add_argument("--catalog", required=True, help="JSON map of SKU to LKR price string")
    parser.add_argument("--messages", required=True, help="JSON array of {id,text} records")
    args = parser.parse_args()
    try:
        drafts = draft_orders(_load(args.messages), _load(args.catalog))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")
    print(json.dumps({"mode": "DRAFT_ONLY_NO_EXTERNAL_ACTIONS", "orders": drafts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
