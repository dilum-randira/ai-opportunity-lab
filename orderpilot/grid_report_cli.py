"""Offline reproducible OrderPilot scenario report CLI.

Usage: python -m orderpilot.grid_report_cli examples/orderpilot-grid-synthetic.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .grid_report import canonical_json, report
from .merchant_grid_cli import MAX_INPUT_BYTES


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline aggregate merchant scenario report")
    parser.add_argument("scenario", type=Path, help="Local hypothetical numeric JSON file")
    args = parser.parse_args(argv)
    try:
        with args.scenario.open("rb") as source:
            raw = source.read(MAX_INPUT_BYTES + 1)
        output = report(raw)
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        # Do not expose paths, values or source content in errors.
        print(f"Invalid scenario: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(canonical_json(output), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
