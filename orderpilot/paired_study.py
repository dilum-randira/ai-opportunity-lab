"""Privacy-minimal paired order-entry timing study; no customer records or network."""
from __future__ import annotations
import argparse
import csv
import json
import random
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from statistics import median
from .roi_simple import estimate_roi

FIELDS = ('baseline_seconds', 'assisted_seconds', 'baseline_errors', 'assisted_errors')
MAX_BYTES = 256_000
MAX_ROWS = 5_000


def _number(raw: str, label: str, upper: int) -> Decimal:
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f'{label}: invalid number') from exc
    if not value.is_finite() or value < 0 or value > upper:
        raise ValueError(f'{label}: out of bounds')
    return value


def read_pairs(filename: str) -> list[tuple[Decimal, Decimal, int, int]]:
    path = Path(filename)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('CSV exceeds 256 KB')
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, restkey='_extra')
        if reader.fieldnames is None or tuple(reader.fieldnames) != FIELDS:
            raise ValueError('CSV needs exactly four numeric columns, without identifiers')
        results = []
        for line, row in enumerate(reader, 2):
            if len(results) == MAX_ROWS or '_extra' in row or any(row.get(k) is None for k in FIELDS):
                raise ValueError(f'CSV row {line}: malformed or too many rows')
            before = _number(row['baseline_seconds'], f'row {line} baseline_seconds', 36000)
            after = _number(row['assisted_seconds'], f'row {line} assisted_seconds', 36000)
            original = _number(row['baseline_errors'], f'row {line} baseline_errors', 100)
            helped = _number(row['assisted_errors'], f'row {line} assisted_errors', 100)
            if original != int(original) or helped != int(helped):
                raise ValueError(f'row {line}: error counts must be integers')
            results.append((before, after, int(original), int(helped)))
    if not results:
        raise ValueError('CSV needs at least one paired observation')
    return results


def summarize(pairs: list[tuple[Decimal, Decimal, int, int]]) -> dict:
    if not pairs or len(pairs) > MAX_ROWS:
        raise ValueError('paired observations required')
    diffs = [before - after for before, after, _, _ in pairs]
    mean = sum(diffs, Decimal(0)) / len(diffs)
    mid = median(diffs)
    interval = None
    if len(diffs) >= 2:
        rng = random.Random(20261016)
        means = sorted(sum((diffs[rng.randrange(len(diffs))] for _ in diffs), Decimal(0))
                       / len(diffs) for _ in range(500))
        interval = [str(means[12].quantize(Decimal('.01'), rounding=ROUND_HALF_UP)),
                    str(means[487].quantize(Decimal('.01'), rounding=ROUND_HALF_UP))]
    fmt = lambda v: str(v.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
    return {'sample_size': len(pairs), 'mean_seconds_saved': fmt(mean),
            'median_seconds_saved': fmt(mid), 'bootstrap_95pct_interval_seconds': interval,
            'orders_slower_with_assistance': sum(d < 0 for d in diffs),
            'errors_before': sum(x[2] for x in pairs),
            'errors_after': sum(x[3] for x in pairs)}


def report(pairs, *, monthly_orders: int, hourly_lkr: str,
           subscription_lkr: str, operating_lkr: str = '0') -> dict:
    stats = summarize(pairs)
    # When observed average time savings are negative, avoid a false claim of benefit.
    raw_saved = Decimal(stats['mean_seconds_saved'])
    roi = estimate_roi(orders_per_month=monthly_orders,
                       seconds_saved_per_order=max(raw_saved, Decimal(0)),
                       hourly_lkr=hourly_lkr, monthly_subscription_lkr=subscription_lkr,
                       monthly_operating_lkr=operating_lkr)
    return {'mode': 'SYNTHETIC_OR_CONSENTED_AGGREGATES_ONLY', 'timings': stats,
            'cost_scenario': roi, 'assistance_slowed_average': raw_saved < 0,
            'cautions': ['Nonrandom paired timing does not establish causality or buyer demand.',
                         'Bootstrap interval describes the sample, not population certainty.',
                         'Negative time savings are floored at zero in the cost scenario; do not interpret as gains.',
                         'Never commit real customer records, IDs, phone numbers, or addresses.']}


def main() -> int:
    p = argparse.ArgumentParser(description='Offline paired merchant ROI pilot')
    p.add_argument('--study', required=True)
    p.add_argument('--monthly-orders', type=int, required=True)
    p.add_argument('--hourly-lkr', required=True)
    p.add_argument('--subscription-lkr', required=True)
    p.add_argument('--operating-lkr', default='0')
    args = p.parse_args()
    try:
        outcome = report(read_pairs(args.study), monthly_orders=args.monthly_orders,
                         hourly_lkr=args.hourly_lkr, subscription_lkr=args.subscription_lkr,
                         operating_lkr=args.operating_lkr)
    except (ValueError, OSError) as exc:
        p.exit(2, f'Invalid pilot study: {exc}\n')
    print(json.dumps(outcome, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
