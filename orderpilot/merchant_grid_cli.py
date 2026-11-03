"""Bounded, offline JSON CLI for OrderPilot workload/price comparisons.

Run: python -m orderpilot.merchant_grid_cli scenario.json
Input is local and never transmitted. Output contains only aggregate counts.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from .merchant_grid import compare

MAX_INPUT_BYTES = 65_536
REQUIRED = frozenset({
    "workloads", "subscription_prices_lkr", "seconds_saved_per_order", "hourly_lkr",
})
OPTIONAL = frozenset({
    "service_rate_lkr", "utility_rate_lkr", "marketing_rate_lkr",
    "authentication_rate_lkr", "free_service_messages_per_number",
    "hosting_support_lkr", "setup_lkr", "setup_amortization_months",
})


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite JSON number")


def parse_scenario(data: bytes) -> dict:
    """Parse a small, strict aggregate-only scenario; reject extra keys."""
    if type(data) is not bytes or not 0 < len(data) <= MAX_INPUT_BYTES:
        raise ValueError("scenario must be nonempty and at most 64 KiB")
    try:
        scenario = json.loads(
            data.decode("utf-8"), object_pairs_hook=_unique_pairs,
            parse_float=Decimal, parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 JSON scenario") from exc
    if type(scenario) is not dict:
        raise ValueError("scenario must be a JSON object")
    keys = set(scenario)
    if not REQUIRED <= keys or keys - (REQUIRED | OPTIONAL):
        raise ValueError("missing or unsupported scenario fields")
    return scenario


def run(data: bytes) -> dict:
    return compare(**parse_scenario(data))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline aggregate OrderPilot scenario grid")
    parser.add_argument("scenario", type=Path, help="Local JSON file; never uploaded")
    args = parser.parse_args(argv)
    try:
        # Read at most limit+1 to avoid unbounded memory use.
        with args.scenario.open("rb") as source:
            data = source.read(MAX_INPUT_BYTES + 1)
        result = run(data)
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        # Never echo input values, paths or customer details on validation errors.
        print(f"Invalid scenario: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
