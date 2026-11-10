"""Synthetic tests for merchant-level aggregation; no identifying data."""
import unittest
from decimal import Decimal
from orderpilot.merchant_aggregation import aggregate_merchants
from orderpilot.pilot_gate import screen


class MerchantAggregationTests(unittest.TestCase):
    def test_exact_means_and_any_error_flags(self):
        result = aggregate_merchants([
            [(Decimal("10.1"), "4.1", 0, 0), ("10.3", "4.3", 1, 0)],
            [(8, 7, 0, 1)],
        ])
        self.assertEqual(result, [
            (Decimal("10.2"), Decimal("4.2"), 1, 0),
            (Decimal("8"), Decimal("7"), 0, 1),
        ])

    def test_repeated_orders_count_as_one_merchant(self):
        groups = [[(120, 60, 1, 0)] * 5 for _ in range(5)]
        pairs = aggregate_merchants(groups)
        self.assertEqual(len(pairs), 5)
        result = screen(study_kind="synthetic", pairs=pairs,
                        consenting_merchants=5,
                        merchants_reporting_repeated_pain=2,
                        merchants_discussing_price=1,
                        modeled_net_lkr="100")
        self.assertFalse(result["checks"]["screening_sample_target"])

    def test_reject_bad_group_shapes(self):
        for bad in ([], {}, [()], [[]], [[(1, 2, 0)]],
                    [[(1, 2, 0, 0, 5)]], [[(1, 2, 0, 0)] * 101]):
            with self.subTest(bad=str(bad)[:60]), self.assertRaises(ValueError):
                aggregate_merchants(bad)

    def test_reject_invalid_numbers_and_flags(self):
        for row in ((True, 2, 0, 0), ("NaN", 2, 0, 0),
                    ("Infinity", 2, 0, 0), (-1, 2, 0, 0),
                    (36001, 2, 0, 0), (1, 2, True, 0),
                    (1, 2, 2, 0), (1, 2, 0.5, 0),
                    ("email@example.com", 2, 0, 0)):
            with self.subTest(row=row), self.assertRaises(ValueError):
                aggregate_merchants([[row]])

    def test_limit_merchant_count(self):
        with self.assertRaises(ValueError):
            aggregate_merchants([[(1, 1, 0, 0)]] * 1001)


if __name__ == "__main__":
    unittest.main()
