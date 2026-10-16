"""Tests for paired local time measurements and cost interpretation."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from orderpilot.paired_study import read_pairs, summarize, report


class PairedStudyTests(unittest.TestCase):
    def test_mean_median_and_errors(self):
        items = [(Decimal(120), Decimal(60), 1, 0),
                 (Decimal(100), Decimal(80), 0, 1),
                 (Decimal(90), Decimal(80), 0, 0)]
        stats = summarize(items)
        self.assertEqual(stats['mean_seconds_saved'], '30.00')
        self.assertEqual(stats['median_seconds_saved'], '20.00')
        self.assertEqual(stats['errors_before'], 1)
        self.assertEqual(stats['errors_after'], 1)
        self.assertEqual(stats['orders_slower_with_assistance'], 0)
        self.assertEqual(len(stats['bootstrap_95pct_interval_seconds']), 2)

    def test_negative_average_is_not_reported_as_positive_labor_value(self):
        items = [(Decimal(15), Decimal(60), 0, 0)]
        result = report(items, monthly_orders=100, hourly_lkr='400', subscription_lkr='100')
        self.assertTrue(result['assistance_slowed_average'])
        self.assertEqual(result['cost_scenario']['gross_labor_value_lkr'], '0.00')
        self.assertEqual(result['cost_scenario']['net_monthly_value_lkr'], '-100.00')

    def test_reject_identifier_and_duplicate_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'study.csv'
            for content in (
                'name,baseline_seconds,assisted_seconds,baseline_errors,assisted_errors\n',
                'baseline_seconds,assisted_seconds,baseline_errors,baseline_errors\n',
                'baseline_seconds,assisted_seconds,baseline_errors,assisted_errors\n',
                'baseline_seconds,assisted_seconds,baseline_errors,assisted_errors\n1,2,0,0,extra\n',
            ):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(ValueError):
                    read_pairs(str(path))

    def test_valid_csv_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'study.csv'
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(('baseline_seconds', 'assisted_seconds', 'baseline_errors', 'assisted_errors'))
                writer.writerow((120, 60, 1, 0))
            root = Path(__file__).resolve().parents[1]
            result = subprocess.run([sys.executable, '-m', 'orderpilot.paired_study', '--study', str(path),
                                     '--monthly-orders', '60', '--hourly-lkr', '600', '--subscription-lkr', '500'],
                                    cwd=root, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data['cost_scenario']['net_monthly_value_lkr'], '100.00')
            self.assertIsNone(data['timings']['bootstrap_95pct_interval_seconds'])

    def test_csv_reject_invalid_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'study.csv'
            for sample in ('NaN,10,0,0', '10,-1,0,0', '10,5,0.5,0'):
                path.write_text('baseline_seconds,assisted_seconds,baseline_errors,assisted_errors\n'
                                + sample + '\n', encoding='utf-8')
                with self.assertRaises(ValueError):
                    read_pairs(str(path))

if __name__ == '__main__':
    unittest.main()
