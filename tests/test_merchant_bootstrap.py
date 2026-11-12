"""Synthetic tests for merchant-level resampling; no real merchant records."""
import unittest
from decimal import Decimal

from orderpilot.merchant_bootstrap import merchant_bootstrap
from orderpilot.merchant_aggregation import aggregate_merchants


class MerchantBootstrapTests(unittest.TestCase):
    def test_constant_savings_have_zero_width_interval(self):
        result = merchant_bootstrap([(20, 10, 0, 0)] * 4, replicates=100, seed=7)
        self.assertEqual(result["mean_saving_seconds"], "10")
        self.assertEqual(result["bootstrap_p025_seconds"], "10")
        self.assertEqual(result["bootstrap_p975_seconds"], "10")
        self.assertEqual(result["bootstrap_fraction_positive"], "1")

    def test_reproducible_and_bounded_by_observed_savings(self):
        rows = [(10, 5, 0, 0), (10, 12, 1, 0), (20, 10, 0, 1)]
        first = merchant_bootstrap(rows, replicates=200, seed=42)
        self.assertEqual(first, merchant_bootstrap(rows, replicates=200, seed=42))
        self.assertEqual(first["merchant_count"], 3)
        self.assertLessEqual(Decimal("-2"), Decimal(first["bootstrap_p025_seconds"]))
        self.assertLessEqual(Decimal(first["bootstrap_p025_seconds"]), Decimal(first["bootstrap_p975_seconds"]))
        self.assertLessEqual(Decimal(first["bootstrap_p975_seconds"]), Decimal("10"))
        self.assertLessEqual(Decimal("0"), Decimal(first["bootstrap_fraction_positive"]))
        self.assertLessEqual(Decimal(first["bootstrap_fraction_positive"]), Decimal("1"))

    def test_negative_savings_not_silently_zeroed(self):
        result = merchant_bootstrap([(1, 4, 0, 0)] * 2, replicates=100)
        self.assertEqual(result["bootstrap_p975_seconds"], "-3")
        self.assertEqual(result["bootstrap_fraction_positive"], "0")

    def test_aggregate_first_not_each_order(self):
        pairs = aggregate_merchants([[(20, 10, 0, 0), (30, 20, 0, 0)], [(10, 8, 0, 0)]])
        result = merchant_bootstrap(pairs, replicates=100)
        self.assertEqual(result["merchant_count"], 2)
        self.assertEqual(result["mean_saving_seconds"], "6")

    def test_reject_invalid_inputs(self):
        valid = [(10, 5, 0, 0)] * 2
        for rows in (None, [], valid[:1], valid * 501, [(1, 2, 0)] * 2,
                     [("NaN", 1, 0, 0)] * 2, [(True, 1, 0, 0)] * 2,
                     [(1, 2, True, 0)] * 2, [(1, 2, 0, 3)] * 2,
                     [("customer@example.com", 2, 0, 0)] * 2):
            with self.subTest(rows=str(rows)[:30]), self.assertRaises(ValueError):
                merchant_bootstrap(rows, replicates=100)
        for count in (0, 99, 5001, True, 1.2):
            with self.subTest(count=count), self.assertRaises(ValueError):
                merchant_bootstrap(valid, replicates=count)
        for seed in (-1, 2**32, True, 1.2):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                merchant_bootstrap(valid, replicates=100, seed=seed)


if __name__ == "__main__":
    unittest.main()
