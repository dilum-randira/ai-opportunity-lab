"""Reproducible, offline summaries of hypothetical OrderPilot grid scenarios.

This is not a pricing recommendation, demand estimate, or break-even solver.
Only explicitly sampled workloads are compared. No network or customer data.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Any

from .merchant_grid_cli import parse_scenario
from .merchant_grid import compare


def summarize_grid(grid: dict[str, Any]) -> dict[str, Any]:
    """Summarize *sampled* workload outcomes without rounding-based decisions."""
    if type(grid) is not dict or grid.get("mode") != "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION":
        raise ValueError("expected a validated hypothetical OrderPilot grid")
    rows = grid.get("rows")
    if type(rows) is not list or not 1 <= len(rows) <= 20:
        raise ValueError("grid must contain 1..20 workload rows")
    if type(grid.get("scenario_count")) is not int or grid["scenario_count"] <= 0:
        raise ValueError("invalid scenario count")
    prices: dict[str, list[tuple[int, bool]]] = {}
    expected_prices = None
    seen_volumes: set[int] = set()
    for row in rows:
        if type(row) is not dict or type(row.get("monthly_orders")) is not int:
            raise ValueError("invalid workload row")
        orders = row["monthly_orders"]
        if not 1 <= orders <= 1_000_000 or orders in seen_volumes:
            raise ValueError("invalid or duplicate monthly order volume")
        seen_volumes.add(orders)
        entries = row.get("prices")
        if type(entries) is not list or not 1 <= len(entries) <= 10:
            raise ValueError("workload must contain 1..10 price entries")
        seen = set()
        for entry in entries:
            if type(entry) is not dict:
                raise ValueError("invalid price entry")
            price = entry.get("subscription_lkr")
            positive = entry.get("positive_after_messaging_under_assumptions")
            if type(price) is not str or type(positive) is not bool:
                raise ValueError("invalid price result")
            try:
                amount = Decimal(price)
            except (InvalidOperation, ValueError) as exc:
                raise ValueError("invalid price result") from exc
            if (not amount.is_finite() or not 0 <= amount <= 100_000_000
                    or price != f"{amount:.2f}" or amount.as_tuple().exponent != -2):
                raise ValueError("price must be a canonical nonnegative LKR amount")
            if price in seen:
                raise ValueError("invalid or duplicate price result")
            seen.add(price)
            prices.setdefault(price, []).append((orders, positive))
        if expected_prices is None:
            expected_prices = seen
        elif seen != expected_prices:
            raise ValueError("inconsistent price grid")
    if len(rows) * len(expected_prices) > 100:
        raise ValueError("grid exceeds 100 scenario cells")
    if grid["scenario_count"] != len(rows) * len(expected_prices):
        raise ValueError("scenario count does not match grid")
    summary = []
    for price, values in sorted(prices.items(), key=lambda item: item[0]):
        sorted_values = sorted(values)
        positive_orders = [orders for orders, flag in sorted_values if flag]
        summary.append({
            "subscription_lkr": price,
            "positive_sampled_workloads": len(positive_orders),
            "sampled_workloads": len(sorted_values),
            "lowest_sampled_positive_volume": min(positive_orders) if positive_orders else None,
            "highest_sampled_negative_volume": max(
                (orders for orders, flag in sorted_values if not flag), default=None),
            "all_sampled_workloads_positive": len(positive_orders) == len(sorted_values),
        })
    return {
        "mode": "OFFLINE_SAMPLED_GRID_SUMMARY_NOT_PRICE_ADVICE",
        "scenario_count": grid.get("scenario_count"),
        "price_summaries": summary,
        "limitations": [
            "Only explicitly sampled order volumes were checked; no break-even threshold is inferred.",
            "Results are hypothetical and do not establish willingness to pay, market size, or causality.",
            "Positive flags come from exact arithmetic in the grid, not rounded display amounts.",
            "Unmodeled costs and adverse outcomes can reverse modeled profitability.",
        ],
    }


def report(data: bytes) -> dict[str, Any]:
    """Run a bounded JSON scenario and return a deterministic aggregate report.

    The digest identifies the exact original input bytes for local reproducibility.
    Never publish a digest of private or identifying data; the strict input schema
    is designed for hypothetical numeric aggregates only.
    """
    scenario = parse_scenario(data)
    grid = compare(**scenario)
    return {
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "summary": summarize_grid(grid),
        "grid": grid,
    }


def canonical_json(result: dict[str, Any]) -> str:
    """Stable machine-readable output for offline comparison and review."""
    return json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
